from seed import CANDIDATES, JOBS


def test_seed_data_has_requested_deterministic_coverage():
    assert len(CANDIDATES) == 8
    assert len(JOBS) == 25
    assert any(not remote and location == "Bangalore" for *_, location, _minimum, _maximum, remote in JOBS)
    assert any(remote for *_, remote in JOBS)
    assert any(years == 0 for _title, _skills, years, *_rest in JOBS)
    assert any(not any(kind == "nice_to_have" for _name, kind in skills) for _title, skills, *_rest in JOBS)
