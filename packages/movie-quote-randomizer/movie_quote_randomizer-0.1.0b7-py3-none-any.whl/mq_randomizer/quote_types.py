class MQuoteLine:
    UNATTRIBUTED = "__none__"

    def __init__(self, character: str, line: str):
        self._character = character
        self._line = line

    @property
    def line(self) -> str:
        return self._line

    @property
    def character(self) -> str:
        return self._character

    def is_unattributed(self) -> bool:
        return self._character == self.UNATTRIBUTED

    def __eq__(self, other):
        eq = False
        if id(other) == id(self):
            eq = True
        elif isinstance(other, MQuoteLine):
            if other._character == self._character:
                if other._line == self._line:
                    eq = True
        return eq

    def __str__(self):
        if self.is_unattributed():
            _str = self.line
        else:
            _str = f"{self.character}: {self.line}"
        return _str


class MQuote(dict):
    UNATTRIBUTED = "__none__"

    def __init__(self, quote_dict: dict, media_title: str, media_type: str, year: int):
        super().__init__()
        quote_dict = self._convert_quote_lines(quote_dict)
        self.update(quote_dict)
        self["media_title"] = media_title
        self["media_type"] = media_type
        self["year"] = year

    @property
    def characters(self) -> list[str]:
        """
        Get the list of characters in the quote.

        Returns
        -------
        list[str]
            A list of character names associated with the quote.
        """
        return self["characters"]

    @property
    def lines(self) -> list[MQuoteLine]:
        """
        Get the list of lines in the quote.

        Returns
        -------
        list[dict[str, str]]
            A list of dictionaries representing each line of the quote.
        """
        lines = self["lines"]
        return lines

    @property
    def media_title(self) -> str:
        """
        Get the title of the media source.

        Returns
        -------
        str
            The title of the movie, TV show, or other media source.
        """
        return self["media_title"]

    @property
    def media_type(self) -> str:
        """
        Get the type of media source.

        Returns
        -------
        str
            The type of media (e.g., "movie", "TV show", "video game").
        """
        return self["media_type"]

    @property
    def year(self) -> int:
        """
        Get the release year of the media.

        Returns
        -------
        int
            The year the media was released.
        """
        return self["year"]

    def _convert_quote_lines(self, quote_dict):
        lines = quote_dict["lines"]
        converted_lines = []
        for line_dict in lines:
            character = list(line_dict.keys())[0]
            line_text = line_dict[character]
            mq_line = MQuoteLine(character, line_text)
            converted_lines.append(mq_line)
        quote_dict["lines"] = converted_lines
        return quote_dict

    def __str__(self):
        """
        Generate a string representation of the quote.

        Returns
        -------
        str
            A formatted string containing the quote's lines and characters.
        """
        lines = []
        for line_obj in self.lines:
            line = str(line_obj)
            lines.append(line)
        _str = "\n".join(lines)
        return _str
