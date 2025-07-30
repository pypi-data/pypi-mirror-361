import pickle
from gzip import GzipFile
from typing import Any, BinaryIO, Union


class RestrictedUnpickler(pickle.Unpickler):
    """
    This class is more secure way to load pickle files.

    See: https://docs.python.org/3/library/pickle.html#restricting-globals
    """

    def find_class(self, module, name):
        raise pickle.UnpicklingError(
            "File contains external object(this is forbidden)."
        )


def load(file_obj: Union[BinaryIO, GzipFile]) -> Any:
    """Restricted version of `pickle.load()`

    Args:
        file_obj (Union[BinaryIO, GzipFile]): object must have two methods read(size: int) and readlines(). Both should return bytes.

    Returns:
        deserialized file data(any built-in object that is not imported).
    """

    return RestrictedUnpickler(file_obj).load()
