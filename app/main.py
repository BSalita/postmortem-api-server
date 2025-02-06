from fastapi import FastAPI, HTTPException
from typing import List, Optional
from .models import DealRequest, AuctionResponse
from .services.auction_service import generate_auction
from .services.ffbridge_service import create_df_from_group_session_pair
import polars as pl
from .services.acbl_service import get_club_player_history, get_tournament_player_history, get_acbl_tournament_session_results, get_club_results_from_acbl_number


# There's weirdness with unicorn sometimes. if so:
# 1) kill python "unicorn" in command line process
# 2) kill python "spawn" in command line process


app = FastAPI(
    title="Bridge Postmortem API",
    description="API for analyzing bridge deals and auctions",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Bridge Postmortem API"}

@app.post("/get_auction", response_model=AuctionResponse)
async def get_auction(request: DealRequest) -> AuctionResponse:
    try:
        auction: List[str]
        explanation: str
        auction, explanation = generate_auction(request.pbn)
        return AuctionResponse(
            auction=auction,
            explanation=explanation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# https://ffbridge.fr/competitions/results/groups/7878/sessions/107118/pairs/3976783
@app.get("/ffbridge.fr/competitions/results/groups/{group_id}/sessions/{session_id}/pairs/{pair_id}")
async def get_ffbridge_data(
    group_id: str,
    session_id: str,
    pair_id: str
) -> dict:
    try:
        print("Starting ffbridge data fetch...")
        df = await create_df_from_group_session_pair(group_id, session_id, pair_id)
        print(f"DF created: {df is not None}")
        return {
            "success": True,
            "data": df.to_dict(as_series=False)
        }
    except Exception as e:
        print(f"Error in get_ffbridge_data: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# change route to something sensible for acbl
# https://my.acbl.org/club-results/my-results/{acbl_number}
@app.get("/acbl/club/player_id/{player_id}")
async def get_acbl_club_player(player_id: str) -> dict:
    try:
        player_data = await get_club_player_history(player_id)
        if player_data is None:
            raise HTTPException(status_code=404, detail="Club player not found")
        return {
            "success": True,
            "data": player_data
        }
    except Exception as e:
        print(f"Error: {e}")  # For debugging
        raise HTTPException(status_code=404, detail=str(e))  # Changed from 501 to 404

# f"https://my.acbl.org/club-results/my-results/{acbl_number}"
@app.get("/acbl/club/results/{acbl_number}")
async def get_acbl_club_results(acbl_number: str) -> dict:
    try:
        results = await get_club_results_from_acbl_number(acbl_number)
        if results is None:
            raise HTTPException(status_code=404, detail="Club results not found")
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# https://api.acbl.org/v1/tournament/player/history_query
@app.get("/acbl/tournament/player_id/{player_id}")
async def get_acbl_tournament_player(player_id: str) -> dict:
    try:
        player_data = await get_tournament_player_history(player_id)
        if player_data is None:
            raise HTTPException(status_code=404, detail="Tournament player not found")
        return {
            "success": True,
            "data": player_data
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# https://api.acbl.org/v1/tournament/session
@app.get("/acbl/tournament/session/{session_id}")
async def get_acbl_tournament_session(session_id: str) -> dict:
    try:
        session_data = await get_acbl_tournament_session_results(session_id)
        if session_data is None:
            raise HTTPException(status_code=404, detail="Tournament session not found")
        return {
            "success": True,
            "data": session_data
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
