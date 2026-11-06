from thesis_routing.data.normalize_text import normalize_text

def test_normalize_nfc() -> None:
    assert normalize_text('café') == 'café'
