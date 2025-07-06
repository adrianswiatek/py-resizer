#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from pathlib import Path
from PIL import Image, ImageFile


class Arguments:
    def __init__(self, args: Namespace):
        self.input_paths = map(lambda x: Path(x), args.filepaths)
        self.scale = args.percent

        if args.destination.startswith('~/'):
            self.destination_path = Path.home() / Path(args.destination[2:])
        else:
            self.destination_path = Path(args.destination)

    def is_scale_valid(self) -> bool:
        return 0 < self.scale < 100


class ImageData:
    def __init__(self, image: ImageFile.ImageFile):
        path = Path(image.filename)
        self.name = path.stem
        self.extension = path.suffix
        self.size_in_bytes = path.stat().st_size
        self.dimensions = Dimensions(width=image.size[0], height=image.size[1])
        self.format = image.format


class Dimensions:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return f'Dimensions: {self.width}x{self.height}'

    def resize(self, percent_value: int):
        if 0 < percent_value < 100:
            value = percent_value / 100
            return Dimensions(
                width=int(self.width * value),
                height=int(self.height * value)
            )
        else:
            return self

    def as_tuple(self):
        return self.width, self.height


def parse_args() -> Arguments:
    parser = ArgumentParser(prog='py-resizer', description='A simple image resizer.')

    filepaths_help = 'A list of paths to images'
    parser.add_argument('filepaths', nargs='+', help=filepaths_help)

    percent_help = 'Proportional change in image size in percentage'
    parser.add_argument('-p', '--percent', type=int, help=percent_help, required=True)

    destination_help = 'A path to the directory with resized images'
    parser.add_argument('-d', '--destination', type=str, default='~/Desktop/Resized Images/', help=destination_help)

    return Arguments(parser.parse_args())


def execute(in_filepath: Path, scale: int, out_directory: Path):
    try:
        with Image.open(in_filepath) as in_image:
            in_image_data = ImageData(in_image)

            if not out_directory.exists():
                out_directory.mkdir(parents=True, exist_ok=True)

            out_path = out_directory / f'{in_image_data.name}_resized{in_image_data.extension}'

            if not out_path.exists():
                out_path.touch()

            out_dimensions = in_image_data.dimensions.resize(scale)
            in_image.resize(out_dimensions.as_tuple()).save(out_path)

    except OSError as error:
        print(f'ERROR: {error}')


if __name__ == '__main__':
    arguments = parse_args()

    if not arguments.is_scale_valid():
        print('Invalid scale. Value should be between 1 and 99')
        exit(1)

    for input_path in arguments.input_paths:
        execute(input_path, arguments.scale, arguments.destination_path)
