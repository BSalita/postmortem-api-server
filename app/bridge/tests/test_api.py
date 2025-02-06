from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from typing import Optional, Dict, Any
import polars as pl

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Bridge Postmortem API"}

def test_get_auction_valid():
    test_deal = "N:T5.J98643.K95.76 432.KQ5.863.T984 86.AT72.QJT7.AKQ AKQJ97..A42.J532"
    response = client.post(
        "/get_auction",
        json={"pbn": test_deal}
    )
    assert response.status_code == 200
    assert "auction" in response.json()
    assert "explanation" in response.json()

def test_get_auction_invalid():
    response = client.post(
        "/get_auction",
        json={"pbn": "invalid deal"}
    )
    assert response.status_code == 400

def mock_create_df_from_group_session_pair(group: str, session: str, pair: str) -> Optional[pl.DataFrame]:
    """Mock version of create_df_from_group_session_pair for testing"""
    data = {
        "board_id": [1, 2, 3],
        "group_id": [int(group)] * 3,
        "session_id": [int(session)] * 3,
        "team_id": [int(pair)] * 3,
        "contract": ["4H", "3NT", "6S"],
        "declarer": ["N", "S", "E"],
        "result": [10, 9, 12],
        "score_ns": [420, 400, -1430],
        "score_ew": [-420, -400, 1430]
    }
    return pl.DataFrame(data)

@patch('app.services.ffbridge_service.create_df_from_group_session_pair')
def test_get_ffbridge_data(mock_create_df):
    """Test the FFBridge data endpoint with known values"""
    # Setup mock return value
    mock_create_df.return_value = mock_create_df_from_group_session_pair("7878", "107118", "3976783")
    
    # Test
    response = client.get("/ffbridge/7878/107118/3976783")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] is True

# TODO: re-Implement test for invalid IDs
def test_get_ffbridge_data_invalid():
    """Test the FFBridge data endpoint with invalid IDs"""
    response = client.get("/ffbridge") # some random invalid url
    assert response.status_code in [404, 500]
    assert "detail" in response.json()

def mock_get_club_player_history(player_id: str) -> Optional[Dict[str, Any]]:
    """Mock ACBL player data response"""
    print(f"in mock: {player_id}")
    if player_id == "2663279":
         return {
                "player_id": "2663279",
                "name": "John Doe",
                "rank": "Life Master",
                "masterpoints": 2500.00
            }
    return None

# https://api.acbl.org/v1/player
# {993420: ('https://my.acbl.org/club-results/my-results/2663279', 'https://my.acbl.org/club-results/details/993420', '2024-04-13, Quick Tricks Friendly Gay DBC, Sat Aft QT 0-2000, Saturday Afternoon, 65.04%')
@patch('app.services.acbl_service.get_club_player_history')
def test_get_acbl_club_player_valid(mock_get_player):
    """Test ACBL club player endpoint with valid ID"""
    mock_data = {
        "player_id": "2663279",
        "name": "Robert Salita",
        "rank": "Life Master",
        "masterpoints": 750.00
    }
    mock_get_player.return_value = mock_data
    
    response = client.get("/acbl/club/player_id/2663279")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["player_id"] == "2663279"

@patch('app.main.get_club_player_history', mock_get_club_player_history)
def test_get_acbl_club_player_invalid():
    """Test ACBL player endpoint with invalid ID"""
    response = client.get("/acbl/club/player_id") # some random invalid url
    assert response.status_code == 404
    assert "detail" in response.json()

# https://my.acbl.org/club-results/my-results/{acbl_number}
@patch('app.services.acbl_service.get_club_results_from_acbl_number')
def test_get_acbl_club_results_valid(mock_get_results):
    """Test ACBL club results endpoint with valid number"""
    mock_data = {
        "acbl_number": "2663279",
        "club_results": [
            {"club": "Virtual Club", "date": "2024-01-15", "score": 65.2},
            {"club": "Bridge Base Online", "date": "2024-01-14", "score": 58.7}
        ]
    }
    mock_get_results.return_value = mock_data
    
    response = client.get("/acbl/club/results/2663279")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["acbl_number"] == "2663279"
    assert "club_results" in data["data"]

# https://api.acbl.org/v1/tournament/player/history_query
@patch('app.services.acbl_service.get_tournament_player_history')
def test_get_acbl_tournament_player_valid(mock_get_tournament_player):
    """Test ACBL tournament player endpoint with valid ID"""
    mock_data = {
        "player_id": "2663279",
        "tournaments": [
            {"name": "Regional", "date": "2024-01-15", "location": "Dallas"},
            {"name": "Sectional", "date": "2024-02-01", "location": "Houston"}
        ]
    }
    mock_get_tournament_player.return_value = mock_data
    
    response = client.get("/acbl/tournament/player_id/2663279")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["player_id"] == "2663279"
    assert "tournaments" in data["data"]

def test_get_acbl_tournament_player_invalid():
    response = client.get("/acbl/tournament/player_id") # some random invalid url
    assert response.status_code == 404
    assert "detail" in response.json()

# https://api.acbl.org/v1/tournament/session
@patch('app.services.acbl_service.get_acbl_tournament_session_results')
def test_get_acbl_tournament_session_valid(mock_get_session):
    """Test ACBL tournament session endpoint with valid ID"""
    mock_data = {
        "session_id": "2402101-07AS-1",
        "event_name": "Open Pairs",
        "date": "2024-02-01",
        "results": [
            {"rank": 1, "pair": "N-S", "score": 65.2},
            {"rank": 2, "pair": "E-W", "score": 58.7}
        ]
    }
    mock_get_session.return_value = mock_data
    
    response = client.get("/acbl/tournament/session/2402101-07AS-1")
    assert response.status_code == 200
    data = response.json()
    print('data:', data)
    assert data["success"] is True
    assert data["data"]["id"] == "2402101-07AS-1"
    assert "tournament" in data["data"]
    assert "event" in data["data"]
    assert "overalls" in data["data"]
    assert "sections" in data["data"]


    