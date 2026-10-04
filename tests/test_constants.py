from entoolkit import constants


def test_size_limits():
    assert constants.EN_MAXID == 31
    assert constants.EN_MAXMSG == 255

def test_enums():
    # Node Types
    assert constants.EN_JUNCTION == 0
    assert constants.EN_TANK == 2
    
    # Demand Models (2.2)
    assert constants.EN_DDA == 0
    assert constants.EN_PDA == 1

    # Status Codes (2.2 action codes)
    assert constants.EN_UNCONDITIONAL == 0
    assert constants.EN_CONDITIONAL == 1
