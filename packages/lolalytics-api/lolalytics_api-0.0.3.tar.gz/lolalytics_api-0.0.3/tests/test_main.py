import pytest
import json
from lolalytics_api import get_tierlist, get_counters, InvalidRank, InvalidLane


class TestGetTierlist:
    def test_invalid_lane_raises_error(self):
        with pytest.raises(InvalidLane):
            get_tierlist(5, "test", "gm+")

    def test_invalid_rank_raises_error(self):
        with pytest.raises(InvalidRank):
            get_tierlist(5, "top", "test")

    def test_lane_shortcuts(self):
        valid_lanes = ['top', 'jg', 'jng', 'jungle', 'mid', 'middle', 'bot', 'bottom', 'adc', 'support', 'supp', 'sup']
        for lane in valid_lanes:
            try:
                get_tierlist(1, lane)
            except InvalidLane:
                pytest.fail(f"Valid lane '{lane}' raised InvalidLane error")

    def test_get_tierlist_returns_json(self):
        result = get_tierlist(1)
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert '0' in parsed
        assert 'rank' in parsed['0']
        assert 'champion' in parsed['0']
        assert 'tier' in parsed['0']
        assert 'winrate' in parsed['0']


class TestGetCounters:
    def test_empty_champion_raises_error(self):
        with pytest.raises(ValueError, match="Champion name cannot be empty"):
            get_counters(5, "")

    def test_get_counters_returns_json(self):
        result = get_counters(1, "yasuo")
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert '0' in parsed
        assert 'champion' in parsed['0']
        assert 'winrate' in parsed['0']
