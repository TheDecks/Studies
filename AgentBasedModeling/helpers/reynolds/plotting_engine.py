import os
from typing import Tuple

import matplotlib.pyplot as plt

import imageio as iio


class PlottingEngine:

    _images_created_counter: int

    def __init__(self, grid_length: float, fig_size: Tuple[float, float] = (6, 8), out_directory: str = 'Results'):
        """Create plotting object that handles clearing, saving and animating.

        :param grid_length: x and y limits.
        :param fig_size: size of figure.
        :param out_directory: saving directory.
        """
        self.grid_length = grid_length
        self.figure = plt.figure(figsize=fig_size)
        self.axis = self.figure.add_subplot()
        self.axis.set_xlim(0, self.grid_length)
        self.axis.set_ylim(0, self.grid_length)
        self._images_created_counter = 0
        self._out_directory = out_directory
        self.font_size = fig_size[1] * self.figure.dpi // 80
        self._images_file_paths = []

    def handle_out_directory(self):
        """Create directory for saving."""
        tries = 1
        directory_template = self._out_directory + '_{no_try}'
        while True:
            try:
                os.mkdir(self._out_directory)
                break
            except FileExistsError:
                self._out_directory = directory_template.format(no_try=tries)
                tries += 1

    def remove_ticks(self):
        """Clear axes of ticks."""
        self.axis.set_xticks([])
        self.axis.set_yticks([])

    def reset(self):
        """Reset axis state."""
        self.axis.clear()
        self.axis.set_xlim(0, self.grid_length)
        self.axis.set_ylim(0, self.grid_length)

    def save(self):
        """Save single image."""
        self._images_created_counter += 1
        file_name = os.path.join(self._out_directory, '{num:0>5}.png'.format(num=self._images_created_counter))
        self.figure.savefig(file_name)
        self._images_file_paths.append(file_name)

    def animate(self, out_name: str = 'animation.gif', frame_duration=0.3):
        """Create animation from all saved images."""
        with iio.get_writer(os.path.join(self._out_directory, out_name), mode='I', duration=frame_duration) as w:
            for file in self._images_file_paths:
                w.append_data(iio.imread(file))
