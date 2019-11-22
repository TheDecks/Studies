from typing import Union, Tuple, Iterable, Set

import AgentBasedModeling.common.shared_cls.square_lat_plt as slp
import AgentBasedModeling.helpers.game_of_life.cell as cell


class PlottingEngine(slp.SquareLatticePlotter):

    _size: Tuple[int, int]

    def __init__(
            self, dims: Union[int, Tuple[int, int]],
            fig_size: Tuple[float, float] = (11.5, 8),
            out_directory: str = 'Results'
    ):
        self.size = dims
        super().__init__(dims[0], fig_size, out_directory)

    def prepare(self, neighbours_shifts: Iterable[Tuple[int, int]], portals: Set[int]):
        self.handle_out_directory()
        self.create_checker_board()
        self.remove_ticks()
        self.base_axis.set_title('Game Of Life', fontsize=self.font_size)
        self._draw_neighbourhood(neighbours=neighbours_shifts, portals=portals)
        self._create_legend()
        self.initialize_all_rectangles()

    def _draw_neighbourhood(self, neighbours: Iterable[Tuple[int, int]], portals: Set[int]):
        x, y = zip(*neighbours)
        neighbour_axes = self.figure.add_subplot(self.grid[0, 2])
        neighbour_axes.set_xticks([])
        neighbour_axes.set_yticks([])
        if max(x) - min(x) >= max(y) - min(y):
            low = min(x) - 1
            high = max(x) + 1
        else:
            low = min(y) - 1
            high = max(y) + 1
        neighbour_axes.set_xlim([low, high])
        neighbour_axes.set_ylim([low, high])
        neighbour_axes.set_title('Neighbourhood', fontsize=self.font_size)
        neighbour_axes.axis('off')
        for _x, _y in neighbours:
            neighbour_axes.add_patch(slp.patches.Rectangle(
                (_x - 0.5, _y - 0.5), 1, 1, fill=True, color='blue'
            ))
        neighbour_axes.add_patch(slp.patches.Rectangle((-0.5, -0.5), 1, 1, fill=True, color='yellow'))
        if 1 in portals:
            neighbour_axes.add_patch(slp.patches.Rectangle(
                (low, low), high - low, 0.5, facecolor='red', edgecolor='none', alpha=0.2
            ))
        if 2 in portals:
            neighbour_axes.add_patch(slp.patches.Rectangle(
                (low, high - 0.5), high - low, 0.5, facecolor='red', edgecolor='none', alpha=0.2
            ))
        if 3 in portals:
            neighbour_axes.add_patch(slp.patches.Rectangle(
                (low, low), 0.5, high - low, facecolor='red', edgecolor='none', alpha=0.2
            ))
        if 4 in portals:
            neighbour_axes.add_patch(slp.patches.Rectangle(
                (high - 0.5, low), 0.5, high - low, facecolor='red', edgecolor='none', alpha=0.2
            ))

    def _create_legend(self):
        temp_axes = self.figure.add_subplot(self.grid[1, 2])
        temp_axes.axis('off')
        custom_patches = [
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='black', linewidth=0.3),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='grey', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='yellow', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='blue', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='none', alpha=0.2)
        ]
        temp_axes.legend(
            custom_patches,
            ('Dead', 'Alive', 'Middle cell', 'Neighbours', 'Portals'),
            fontsize=self.font_size
        )


    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, set_val: Union[int, Tuple[int, int]]):
        if isinstance(set_val, int):
            self._size = (set_val, set_val)
        else:
            self._size = set_val

    def create_checker_board(self):
        height, width = self.size
        self.base_axis.set_xlim([-0.5, width - 0.5])
        self.base_axis.set_ylim([-0.5, height - 0.5])
        self.base_axis.hlines(
            [level - 0.5 for level in range(height)],
            xmin=-0.5, xmax=width + 0.5, color='k', lw=0.5
        )
        self.base_axis.vlines(
            [level - 0.5 for level in range(width)],
            ymin=-0.5, ymax=height + 0.5, color='k', lw=0.5
        )

    def initialize_all_rectangles(self):
        height, width = self.size
        self.add_permanent_rectangles([(x, y) for x in range(width) for y in range(height)])

    def draw_alive(self, alive_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(alive_coords), 'grey')

    def draw_dead(self, dead_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(dead_coords), 'white')

    @staticmethod
    def translate_iterable(any_iter: Iterable[Union[Tuple[int, int], 'cell.Cell']]) -> Iterable[Tuple[int, int]]:
        return set(map(lambda coord: coord.position if isinstance(coord, cell.Cell) else coord, any_iter))

    def loop_n_last_pictures(self, n: int = 1, times: int = 1):
        pictures_subset = self._images_file_paths[-n:]
        self._images_file_paths.extend(pictures_subset * times)

    def animate(self, out_name: str = 'animation.gif', frame_duration=0.6):
        super().animate(out_name, frame_duration)
