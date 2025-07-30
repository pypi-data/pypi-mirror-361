import pickle
from pathlib import Path
from gzip import GzipFile
from dataclasses import asdict
from typing import Optional, Callable

from pickart.errors import BadPickartFile, BadPixelFormat
from pickart.colour import Colour
from pickart.constatnts import PICKART_VERSON, strOrPath
from pickart.colour_formats import ColourFormats
from pickart.pickart_file_data import PickartFileData
from pickart.restricted_unpickler import load


def set_stdo(new_stdo: Callable):
    """Set new global stdo for Pickart files. `stdo` is used as standart output for errors that happend during file loading.

    Args:
        new_stdo (Callable): function with one positional argument. This argument is string with error message.

    Raises:
        ValueError: if argument `new_stdo` is not callable.
    """

    if not callable(new_stdo):
        raise ValueError(f"'new_stdo' must be callable.")
    PickartFile._STDO = new_stdo


class PickartFile:
    _STDO = print

    def __init__(
        self,
        filepath: Optional[strOrPath] = None,
        file_data: Optional[PickartFileData] = None,
        stdo: Optional[Callable] = None,
    ):
        """Load Pickart file. If file does not exist or is not Pickart format exception `will not` be raised to check if loading was successful use `valid` attribute.

        Args:
            filepath (Optional[strOrPath]): path to .pickart file.
            file_data (Optional[PickartFileData]): file data. Note if `filepath` is passed this argument will be ignored.
            stdo (Callable): function which will be called when error occur during file loading. Defaults to `print`. Can be changed via this argument, or globaly(for all Pickart instances) with set_stdo function.
        Raises:
            ValueError: if `filepath` or `file_data` has wrong type.
        """

        self.stdo = PickartFile._STDO
        if stdo is not None:
            self.stdo = stdo
        self._data = PickartFileData()
        self.filepath = None
        self.errors = []

        if file_data is not None:
            if not isinstance(file_data, PickartFileData):
                raise ValueError(
                    f"'file_data' must be pickart.PickartFileData type, not: {type(file_data)}."
                )
            self._data = file_data

        self._colour_palette: dict[int, Colour] = {}
        self.valid = False

        if filepath is not None:
            if not isinstance(filepath, (str, Path)):
                raise ValueError(
                    f"'filepath' must be str or pathlib.Path type, not: {type(filepath)}."
                )
            self.filepath = Path(filepath)
            self.load()

    def _load_file(self):
        try:
            with GzipFile(self.filepath) as file:
                self._data = PickartFileData(**load(file))
                version: int = self._data.info.get("version", -1)
                if version != PICKART_VERSON:
                    raise BadPickartFile(f"File version: '{version}' is not supported.")
                if any(i <= 0 for i in self._data.info.get("size", (0, 0))):
                    raise BadPickartFile("Art size must be positive")

                self.fmt = ColourFormats(len(self._data.palette[0]))
                self.valid = True
        except Exception as error:
            self.errors.append(error)
            self.stdo(f"Cannot load file '{self.filepath}', error: {error}.")

    def load(self, filepath: Optional[strOrPath] = None):
        """Load file from filepath.

        Args:
            filepath (Optional[strOrPath]): new filepath, will override existing filepath.

        Raises:
            ValueError: if `filepath` has wrong type.
        """

        if filepath is not None:
            if not isinstance(filepath, (str, Path)):
                raise ValueError(
                    f"'filepath' must be str or pathlib.Path type, not: {type(filepath)}."
                )
            self.filepath = filepath

        self._load_file()

        if not self.valid:
            return

        for key, colour in enumerate(self._data.palette):
            if not Colour.check_colour(colour, self.fmt):
                self.valid = False
                error_msg = f"Bad pixel format in file: '{self.filepath}'."
                self.errors.append(BadPixelFormat(error_msg))
                self.stdo(error_msg)
                break

            self._colour_palette[key] = Colour(colour)

    def set_painted(self, x: int, y: int, colour_index: int) -> bool:
        """Paint pixel at `x`, `y` if `colour_index` is the same. Return `False` if pixel is already painted or `colour_index` is different, else return `True`."""

        if self._data.pixels[y][x][0] != colour_index or self._data.pixels[y][x][1]:
            return False
        self._data.pixels[y][x][1] = True
        return True

    def get_pixels(self) -> list[list]:
        return self._data.pixels

    def get_size(self) -> tuple[int, int]:
        return self._data.info["size"]

    def get_palette(self):
        return self._colour_palette

    def save(self, filepath: Optional[strOrPath] = None):
        """Save file to filepath.

        Args:
            filepath (Optional[strOrPath]): new filepath will, override existing filepath.

        Raises:
            ValueError: if `filepath` has wrong type.
        """

        if filepath is not None:
            if not isinstance(filepath, (str, Path)):
                raise ValueError(
                    f"'filepath' must be str or pathlib.Path type, not: {type(filepath)}."
                )
            self.filepath = filepath
        with GzipFile(self.filepath, "w") as file:
            pickle.dump(asdict(self._data), file)
        self.valid = True

    def __repr__(self) -> str:
        filepath = self.filepath
        if filepath is not None:
            filepath = str(filepath)

        valid = self.valid
        size = None
        if valid:
            size = self.get_size()
        return f"PickartFile({filepath=}, {size=}, {valid=})"
