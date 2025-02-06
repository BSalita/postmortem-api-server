from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class DealRequest(BaseModel):
    pbn: str = Field(..., description="PBN format deal string")

class AuctionResponse(BaseModel):
    auction: List[str] = Field(..., description="List of bids in the auction")
    explanation: str = Field(..., description="Explanation of the auction")

class FFBridgeResponse(BaseModel):
    success: bool = Field(..., description="True if the request was successful")
    data: List[Dict[str, Any]] = Field(..., description="Data returned from the FFBridge API")

class ACBLPlayerResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]]
