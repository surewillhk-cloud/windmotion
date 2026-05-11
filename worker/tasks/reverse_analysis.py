"""Reverse Analysis Task - 6-phase reverse inference pipeline (R0-R5).

Phase R0: Data Fetch (transactions + prices via DataFetch + PriceOracle)
Phase R1: Factor Reverse (transaction classification + round identification via FactorReverse)
Phase R2: Decision node identification + environment reconstruction
Phase R3: Factor scoring (F1-F5)
Phase R4: Strategy pattern matching
Phase R5: Report generation
"""
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute the reverse analysis pipeline."""
    address = payload["address"]
    chain = payload.get("chain", "bsc")
    publish = context["publish_progress"]

    pg = context["pg"]
    neo4j = context["neo4j"]
    agent_pool = context["agent_pool"]
    model_router = context["model_router"]
    redis = context["redis"]
    llm_caller = context.get("llm_caller")

    analysis_id = context["task_id"]
    results: Dict[str, Any] = {}

    # ── Phase R0: Data Fetch ─────────────────────────────────
    publish(5, "Phase R0: Fetching on-chain data and prices...")
    from backend.skills.data_fetch import DataFetch
    data_fetch = DataFetch()

    # Fetch transactions
    tx_result = await data_fetch.execute({
        "data_type": "transactions",
        "params": {"address": address, "chain": chain, "limit": 200},
    })
    transactions = tx_result.data.get("data", {}).get("transactions", []) if tx_result.success else []

    # Fetch token transfers
    transfer_result = await data_fetch.execute({
        "data_type": "token_transfers",
        "params": {"address": address, "chain": chain, "limit": 200},
    })
    token_transfers = transfer_result.data.get("data", {}).get("transfers", []) if transfer_result.success else []

    # Fetch BNB balance
    balance_result = await data_fetch.execute({
        "data_type": "balance",
        "params": {"address": address},
    })
    balance = balance_result.data.get("data", {}).get("balance_bnb", 0) if balance_result.success else 0

    # Fetch price data for tokens involved
    price_data: Dict[str, Any] = {}
    token_addresses = _extract_unique_tokens(transactions, token_transfers)
    for token_addr in token_addresses[:10]:  # limit to avoid API abuse
        price_result = await data_fetch.execute({
            "data_type": "price_history",
            "params": {"token": token_addr, "chain": chain, "days": 90},
        })
        if price_result.success:
            price_data[token_addr] = price_result.data.get("data", {}).get("prices", [])

    publish(15, f"Phase R0: Fetched {len(transactions)} txs, {len(token_transfers)} transfers, {len(price_data)} price series")

    results["phase_R0"] = {
        "transactions": transactions,
        "token_transfers": token_transfers,
        "balance_bnb": balance,
        "price_data": price_data,
        "token_count": len(token_addresses),
    }

    # ── Phase R1: Factor Reverse ─────────────────────────────
    publish(20, "Phase R1: Classifying transactions and identifying rounds...")
    from backend.skills.factor_reverse import FactorReverse
    factor_reverse = FactorReverse()

    # Merge transactions and transfers for analysis
    combined_txs = _merge_transactions(transactions, token_transfers)

    factor_result = await factor_reverse.execute({
        "address": address,
        "transactions": combined_txs,
        "price_data": price_data,
        "mode": payload.get("mode", "standard"),
    })

    if not factor_result.success:
        raise Exception(f"Factor reverse failed: {factor_result.error}")

    classified_txs = factor_result.data.get("classified_transactions", {})
    decision_nodes = factor_result.data.get("decision_nodes", [])
    factors = factor_result.data.get("factors", {})

    publish(35, f"Phase R1: Classified {sum(classified_txs.values())} txs, found {len(decision_nodes)} decision nodes")

    results["phase_R1"] = {
        "classified_transactions": classified_txs,
        "decision_nodes": decision_nodes,
    }

    # ── Phase R2: Decision Node Identification + Environment ─
    publish(40, "Phase R2: Identifying decision nodes and reconstructing environment...")
    from backend.skills.context_manage import ContextManage
    context_mgr = ContextManage()

    env_result = await context_mgr.execute({
        "address": address,
        "chain": chain,
        "timeframe": payload.get("timeframe", "90d"),
    })
    env_state = env_result.data if env_result.success else {}

    # Enrich decision nodes with price context
    enriched_nodes = _enrich_decision_nodes(decision_nodes, price_data, transactions)

    publish(50, f"Phase R2: Enriched {len(enriched_nodes)} decision nodes with market context")

    results["phase_R2"] = {
        "enriched_nodes": enriched_nodes,
        "environment_state": env_state,
    }

    # ── Phase R3: Factor Scoring (F1-F5) ─────────────────────
    publish(55, "Phase R3: Computing factor scores (F1-F5)...")
    factor_scores = factors  # already computed in R1 by FactorReverse

    # If LLM caller available, use it for deeper analysis
    if llm_caller and enriched_nodes:
        llm_analysis = await _llm_factor_analysis(
            llm_caller, address, enriched_nodes, factor_scores, price_data
        )
        if llm_analysis:
            factor_scores = _merge_factor_scores(factor_scores, llm_analysis)

    f1 = factor_scores.get("F1_entry_timing", {}).get("score", 0)
    f2 = factor_scores.get("F2_exit_timing", {}).get("score", 0)
    f3 = factor_scores.get("F3_position_management", {}).get("score", 0)
    f4 = factor_scores.get("F4_token_selection", {}).get("score", 0)
    f5 = factor_scores.get("F5_behavior_pattern", {}).get("score", 0)

    publish(65, f"Phase R3: F1={f1:.1f} F2={f2:.1f} F3={f3:.1f} F4={f4:.1f} F5={f5:.1f}")

    results["phase_R3"] = {
        "factor_scores": factor_scores,
        "factor_summary": {
            "F1_entry_timing": f1,
            "F2_exit_timing": f2,
            "F3_position_management": f3,
            "F4_token_selection": f4,
            "F5_behavior_pattern": f5,
            "average": round((f1 + f2 + f3 + f4 + f5) / 5, 2),
        },
    }

    # ── Phase R4: Strategy Pattern Matching ──────────────────
    publish(70, "Phase R4: Matching strategy patterns...")
    matched_strategies = factor_result.data.get("matched_strategies", [])
    roi_data = factor_result.data.get("roi_data", {})

    # Pattern matching with LLM if available
    if llm_caller and factor_scores:
        pattern_llm = await _llm_pattern_matching(
            llm_caller, factor_scores, matched_strategies, enriched_nodes
        )
        if pattern_llm:
            matched_strategies = pattern_llm

    primary_strategy = matched_strategies[0] if matched_strategies else None

    publish(80, f"Phase R4: Matched {len(matched_strategies)} strategies" +
            (f" (primary: {primary_strategy.get('pattern_name', 'N/A')})" if primary_strategy else ""))

    results["phase_R4"] = {
        "matched_strategies": matched_strategies,
        "primary_strategy": primary_strategy,
        "roi_data": roi_data,
    }

    # ── Phase R5: Report Generation ──────────────────────────
    publish(85, "Phase R5: Generating report...")
    from backend.skills.report_generate import ReportGenerate
    report_skill = ReportGenerate()

    # Build analysis data for report
    analysis_data = {
        "type": "reverse",
        "address": address,
        "chain": chain,
        "factor_scores": results["phase_R3"]["factor_scores"],
        "factor_summary": results["phase_R3"]["factor_summary"],
        "decision_nodes": enriched_nodes,
        "classified_transactions": classified_txs,
        "matched_strategies": matched_strategies,
        "primary_strategy": primary_strategy,
        "roi_data": roi_data,
        "environment_state": env_state,
        "rounds": _build_rounds_from_nodes(enriched_nodes),
    }

    report_result = await report_skill.execute(
        {"analysis_data": analysis_data},
        context={"agent_pool": agent_pool, "llm_caller": llm_caller},
    )
    report = report_result.data if report_result.success else {}

    publish(92, "Phase R5: Report generated")

    results["phase_R5"] = report

    # ── Deliberation check (if factor spread > threshold) ────
    scores_list = [f1, f2, f3, f4, f5]
    score_spread = max(scores_list) - min(scores_list) if scores_list else 0

    if score_spread > 2.0:
        publish(94, f"Deliberation triggered (factor spread={score_spread:.1f})...")
        from backend.skills.deliberate import Deliberate
        deliberation = Deliberate()
        delib_result = await deliberation.execute({
            "agent_results": _build_deliberation_agents(factor_scores),
            "most_divergent_pair": _find_divergent_pair(factor_scores),
            "graph_snapshot": {"nodes": [], "edges": []},
            "spread": score_spread * 20,  # scale to percentage
            "weighted_probability": results["phase_R3"]["factor_summary"]["average"] * 20,
        }, context={"agent_pool": agent_pool, "llm_caller": llm_caller})

        results["deliberation"] = {
            "triggered": True,
            "spread": score_spread,
            "records": delib_result.data if delib_result.success else {},
        }
    else:
        results["deliberation"] = {"triggered": False, "spread": score_spread}

    # ── Persist ──────────────────────────────────────────────
    publish(97, "Saving results...")
    await _save_reverse_analysis(pg, analysis_id, address, chain, results)
    await redis.set_json(f"analysis:{analysis_id}:result", results, ttl=86400)

    publish(100, "Reverse analysis complete")

    return {
        "analysis_id": analysis_id,
        "address": address,
        "chain": chain,
        "factor_scores": results["phase_R3"]["factor_summary"],
        "matched_strategies": matched_strategies,
        "decision_nodes": enriched_nodes,
        "deliberation": results.get("deliberation", {}),
        "report": report,
    }


def _extract_unique_tokens(transactions: List[Dict], transfers: List[Dict]) -> List[str]:
    """Extract unique token addresses from transactions and transfers."""
    tokens = set()
    for tx in transactions:
        # For BNB transactions, use WBNB address
        if tx.get("value", "0") != "0" and not tx.get("contractAddress"):
            tokens.add("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # WBNB
        if tx.get("contractAddress"):
            tokens.add(tx["contractAddress"].lower())
    for tf in transfers:
        ca = tf.get("contractAddress", "")
        if ca:
            tokens.add(ca.lower())
    return list(tokens)


def _merge_transactions(transactions: List[Dict], transfers: List[Dict]) -> List[Dict]:
    """Merge external transactions and token transfers into unified format."""
    merged = []
    for tx in transactions:
        merged.append({
            "hash": tx.get("hash", ""),
            "from": tx.get("from", "").lower(),
            "to": tx.get("to", "").lower(),
            "value_wei": int(tx.get("value", "0")),
            "value_bnb": int(tx.get("value", "0")) / 1e18,
            "timestamp": int(tx.get("timeStamp", 0)),
            "block": int(tx.get("blockNumber", 0)),
            "method": tx.get("functionName", ""),
            "is_error": tx.get("isError", "0") == "1",
            "type": _classify_tx_method(tx.get("functionName", "")),
            "source": "external",
        })
    for tf in transfers:
        merged.append({
            "hash": tf.get("hash", ""),
            "from": tf.get("from", "").lower(),
            "to": tf.get("to", "").lower(),
            "value_wei": int(tf.get("value", "0")),
            "token": tf.get("tokenSymbol", ""),
            "token_address": tf.get("contractAddress", "").lower(),
            "timestamp": int(tf.get("timeStamp", 0)),
            "block": int(tf.get("blockNumber", 0)),
            "type": "token_transfer",
            "source": "token_transfer",
        })
    merged.sort(key=lambda x: x.get("timestamp", 0))
    return merged


def _classify_tx_method(function_name: str) -> str:
    """Classify a transaction by its function name."""
    fn = function_name.lower()
    if "swap" in fn:
        return "swap"
    elif "addliquidity" in fn:
        return "lp_add"
    elif "removeliquidity" in fn:
        return "lp_remove"
    elif "deposit" in fn:
        return "deposit"
    elif "withdraw" in fn:
        return "withdraw"
    elif "borrow" in fn:
        return "borrow"
    elif "repay" in fn:
        return "repay"
    elif "transfer" in fn:
        return "transfer"
    elif "approve" in fn:
        return "approve"
    elif fn == "":
        return "bnb_transfer"
    return "other"


def _enrich_decision_nodes(
    nodes: List[Dict], price_data: Dict, transactions: List[Dict]
) -> List[Dict]:
    """Enrich decision nodes with price context at the time of each decision."""
    enriched = []
    for node in nodes:
        enriched_node = dict(node)
        # Add price context if available
        node_type = node.get("type", "")
        if "INITIAL_BUY" in node_type or "ADD_POSITION" in node_type:
            enriched_node["action"] = "buy"
        elif "EXIT" in node_type:
            enriched_node["action"] = "sell"
        elif "HOLD" in node_type:
            enriched_node["action"] = "hold"
        else:
            enriched_node["action"] = "other"
        enriched.append(enriched_node)
    return enriched


def _build_rounds_from_nodes(nodes: List[Dict]) -> List[Dict]:
    """Group decision nodes into trading rounds."""
    rounds = []
    current_round: Dict[str, Any] = {"trades": [], "round_num": 1}

    for node in nodes:
        action = node.get("action", "")
        if action == "buy" and current_round["trades"] and any(
            t.get("action") == "sell" for t in current_round["trades"]
        ):
            # Previous round ended with a sell, start new round
            if current_round["trades"]:
                rounds.append(current_round)
            current_round = {"trades": [], "round_num": len(rounds) + 1}

        current_round["trades"].append(node)

    if current_round["trades"]:
        rounds.append(current_round)

    return rounds


async def _llm_factor_analysis(
    llm_caller, address: str, nodes: List[Dict], factors: Dict, price_data: Dict
) -> Optional[Dict]:
    """Use LLM to deepen factor analysis."""
    try:
        system_prompt = """你是一个链上交易行为分析专家。请根据提供的决策节点和交易数据，对以下5个因子进行评分（0-5分）：
