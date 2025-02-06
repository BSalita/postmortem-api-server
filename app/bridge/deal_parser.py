from typing import Dict, List

def parse_pbn_deal(pbn: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Parse a PBN format deal string into a structured format.
    
    Args:
        pbn: String in PBN format (e.g., "N:T5.J98643.K95.76 432.KQ5.863.T984 ...")
        
    Returns:
        Dictionary containing the hands for each direction
    """
    try:
        dealer, hands = pbn.split(":")
        hands = hands.strip().split()
        
        if len(hands) != 4:
            raise ValueError("Invalid number of hands in PBN string")
            
        directions = ['N', 'E', 'S', 'W']
        start_idx = directions.index(dealer)
        
        result = {}
        for i in range(4):
            direction = directions[(start_idx + i) % 4]
            hand = hands[i]
            suits = hand.split(".")
            
            if len(suits) != 4:
                raise ValueError(f"Invalid hand format for {direction}")
                
            result[direction] = {
                'S': list(suits[0]),
                'H': list(suits[1]),
                'D': list(suits[2]),
                'C': list(suits[3])
            }
            
        return result
        
    except Exception as e:
        raise ValueError(f"Error parsing PBN deal: {str(e)}")
