"""Address Labeler - Labels known addresses (exchanges, contracts, bots)."""
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Known exchange hot wallets (BSC)
EXCHANGE_WALLETS = {
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance",
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance",
    "0x56Eddb7aa87536c09CCc2793473599fD21A8b17F": "KuCoin",
    "0xf1b0a3efb8e8e4c2dff7a9f2b8ad8c4e6eda1f00": "OKX",
}

# Known MEV bot addresses
MEV_BOTS = {
    "0x00000000003b3cc22af3ae1eac0440bcee416b40": "MEV Bot",
}

# Known contract addresses
KNOWN_CONTRACTS = {
    "0x10ed43c718714eb63d5aa57b78b54704e256024e": "PancakeSwap Router",
    "0x1111111254fb6c44bac0bed2854e76f90643097d": "1inch Router",
    "0x3a8d5c4c2e1d4e3b5f6a7b8c9d0e1f2a3b4c5d6e": "Venus Protocol",
}


class AddressLabeler:
    """Labels addresses with known categories."""

    def __init__(self):
        self.exchange_wallets = EXCHANGE_WALLETS
        self.mev_bots = MEV_BOTS
        self.known_contracts = KNOWN_CONTRACTS

    def label(self, address: str) -> Dict:
        """Get label for an address."""
        addr_lower = address.lower()

        if addr_lower in self.exchange_wallets:
            return {"type": "exchange", "name": self.exchange_wallets[addr_lower]}
        if addr_lower in self.mev_bots:
            return {"type": "mev_bot", "name": self.mev_bots[addr_lower]}
        if addr_lower in self.known_contracts:
            return {"type": "contract", "name": self.known_contracts[addr_lower]}

        return {"type": "unknown", "name": ""}

    def is_exchange(self, address: str) -> bool:
        return address.lower() in self.exchange_wallets

    def is_mev_bot(self, address: str) -> bool:
        return address.lower() in self.mev_bots

    def is_contract(self, address: str) -> bool:
        return address.lower() in self.known_contracts

    def should_exclude(self, address: str, exclude_contracts=True,
                       exclude_exchanges=True, exclude_mev=True) -> bool:
        """Check if address should be excluded from analysis."""
        if exclude_contracts and self.is_contract(address):
            return True
        if exclude_exchanges and self.is_exchange(address):
            return True
        if exclude_mev and self.is_mev_bot(address):
            return True
        return False

    def batch_label(self, addresses: List[str]) -> Dict[str, Dict]:
        return {addr: self.label(addr) for addr in addresses}
