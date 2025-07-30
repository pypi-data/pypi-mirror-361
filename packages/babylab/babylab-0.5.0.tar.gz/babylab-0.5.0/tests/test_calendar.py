"""Test calendar"""

from datetime import datetime
import pytest
from babylab import api

timestamp = datetime(2024, 12, 17)


def test_get_age(benchmark):
    """Test ``get_age``"""
    ts = datetime(2024, 5, 1, 3, 4)
    ts_new = datetime(2025, 1, 4, 1, 2)
    age = (5, 5)

    # when only birth date is provided
    assert isinstance(api.get_age(age, ts), tuple)
    assert all(isinstance(d, int) for d in api.get_age(age, ts))
    assert len(api.get_age(age, ts)) == 2

    # when birth date AND ts_new are provided
    assert isinstance(api.get_age(age, ts, ts_new=ts_new), tuple)
    assert all(isinstance(d, int) for d in api.get_age(age, ts, ts_new))
    assert len(api.get_age(age, ts, ts_new)) == 2

    assert api.get_age(age, ts, ts_new) == (13, 7)

    assert all(d > 0 for d in api.get_age(age, ts, ts_new))
    with pytest.raises(api.BadAgeFormat):
        api.get_age(age="5, 4", ts=ts)

    def _get_age():
        api.get_age(age, ts, ts_new)

    benchmark(_get_age)
