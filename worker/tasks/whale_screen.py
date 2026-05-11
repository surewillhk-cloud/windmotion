"""Whale Screen Task - Periodic whale discovery and scoring.

Scans blockchain for new whale wallets, scores them against
user-defined filters, and triggers auto-analysis when matched.
"""
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute whale screening."""
    publish = context["publish_progress"]
    pg = context["pg"]
    redis = context["redis"]

    chain = payload.get("chain", "bsc")
    filters = payload.get("filters", {})
    scan_mode = payload.get("mode", "full")  # full | incremental

    # ── Step 1: Discover candidates via ChainScanner ─────────
    publish(10, f"Scanning {chain} for whale candidates...")
    from backend.services.chain_scanner import ChainScanner
    from backend.skills.data_fetch import DataFetch

    scanner = ChainScanner()
    data_fetch = DataFetch()

    # Scan large transactions on DEX routers
    min_value_usd = filters.get("min_portfolio_usd", 100000)
    # Convert USD to BNB (rough estimate ~$600/BNB)
    min_value_bnb = max(min_value_usd / 600, 10)

    large_txs = await scanner.scan_large_transactions(min_value_bnb=min_value_bnb, chain=chain)
    publish(20, f"Found {len(large_txs)} large transactions on DEX routers")

    # Extract unique addresses from large transactions
    candidate_addresses = set()
    for tx in large_txs:
        from_addr = tx.get("from", "")
        to_addr = tx.get("to", "")
        if from_addr:
            candidate_addresses.add(from_addr.lower())
        if to_addr:
            candidate_addresses.add(to_addr.lower())

    # Also run WhaleScreen skill on the transaction data
    from backend.skills.whale_screen import WhaleScreen
    whale_screen = WhaleScreen()

    # Build transaction list for whale screen
    screen_txs = []
    for tx in large_txs:
        screen_txs.append({
            "from": tx.get("from", ""),
            "to": tx.get("to", ""),
            "value_usd": tx.get("value_bnb", 0) * 600,  # rough BNB->USD
            "chain": chain,
            "token": "BNB",
        })

    if screen_txs:
        screen_result = await whale_screen.execute({
            "transactions": screen_txs,
            "filters": {
                "min_value_usd": min_value_usd,
                "chain": chain,
            },
        })
        if screen_result.success:
            for whale in screen_result.data.get("whales", []):
                candidate_addresses.add(whale["address"].lower())

    publish(30, f"Found {len(candidate_addresses)} unique candidate addresses")

    # ── Step 2: Score each candidate ─────────────────────────
    from backend.services.whale_discovery import WhaleDiscoveryService
    whale_discovery = WhaleDiscoveryService()

    scored_whales: List[Dict] = []
    candidates = list(candidate_addresses)

    for i, address in enumerate(candidates):
        # Fetch detailed history via DataFetch
        history_result = await data_fetch.execute({
            "data_type": "transactions",
            "params": {"address": address, "chain": chain, "limit": 100},
        })
        transactions = history_result.data.get("data", {}).get("transactions", []) if history_result.success else []

        # Fetch token transfers
        transfers_result = await data_fetch.execute({
            "data_type": "token_transfers",
            "params": {"address": address, "chain": chain, "limit": 100},
        })
        transfers = transfers_result.data.get("data", {}).get("transfers", []) if transfers_result.success else []

        # Fetch balance
        balance_result = await data_fetch.execute({
            "data_type": "balance",
            "params": {"address": address},
        })
        balance = balance_result.data.get("data", {}).get("balance_bnb", 0) if balance_result.success else 0

        # Calculate score
        score_result = await whale_discovery.score_whale(
            address=address,
            history={"transactions": transactions, "transfers": transfers, "balance_bnb": balance},
            filters=filters,
        )

        labels = _derive_labels(transactions, transfers, balance)

        scored_whales.append({
            "address": address,
            "chain": chain,
            "score": score_result.get("score", 0),
            "profit_usd": score_result.get("profit_usd", 0),
            "win_rate": score_result.get("win_rate", 0),
            "roi": score_result.get("roi", 0),
            "trade_count": len(transactions),
            "transfer_count": len(transfers),
            "balance_bnb": balance,
            "labels": labels,
        })

        pct = 30 + int((i + 1) / max(len(candidates), 1) * 40)
        publish(pct, f"Scored {i + 1}/{len(candidates)} whales")

    # ── Step 3: Apply filters ────────────────────────────────
    publish(75, "Applying filter criteria...")
    qualified = _apply_filters(scored_whales, filters)

    # ── Step 4: Store results ────────────────────────────────
    publish(85, "Storing whale data...")
    for whale in scored_whales:
        await redis.cache_whale_data(whale["address"], whale, ttl=3600)

    try:
        for whale in qualified:
            await pg.execute(
                "INSERT INTO whales (address, chain, score, profit_usd, win_rate, roi, trade_count, labels, updated_at) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW()) "
                "ON CONFLICT (address) DO UPDATE SET "
                "score = $3, profit_usd = $4, win_rate = $5, roi = $6, trade_count = $7, labels = $8, updated_at = NOW()",
                whale["address"], whale["chain"], whale["score"],
                whale["profit_usd"], whale["win_rate"], whale["roi"],
                whale["trade_count"], json.dumps(whale["labels"]),
            )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")

    # ── Step 5: Trigger auto-analysis if enabled ─────────────
    auto_analyze = payload.get("auto_analyze", False)
    triggered = []
    if auto_analyze and qualified:
        publish(92, f"Triggering auto-analysis for {len(qualified)} whales...")
        for whale in qualified[:5]:
            task_payload = {
                "task_type": "forward_analysis",
                "task_id": f"auto-{whale['address'][:8]}",
                "payload": {
                    "address": whale["address"],
                    "chain": whale["chain"],
                    "source": "auto_whale_screen",
                },
            }
            await redis.client.rpush("wm:task_queue", json.dumps(task_payload))
            triggered.append(whale["address"])

    publish(100, f"Done. {len(qualified)} whales qualified.")

    return {
        "chain": chain,
        "candidates_found": len(candidates),
        "scored": len(scored_whales),
        "qualified": len(qualified),
        "auto_triggered": len(triggered),
        "top_whales": qualified[:10],
        "triggered_analyses": triggered,
    }


def _derive_labels(transactions: List[Dict], transfers: List[Dict], balance: float) -> List[str]:
    """Derive behavioral labels from transaction data."""
    labels = []

    if balance > 1000:
        labels.append("high_balance")
    if len(transactions) > 100:
        labels.append("active_trader")
    if len(transfers) > 50:
        labels.append("token_active")

    # Check for DEX activity
    dex_methods = {"swap", "addliquidity", "removeliquidity"}
    has_dex = any(
        tx.get("functionName", "").lower().startswith(m)
        for tx in transactions
        for m in dex_methods
    )
    if has_dex:
        labels.append("dex_user")

    # Check for DeFi activity
    defi_methods = {"deposit", "withdraw", "borrow", "repay", "stake"}
    has_defi = any(
        tx.get("functionName", "").lower().startswith(m)
        for tx in transactions
        for m in defi_methods
    )
    if has_defi:
        labels.append("defi_user")

    return labels


def _apply_filters(whales: List[Dict], filters: Dict) -> List[Dict]:
    """Apply user filter criteria to scored whales."""
    result = []
    for w in whales:
        if filters.get("min_win_rate") and w.get("win_rate", 0) < filters["min_win_rate"]:
            continue
        if filters.get("min_roi") and w.get("roi", 0) < filters["min_roi"]:
            continue
        if filters.get("min_profit") and w.get("profit_usd", 0) < filters["min_profit"]:
            continue
        if filters.get("min_score") and w.get("score", 0) < filters["min_score"]:
            continue
        result.append(w)

    result.sort(key=lambda x: x.get("score", 0), reverse=True)
    return result
