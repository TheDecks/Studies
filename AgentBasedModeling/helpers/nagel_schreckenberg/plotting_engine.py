import os
import time
from typing import Tuple, Iterable, Dict, Set

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as grd
import AgentBasedModeling.common.log.logger as log
import imageio as iio

LOGGER = log.get_logger(__name__)


class PlottingEngine:

    def __init__(self, number_of_lanes: int, r: float, out_directory: 'str' = 'Results'):
        self.first_r = r
        self.n = number_of_lanes
        self.figure = plt.figure(figsize=(11.5, 8))
        self.grid = grd.GridSpec(1, 2)
        self.base_axis = self.figure.add_subplot(self.grid[0, 0])
        self.velocity_axis = self.figure.add_subplot(self.grid[0, 1])
        self.circles = set()
        self.base_patches = []
        self._images_created_counter = 0
        self._out_directory = out_directory
        self.font_size = 8 * self.figure.dpi // 80
        self._images_file_paths = []
        self.velocities = []

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

    def setup_base_axes(self):
        # self.base_axis.set_xticks([])
        # self.base_axis.set_yticks([])
        for i in range(self.n):
            c = plt.Circle((0, 0), self.first_r+i, facecolor='none', edgecolor='grey')
            self.base_axis.add_patch(c)
            self.base_patches.append(c)
        self.base_axis.set_xlim([-self.first_r - self.n, self.first_r + self.n])
        self.base_axis.set_ylim([-self.first_r - self.n, self.first_r + self.n])

    def setup_velocity_axes(self):
        self.velocity_axis.set_xlabel('time')
        self.velocity_axis.set_ylabel('V')

    def clear_main_axes(self):
        self.base_axis.patches = []
        for ptch in self.base_patches:
            self.base_axis.add_patch(ptch)
        self.base_axis.texts = []
        self.circles = set()

    def draw_circle(self, coords: Tuple[int, int], label: str, color: str, alpha: float):
        crcle = plt.Circle(coords, 0.5, facecolor=color, edgecolor=color, alpha=alpha)
        self.base_axis.add_patch(crcle)
        self.base_axis.text(*coords, label, horizontalalignment='center', verticalalignment='center')

    def process_velocity_axes(self, new_veloc: float):
        self.velocities.append(new_veloc)
        self.velocity_axis.clear()
        self.velocity_axis.plot(self.velocities)

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

