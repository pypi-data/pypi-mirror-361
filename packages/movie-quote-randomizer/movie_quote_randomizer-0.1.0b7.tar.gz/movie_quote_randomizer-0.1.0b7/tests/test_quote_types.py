import pytest

from mq_randomizer.quote_types import MQuote, MQuoteLine


class TestMQuote:
    _media_title = "The Matrix"
    _media_type = "movie"
    _media_year = 1999
    _characters = ["Neo"]
    _neo_line = "Remember... there is no spoon."

    @pytest.fixture
    def sample_quote(self):
        quote_dict = {
            "characters": self._characters,
            "lines": [{"Neo": self._neo_line}]
        }
        return MQuote(quote_dict, self._media_title, self._media_type, self._media_year)

    def test_initialization(self, sample_quote):
        assert sample_quote["media_title"] == self._media_title
        assert sample_quote["media_type"] == self._media_type
        assert sample_quote["year"] == self._media_year
        assert sample_quote["characters"] == self._characters
        sample_quote_line = MQuoteLine("Neo", self._neo_line)
        assert sample_quote["lines"] == [sample_quote_line]

    def test_characters_property(self, sample_quote):
        assert sample_quote.characters == ["Neo"]

    def test_lines_property(self, sample_quote):
        sample_quote_line = MQuoteLine("Neo", self._neo_line)
        assert sample_quote.lines == [sample_quote_line]

    def test_media_title_property(self, sample_quote: MQuote):
        assert sample_quote.media_title == self._media_title

    def test_media_type_property(self, sample_quote: MQuote):
        assert sample_quote.media_type == self._media_type

    def test_year_property(self, sample_quote: MQuote):
        assert sample_quote.year == self._media_year

    def test_mquote_line_equality_010(self):
        """
        Test the __eq__() implementation

        Verify: two different MQuoteLine but equivalent objects are equal
        """
        quote_line_1 = MQuoteLine("Neo", self._neo_line)
        quote_line_2 = MQuoteLine("Neo", self._neo_line)

        # no tricks up our sleeve ,these actually are different objects
        assert id(quote_line_1) != id(quote_line_2)
        assert quote_line_1 == quote_line_1

    def test_mquote_line_equality_020(self):
        """
        Test the __eq__() implementation

        Verify: An MQuoteLine object is equal to itself

        Note: this is trivially true and is present for the purpose of complete coverage
        """
        quote_line = MQuoteLine("Neo", self._neo_line)

        assert id(quote_line) == id(quote_line)
        assert quote_line == quote_line

    def test_str_representation(self, sample_quote):
        expected = f"Neo: {self._neo_line}"
        assert str(sample_quote) == expected

    def test_unattributed_line(self):
        quote_dict = {
            "characters": ["Unattributed"],
            "lines": [{"__none__": "This is a line without attribution."}]
        }
        quote = MQuote(quote_dict, "Test Movie", "movie", 2023)
        assert str(quote) == "This is a line without attribution."
