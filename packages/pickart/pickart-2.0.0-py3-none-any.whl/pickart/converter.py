import struct
from io import BytesIO
from pathlib import Path
from typing import Optional

import pygame

from pickart import PickartFile, PickartFileData
from pickart.constatnts import PICKART_VERSON, strOrPath


def convert_to_png(
    filename: strOrPath, output_dir: strOrPath, output_file_name: Optional[str] = None
):
    """Convert `.pickart` file to `.png`.

    Args:
        filename (strOrPath): `.pickart` file path.
        output_dir (strOrPath): folder where converted file will be saved. If it does not exist it will be created.
        output_file_name (Optional[str]): name for converted file, `.png` extension will be added if needed.

    Raises:
        ValueError: if `.pickart` file is invalid.
    """

    filename = Path(filename)
    output_dir = Path(output_dir)

    if output_file_name is None:
        output_file_name = f"{filename.stem}.png"
    elif not output_file_name.endswith(".png"):
        output_file_name += ".png"

    file = PickartFile(filename)
    if not file.valid:
        raise ValueError(f"'{filename}' invalid Pickart file.")

    buffer = BytesIO()
    palette = file.get_palette()
    pixel_fmt = ">" + "B" * file.fmt.value

    for col in file.get_pixels():
        for colour_index, is_painted in col:
            if colour_index is None:
                buffer.write(struct.pack(pixel_fmt, 0, 0, 0, 0))
                continue

            colour = palette[colour_index]
            colour = colour.colour if is_painted else colour.grayscale
            buffer.write(struct.pack(pixel_fmt, *colour))
    surf = pygame.image.frombuffer(buffer.getbuffer(), file.get_size(), file.fmt.name)  # type: ignore

    output_filename = Path(output_dir, output_file_name)
    pygame.image.save(surf, output_filename)


def convert_to_pickart(
    filename: strOrPath, output_dir: strOrPath, converted_filename: Optional[str] = None
):
    """Convert `.png` file to `.pickart`.

    Args:
        filename (strOrPath): `.png` file path.
        output_dir (strOrPath): folder where converted file will be saved. If it does not exist it will be created.
        converted_filename (Optional[str]): name for converted file, `.pickart` extension will be added if needed.

    Raises:
        ValueError: if `filename` does not exist.
    """

    filename = Path(filename)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if converted_filename is None:
        converted_filename = f"{filename.stem}.pickart"
    elif not converted_filename.endswith(".pickart"):
        converted_filename += ".pickart"

    if not filename.is_file():
        raise ValueError(f"'{filename}' does not exist.")

    image = pygame.image.load(filename)
    file_data = BytesIO(image.get_buffer().raw)  # type: ignore

    byte_size = image.get_bytesize()
    pixel_fmt = ">" + "B" * byte_size

    width, height = image.get_size()

    pixels = []
    palette = {}

    header = {
        "size": (width, height),
        "version": PICKART_VERSON,
    }

    for _ in range(height):
        row = []
        for _ in range(width):
            colour = struct.unpack_from(pixel_fmt, file_data.read(byte_size))
            if byte_size == 4 and colour[3] == 0:  # Transparent pixel
                row.append([None, False])
                continue

            if colour not in palette:
                palette[colour] = len(palette)

            colour_index = palette[colour]
            row.append([colour_index, False])

        pixels.append(row)

    result = PickartFileData(header, list(palette.keys()), pixels)
    output_filename = Path(output_dir, converted_filename)

    file = PickartFile(file_data=result)
    file.save(output_filename)