F1 入场时机、F2 出场时机、F3 仓位管理、F4 代币选择、F5 行为模式。
输出JSON格式：{"F1_entry_timing": {"score": x, "reasoning": "..."}, ...}"""

        user_prompt = f"""地址: {address}
决策节点: {json.dumps(nodes[:20], ensure_ascii=False)}
现有因子分数: {json.dumps({k: v.get('score', 0) for k, v in factors.items()}, ensure_ascii=False)}"""

        result = await llm_caller(
            task_type="factor_analysis",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_tier="medium",
            json_mode=True,
        )
        if result.get("success"):
            return result.get("data", {}).get("parsed", {})
    except Exception as e:
        logger.warning(f"LLM factor analysis failed: {e}")
    return None


async def _llm_pattern_matching(
    llm_caller, factor_scores: Dict, matched: List[Dict], nodes: List[Dict]
) -> Optional[List[Dict]]:
    """Use LLM to refine strategy pattern matching."""
    try:
        system_prompt = """你是策略模式匹配专家。根据因子分数和决策节点，判断最匹配的交易策略模式。
输出JSON数组: [{"pattern_id": "...", "pattern_name": "...", "match_ratio": 0.x, "reasoning": "..."}]"""

        user_prompt = f"""因子分数: {json.dumps({k: v.get('score', 0) for k, v in factor_scores.items()}, ensure_ascii=False)}
