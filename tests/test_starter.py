import p2p.starter as starter

def test_P2P():
    msg=starter.p2p()
    assert msg == "P2P Protocol to be built"