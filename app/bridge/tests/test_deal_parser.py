import pytest
from ...bridge.deal_parser import parse_pbn_deal

def test_parse_pbn_deal_valid():
    test_deal = "N:T5.J98643.K95.76 432.KQ5.863.T984 86.AT72.QJT7.AKQ AKQJ97..A42.J532"
    result = parse_pbn_deal(test_deal)
    
    # Test structure
    assert isinstance(result, dict)
    assert all(d in result for d in ['N', 'E', 'S', 'W'])
    assert all(s in result['N'] for s in ['S', 'H', 'D', 'C'])
    
    # Test specific values
    assert result['N']['S'] == list('T5')
    assert result['N']['H'] == list('J98643')
    assert result['N']['D'] == list('K95')
    assert result['N']['C'] == list('76')

def test_parse_pbn_deal_invalid_format():
    with pytest.raises(ValueError):
        parse_pbn_deal("Invalid:Deal Format")

def test_parse_pbn_deal_wrong_number_of_hands():
    with pytest.raises(ValueError):
        parse_pbn_deal("N:T5.J98643.K95.76 432.KQ5.863.T984 86.AT72.QJT7.AKQ")
