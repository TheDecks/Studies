import os
import time
from typing import Tuple, Iterable, Dict, Set

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as grd
import AgentBasedModeling.common.log.logger as log
import imageio as iio

LOGGER = log.get_logger(__name__)


class SquareLatticePlotter:

    rectangles: Dict[Tuple[int, int], patches.Rectangle]
    _temporary_rectangles: Set[patches.Rectangle]
    _images_created_counter: int

    def __init__(self, grid_length: int, fig_size: Tuple[float, float], out_directory: 'str'):
        self.grid_length = grid_length
        self.figure = plt.figure(figsize=fig_size)
        self.grid = grd.GridSpec(2, 3)
        self.base_axis = self.figure.add_subplot(self.grid[0:2, 0:2])
        self.rectangles = {}
        self._temporary_rectangles = set()
        self._images_created_counter = 0
        self._out_directory = out_directory
        self.font_size = fig_size[1] * self.figure.dpi // 80
        self._images_file_paths = []

    def handle_out_directory(self):
        tries = 1
        directory_template = self._out_directory + '_{no_try}'
        while True:
            try:
                os.mkdir(self._out_directory)
                break
            except FileExistsError:
                LOGGER.info(
                    'Creation of {dir_name} directory failed. Trying further...'.format(dir_name=self._out_directory)
                )
                self._out_directory = directory_template.format(no_try=tries)
                tries += 1

    def create_checker_board(self):
        self.base_axis.set_xlim([-0.5, self.grid_length - 0.5])
        self.base_axis.set_ylim([-0.5, self.grid_length - 0.5])
        self.base_axis.hlines(
            [level - 0.5 for level in range(self.grid_length)],
            xmin=-0.5, xmax=self.grid_length + 0.5, color='k', lw=0.5
        )
        self.base_axis.vlines(
            [level - 0.5 for level in range(self.grid_length)],
            ymin=-0.5, ymax=self.grid_length + 0.5, color='k', lw=0.5
        )

    def remove_ticks(self):
        self.base_axis.set_xticks([])
        self.base_axis.set_yticks([])

    def add_permanent_rectangles(self, coords: Iterable[Tuple[int, int]]):
        for x, y in coords:
            self.rectangles[(x, y)] = patches.Rectangle(
                (x - 0.5, y - 0.5), 1, 1, fill=True
            )
            self.base_axis.add_patch(self.rectangles[(x, y)])

    def add_temporary_rectangles(
            self, coords: Iterable[Tuple[int, int]], size: Tuple[int, int], color: str, alpha: float
    ):
        for x, y in coords:
            x_off, y_off = size
            tmp = patches.Rectangle(
                (x - x_off/2, y - y_off/2), x_off, y_off, fill=True, color=color, alpha=alpha
            )
            self._temporary_rectangles.add(tmp)
            self.base_axis.add_patch(tmp)

    def clear_main_axes(self):
        self.base_axis.patches = [patch for _, patch in self.rectangles.items()]
        self._temporary_rectangles = set()

    def colour_rectangles(self, coords: Iterable[Tuple[int, int]], color: str):
        for x, y in coords:
            self.rectangles[(x, y)].set_color(color)

    def save(self):
        self.figure.canvas.draw()
        self._images_created_counter += 1
        file_name = os.path.join(self._out_directory, '{num:0>5}.png'.format(num=self._images_created_counter))
        self.figure.savefig(file_name)
        self._images_file_paths.append(file_name)

    def animate(self, out_name: str = 'animation.gif', frame_duration=0.8):
        with iio.get_writer(os.path.join(self._out_directory, out_name), mode='I', duration=frame_duration) as w:
            for file in self._images_file_paths:
                w.append_data(iio.imread(file))


if __name__ == '__main__':
    pass
