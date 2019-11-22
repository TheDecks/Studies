from typing import Tuple, Iterable, Union

import AgentBasedModeling.common.shared_cls.square_lat_plt as slp
from AgentBasedModeling.helpers.schellings import cell
from matplotlib import cm


class PlottingEngine(slp.SquareLatticePlotter):

    def __init__(
            self,
            grid_length: int,
            groups_count: int,
            fig_size: Tuple[float, float] = (11.5, 8),
            out_directory: str = 'Results'
    ):
        super().__init__(grid_length, fig_size, out_directory)
        self.number_groups = groups_count
        self.colours = cm.get_cmap('tab10')(range(self.number_groups))
        self.figure.set_dpi(50)

    def prepare(self, happiness_thresholds: Iterable[int], max_neighbours: int):
        self.handle_out_directory()
        self.create_checker_board()
        self.remove_ticks()
        self.base_axis.set_title("Schelling's model", fontsize=self.font_size)
        self._prepare_happiness_base(happiness_thresholds, max_neighbours)
        self.create_all_rectangles()

    def _prepare_happiness_base(self, happiness_thresholds: Iterable[int], max_neighbours: int):
        _happiness_axes = self.figure.add_subplot(self.grid[0:2, 2])
        _happiness_axes.set_xticks([])
        _happiness_axes.set_yticks([])
        _happiness_axes.axis('off')
        _happiness_axes.bar(
            range(self.number_groups),
            [th / max_neighbours for th in happiness_thresholds],
            width=1, color=self.colours
        )
        _happiness_axes.set_xlim([-0.5, self.number_groups - 0.5])
        _happiness_axes.set_ylim([0, 1.1])
        _happiness_axes.set_title(f'{max_neighbours} neighbours', fontsize=self.font_size)
        _happiness_axes.axhline(y=1, xmin=0, xmax=1, fillstyle='full', color='grey', linewidth=0.5)

    def create_all_rectangles(self):
        self.add_permanent_rectangles([(x, y) for x in range(self.grid_length) for y in range(self.grid_length)])

    def draw_empties(self, empties_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(empties_coords), 'white')

    def draw_groups(self, groups: Iterable[Iterable[Union[Tuple[int, int], 'cell.Cell']]]):
        for i, group_coords in enumerate(groups):
            self.colour_rectangles(PlottingEngine.translate_iterable(group_coords), self.colours[i])

    @staticmethod
    def translate_iterable(any_iter: Iterable[Union[Tuple[int, int], 'cell.Cell']]) -> Iterable[Tuple[int, int]]:
        return set(map(lambda coord: coord.position if isinstance(coord, cell.Cell) else coord, any_iter))

    @staticmethod
    def get_colours_sequence(no_colours: int):
        return cm.get_cmap('tab10')(range(no_colours))


if __name__ == '__main__':
    pe = PlottingEngine(1, 1, out_directory='Results_2')
    pe._images_file_paths = [
        slp.os.path.join('Results_2', '{num:0>5}.png'.format(num=i)) for i in range(1, 501)
    ]
    pe.animate()
