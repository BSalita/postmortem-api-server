import polars as pl
from typing import Dict, Any, List, Optional
import json
import httpx


def test_for_create_df_from_group_session_pair(group_id: str, session_id: str, pair_id: str) -> Optional[pl.DataFrame]:
    """
    Mock version of test_for_create_df_from_group_session_pair for testing
    
    Args:
        url (str): FFBridge URL (ignored in mock)
        
    Returns:
        Optional[pl.DataFrame]: Test DataFrame with dummy data
    """

    # Create sample data
    data = {
        "board_id": [1, 2, 3],
        "group_id": [7878] * 3,
        "session_id": [107118] * 3,
        "team_id": [3976783] * 3,
        "contract": ["4H", "3NT", "6S"],
        "declarer": ["N", "S", "E"],
        "result": [10, 9, 12],
        "score_ns": [420, 400, -1430],
        "score_ew": [-420, -400, 1430]
    }
    print(f"test_for_create_df_from_group_session_pair: {group_id} {session_id} {pair_id}")
    return pl.DataFrame(data)


def flatten_json(nested_json: Dict) -> Dict:
    """Flatten nested JSON structure into a single level dictionary"""
    flat_dict = {}
    
    def flatten(x: Any, name: str = '') -> None:
        #print(f"flattening {name}")
        if isinstance(x, dict):
            for key, value in x.items():
                flatten(value, f"{name}_{key}" if name else key)
        elif isinstance(x, list):
            #for i, value in enumerate(x):
            #    flatten(value, f"{name}_{i}")
            flat_dict[name] = x
        else:
            flat_dict[name] = x
            
    flatten(nested_json)
    return flat_dict


def create_dataframe(data: List[Dict[str, Any]]) -> pl.DataFrame:
    """Create a Polars DataFrame from flattened JSON data"""
    try:
        # Flatten each record in the dict or list
        if isinstance(data, dict):
            #print(f"flattening dict")
            flattened_data = [flatten_json(data)]
        elif isinstance(data, list):
            #print(f"flattening list")
            flattened_data = [flatten_json(record) for record in data]
        else:
            print(f"Unsupported data type: {type(data)}")
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Create DataFrame
        df = pl.DataFrame(flattened_data)
        return df
        
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        print(f"Data structure: {type(data)}")
        print(f"First record: {json.dumps(data[0], indent=2) if data else 'Empty'}")
        raise

# obsolete?
def get_scores_data(scores_json: List[Dict[str, Any]], group_id: int, session_id: int, team_id: int) -> Optional[pl.DataFrame]:
    print(f"creating dataframe from scores_json")
    df = create_dataframe(scores_json)
    if df is None:
        print(f"Couldn't make dataframe from scores_json for {team_id=} {session_id=}")
        return None
    if 'board_id' not in df.columns: # todo: find out why 'board_id' doesn't exist
        print(f"No board_id for team_session_scores: {team_id} {session_id}")
        return None
    if df['lineup_segment_game_homeTeam_orientation'].ne('NS').any():
        print(f"Not a Mitchell movement. homeTeam_orientations are not all NS. Skipping: {team_id} {session_id}")
        return None
    if df['lineup_segment_game_awayTeam_orientation'].ne('EW').any():
        print(f"Not a Mitchell movement. awayTeam_orientations are not all EW. Skipping: {team_id} {session_id}")
        return None
    return df


async def create_df_from_group_session_pair(group_id: str, session_id: str, pair_id: str) -> Optional[pl.DataFrame]:
    try:
        
        # get team data
        api_team_url = f'https://api-lancelot.ffbridge.fr/results/teams/{pair_id}'
        print(f"api_team_url:{api_team_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(api_team_url)
            response.raise_for_status()
            team_json = response.json()
            print(f"got team_json")
            team_df = create_dataframe(team_json)
            # columns: ['awayGames', 'homeGames', 'orientation', 'player1_id', 'player1_migrationId', 'player1_firstName', 'player1_lastName',
            #  'player2_firstName', 'player2_lastName', 'player2_id', 'player2_migrationId',
            #  'player3', 'player4', 'player5', 'player6', 'player7', 'player8', 'rankings', 'section', 'startTableNumber', 'id', 'label']
            print(f"team_df:",team_df.columns)
            print(team_df)

        api_scores_url = f'https://api-lancelot.ffbridge.fr/results/teams/{pair_id}/session/{session_id}/scores'
        print(f"api_scores_url:{api_scores_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(api_scores_url)
            response.raise_for_status()
            scores_json = response.json() 
        df = get_scores_data(scores_json, group_id, session_id, pair_id)

        # initialize columns which are needed for SQL queries.
        # todo: should these be initialized in ffbridgelib.convert_ffdf_to_mldf()?
        df = df.with_columns(pl.lit(group_id).cast(pl.UInt32).alias('group_id'))
        df = df.with_columns(pl.lit(session_id).cast(pl.UInt32).alias('session_id'))
        df = df.with_columns(pl.lit(pair_id).cast(pl.UInt32).alias('team_id'))
        df = df.with_columns(pl.lit(team_df['orientation'].first()).cast(pl.String).alias('orientation'))
        df = df.with_columns(pl.lit(team_df['player1_id'].first()).cast(pl.UInt32).alias('player1_id'))
        df = df.with_columns(pl.lit(team_df['player1_firstName'].first()).cast(pl.String).alias('player1_firstName'))
        df = df.with_columns(pl.lit(team_df['player1_lastName'].first()).cast(pl.String).alias('player1_lastName'))
        df = df.with_columns(pl.lit(team_df['player2_id'].first()).cast(pl.UInt32).alias('player2_id'))
        df = df.with_columns(pl.lit(team_df['player2_firstName'].first()).cast(pl.String).alias('player2_firstName'))
        df = df.with_columns(pl.lit(team_df['player2_lastName'].first()).cast(pl.String).alias('player2_lastName'))
        # todo: implement awayGames, homeGames, player3, player4, player5, player6, player7, player8, rankings?
        df = df.with_columns(pl.lit(team_df['section'].first()).cast(pl.String).alias('section'))
        df = df.with_columns(pl.lit(team_df['startTableNumber'].first()).cast(pl.UInt16).alias('startTableNumber'))
        df = df.with_columns(pl.struct([pl.col('team_id'),pl.col('session_id')]).alias('team_session_id'))
        df = df.select([pl.col('group_id','team_session_id','session_id','team_id'),pl.all().exclude('group_id','team_session_id','session_id','team_id')])
    except Exception as e:
        print(f"Error creating df from group_session_pair: {e}")
        return None

    return df