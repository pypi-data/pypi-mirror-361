from pickart.colour_formats import ColourFormats


class Colour:
    def __init__(self, colour: tuple[int, ...]):
        """Initialize colour.

        Args:
            colour (tuple[int, ...]): tuple with 3 or 4 integers that represent colour - r, g, b, a. Alpha is optional
        """

        self.colour: tuple[int, ...] = colour[:4]
        self.fmt = ColourFormats(len(self.colour))
        if self.fmt == ColourFormats.RGBA and self.colour[3] != 255:
            self.colour = (*self.colour[:3], 255)

        self._generate_grayscale()

    def _generate_grayscale(self):
        colour = sum(self.colour[:3]) // 3
        if colour == 0:
            colour = 10
        self.grayscale = (
            (colour, colour, colour, 255)
            if self.fmt == ColourFormats.RGBA
            else (colour, colour, colour)
        )

    @staticmethod
    def check_colour(colour: tuple[int, ...], fmt: ColourFormats) -> bool:
        return len(colour) == fmt.value and all(
            (c <= 255 and c >= 0 and isinstance(c, int) for c in colour)
        )

    def __repr__(self) -> str:
        colour = self.colour
        fmt = self.fmt.name
        return f"Colour({colour=},  {fmt=})"
