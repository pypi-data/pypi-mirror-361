import json
from tempfile import NamedTemporaryFile
from unittest import mock

import pytest

from mq_randomizer.quote_types import MQuote
from mq_randomizer.randomizer import MQRandomizer


class TestMQRandomizer:

    @pytest.fixture
    def mock_data(self):
        return {
            "meta": {
                "version": 1,
                "media_title": "Test Movie",
                "media_type": "movie",
                "year": 2023,
                "description": "A test movie"
            },
            "quotes": [
                {
                    "quote_type": "single",
                    "characters": ["Character1"],
                    "lines": [{"Character1": "Line 1"}]
                },
                {
                    "quote_type": "single",
                    "characters": ["Character2"],
                    "lines": [{"Character2": "Line 2"}]
                }
            ]
        }

    @pytest.fixture
    def randomizer_default_data(self, mock_data):
        with mock.patch.object(MQRandomizer, '_default_quote_data', return_value=mock_data):
            return MQRandomizer()

    @pytest.fixture
    def randomizer_with_path(self, mock_data):
        # python 3.12 adds delete_on_close, which lets us close the file
        # within the context, but still re-open it
        # however, python <= 3.11 only has the delete kwarg which means
        # the file gets deleted on close, or when the context is exited
        # with NamedTemporaryFile(mode="w", delete_on_close=False) as f:
        with NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump(mock_data, f)
            # on some systems, you can open the file elsewhere even if it's already
            # open here. But not on Windows. So we have to close the file
            f.close()
            return MQRandomizer(quote_data_src=f.name)

    @pytest.fixture
    def randomizer_with_dict(self, mock_data):
        return MQRandomizer(quote_data_src=mock_data)

    def test_initialization_010(self, randomizer_default_data):
        assert randomizer_default_data._media_title == "Test Movie"
        assert randomizer_default_data._media_type == "movie"
        assert randomizer_default_data._year == 2023
        assert len(randomizer_default_data._quotes) == 2
        assert isinstance(randomizer_default_data._quotes[0], MQuote)

    def test_initialization_020(self, randomizer_with_path):
        assert randomizer_with_path._media_title == "Test Movie"
        assert randomizer_with_path._media_type == "movie"
        assert randomizer_with_path._year == 2023
        assert len(randomizer_with_path._quotes) == 2
        assert isinstance(randomizer_with_path._quotes[0], MQuote)

    def test_initialization_030(self, randomizer_with_dict):
        assert randomizer_with_dict._media_title == "Test Movie"
        assert randomizer_with_dict._media_type == "movie"
        assert randomizer_with_dict._year == 2023
        assert len(randomizer_with_dict._quotes) == 2
        assert isinstance(randomizer_with_dict._quotes[0], MQuote)

    def test_validation_with_external_data(self, external_data):
        randomizer = MQRandomizer(external_data)
        assert randomizer._validated is True

    def test_initialization_with_external_data(self, external_data):
        randomizer = MQRandomizer(external_data)
        assert len(randomizer._quotes) == 17

    def test_random_quote_with_external_data(self, external_data):
        randomizer = MQRandomizer(external_data)
        quote = randomizer.random_quote()
        assert isinstance(quote, MQuote)

    def test_quote_at_index_with_external_data(self, external_data):
        randomizer = MQRandomizer(external_data)
        quote_str = "In A.D. 2101\nWar was beginning."
        quote = randomizer.quote_at_index(0)
        assert isinstance(quote, MQuote)
        assert str(quote) == quote_str

    def test_random_quote(self, randomizer_default_data):
        quote = randomizer_default_data.random_quote()
        assert isinstance(quote, MQuote)
        assert len(randomizer_default_data._quotes) > 0

    def test_quote_at_index_010(self, randomizer_default_data):
        assert len(randomizer_default_data._quotes) > 0
        quote = randomizer_default_data.quote_at_index(0)
        assert isinstance(quote, MQuote)

    def test_quote_at_index_020(self, randomizer_default_data):
        assert len(randomizer_default_data._quotes) > 0
        quote = randomizer_default_data.quote_at_index(1)
        assert isinstance(quote, MQuote)

    def test_quote_at_index_030(self, randomizer_default_data):
        assert len(randomizer_default_data._quotes) > 0
        with pytest.raises(IndexError):
            randomizer_default_data.quote_at_index(1000)

    def test_random_quote_empty(self, randomizer_default_data):
        randomizer_default_data._quotes = []
        with pytest.raises(IndexError):
            randomizer_default_data.random_quote()