已匹配模式: {json.dumps(matched[:5], ensure_ascii=False)}
决策节点: {json.dumps(nodes[:10], ensure_ascii=False)}"""

        result = await llm_caller(
            task_type="pattern_matching",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_tier="medium",
            json_mode=True,
        )
        if result.get("success"):
            parsed = result.get("data", {}).get("parsed", [])
            if isinstance(parsed, list):
                return parsed
    except Exception as e:
        logger.warning(f"LLM pattern matching failed: {e}")
    return None


def _merge_factor_scores(original: Dict, llm_analysis: Dict) -> Dict:
    """Merge LLM analysis into original factor scores."""
    merged = dict(original)
    for key in ["F1_entry_timing", "F2_exit_timing", "F3_position_management", "F4_token_selection", "F5_behavior_pattern"]:
        if key in llm_analysis and isinstance(llm_analysis[key], dict):
            if key not in merged:
                merged[key] = {}
            llm_score = llm_analysis[key].get("score")
            if llm_score is not None:
                # Weighted average: 60% algorithmic, 40% LLM
                orig_score = merged[key].get("score", 3.0)
                merged[key]["score"] = round(orig_score * 0.6 + llm_score * 0.4, 2)
            if "reasoning" in llm_analysis[key]:
                merged[key]["llm_reasoning"] = llm_analysis[key]["reasoning"]
    return merged


def _build_deliberation_agents(factor_scores: Dict) -> List[Dict]:
    """Build synthetic agent results for deliberation from factor scores."""
    agents = []
    for key, label in [
        ("F1_entry_timing", "入场分析师"),
        ("F2_exit_timing", "出场分析师"),
        ("F3_position_management", "仓位管理分析师"),
    ]:
        score = factor_scores.get(key, {}).get("score", 3.0)
        agents.append({
            "agent_id": key,
            "agent_name": label,
            "agent_type": "B",
            "probability_estimate": round(score * 20),  # scale 0-5 to 0-100
            "causal_analysis": factor_scores.get(key, {}).get("llm_reasoning", ""),
        })
    return agents


def _find_divergent_pair(factor_scores: Dict) -> Dict:
    """Find the most divergent factor pair."""
    scores = {}
    for key in ["F1_entry_timing", "F2_exit_timing", "F3_position_management", "F4_token_selection", "F5_behavior_pattern"]:
        scores[key] = factor_scores.get(key, {}).get("score", 3.0)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    if len(sorted_scores) < 2:
        return {"low": {"agent_id": "", "probability": 50}, "high": {"agent_id": "", "probability": 50}}

    return {
        "low": {"agent_id": sorted_scores[0][0], "probability": round(sorted_scores[0][1] * 20)},
        "high": {"agent_id": sorted_scores[-1][0], "probability": round(sorted_scores[-1][1] * 20)},
    }


async def _save_reverse_analysis(pg, analysis_id: str, address: str, chain: str, results: Dict):
    """Persist reverse analysis to PostgreSQL."""
    try:
        await pg.execute(
            "INSERT INTO analyses (id, address, chain, type, status, result, created_at) "
            "VALUES ($1, $2, $3, 'reverse', 'completed', $4, NOW()) "
            "ON CONFLICT (id) DO UPDATE SET status = 'completed', result = $4",
            analysis_id, address, chain,
            json.dumps(results, ensure_ascii=False, default=str)
        )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")
