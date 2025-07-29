from blissclient import BlissClient


def test_client_info(blissclient: BlissClient):
    assert blissclient.info.bliss_version
