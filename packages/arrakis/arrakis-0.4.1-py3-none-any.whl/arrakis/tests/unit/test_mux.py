from ...mux import Muxer


def test_muxer():
    keys = {"A", "B", "C"}
    items = [
        (1, "A", None),
        (2, "A", None),
        (1, "B", None),
        (1, "C", None),
        (2, "B", None),
        (3, "A", None),
        (2, "C", None),
        (3, "C", None),
        (3, "B", None),
    ]

    muxer: Muxer = Muxer(keys)
    for time, key, data in items:
        muxer.push(time, key, data)

    for time, item in enumerate(muxer.pull(), start=1):
        assert item.time == time
        assert set(item.keys()) == keys
