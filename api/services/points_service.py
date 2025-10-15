from typing import Dict

class PointsService:
    def __init__(self):
        # In-memory points storage (demo)
        self.points: Dict[str, int] = {}  # wallet -> whole tokens (not raw units)
        # Clear all points on startup for fresh start
        self.points.clear()
    
    def get_points(self, wallet: str) -> int:
        """Get points for a wallet"""
        return self.points.get(wallet, 0)
    
    def add_points(self, wallet: str, amount: int) -> int:
        """Add points to a wallet"""
        self.points[wallet] = self.points.get(wallet, 0) + amount
        return self.points[wallet]
    
    def reset_points(self, wallet: str) -> None:
        """Reset points for a wallet"""
        self.points[wallet] = 0
    
    def claim_points(self, wallet: str) -> int:
        """Claim all points for a wallet and reset to 0"""
        amount = self.points.get(wallet, 0)
        self.points[wallet] = 0
        return amount

# Global instance
points_service = PointsService()

