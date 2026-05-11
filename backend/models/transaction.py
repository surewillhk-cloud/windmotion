from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime


@dataclass
class Transaction:
    hash: str
    from_address: str
    to_address: str
    chain: str = "bsc"
    block_number: int = 0
    timestamp: Optional[datetime] = None
    value_usd: float = 0
    token_address: Optional[str] = None
    token_symbol: Optional[str] = None
    token_amount: float = 0
    tx_type: str = "TRANSFER"  # SWAP, TRANSFER, APPROVE, STAKE, BORROW, LP_JOIN, LP_EXIT
    dex: Optional[str] = None
    gas_used: int = 0
    gas_price: int = 0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "hash": self.hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "chain": self.chain,
            "block_number": self.block_number,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "value_usd": self.value_usd,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "token_amount": self.token_amount,
            "tx_type": self.tx_type,
            "dex": self.dex,
            "gas_used": self.gas_used,
            "metadata": self.metadata
        }
