from typing import Tuple, Iterable, Union

import AgentBasedModeling.common.shared_cls.square_lat_plt as slp
from AgentBasedModeling.helpers.burning import wind
from AgentBasedModeling.helpers.burning import cell


class PlottingEngine(slp.SquareLatticePlotter):

    def __init__(self, grid_length: int, fig_size: Tuple[float, float], out_directory: 'str'):
        super().__init__(grid_length, fig_size, out_directory)
        self.wind_axes = self.figure.add_subplot(self.grid[0, 2])

    def prepare(self, prob: float):
        self.handle_out_directory()
        self.create_checker_board()
        self.remove_ticks()
        self.base_axis.set_title('Simulation grid with p={:.2f}'.format(prob), fontsize=self.font_size)
        self._prepare_wind_base()
        self._create_legend()

    def _prepare_wind_base(self):
        self.wind_axes.set_xticks([])
        self.wind_axes.set_yticks([])
        self.wind_axes.add_patch(slp.plt.Circle((0, 0), 1, facecolor='none', edgecolor='grey'))
        self.wind_axes.set_xlim([-1, 1])
        self.wind_axes.set_ylim([-1, 1])
        self.wind_axes.set_title('Wind', fontsize= self.font_size)
        self.wind_axes.axis('off')
        self.wind_axes.axhline(y=0, xmin=0, xmax=0.05, fillstyle='full', color='grey', linewidth=0.5)
        self.wind_axes.axhline(y=0, xmin=0.95, xmax=1, fillstyle='full', color='grey', linewidth=0.5)
        self.wind_axes.axvline(x=0, ymin=0, ymax=0.05, fillstyle='full', color='grey', linewidth=0.5)
        self.wind_axes.axvline(x=0, ymin=0.95, ymax=1, fillstyle='full', color='grey', linewidth=0.5)
        self.wind_axes.plot(0, 0, color='black', marker='.', markersize=0.5)

    def _create_legend(self):
        temp_axes = self.figure.add_subplot(self.grid[1, 2])
        temp_axes.axis('off')
        custom_patches = [
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='black', linewidth=0.3),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='green', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='brown', edgecolor='none'),
            slp.patches.Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='none', alpha=0.2)
        ]
        temp_axes.legend(custom_patches, ('Empty', 'Tree', 'Burning', 'Burned', 'Fire range'), fontsize=self.font_size)

    def initialize_trees_places(self, non_empty_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.add_permanent_rectangles(coords=PlottingEngine.translate_iterable(non_empty_coords))

    def draw_trees(self, trees_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(trees_coords), 'green')

    def draw_burning(self, burning_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(burning_coords), 'red')

    def draw_burned(self, burned_coords: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.colour_rectangles(PlottingEngine.translate_iterable(burned_coords), 'brown')

    def draw_fire_propagation_range(self, ignition_centers: Iterable[Union[Tuple[int, int], 'cell.Cell']]):
        self.add_temporary_rectangles(PlottingEngine.translate_iterable(ignition_centers), (3, 3), 'red', 0.2)

    def draw_wind_arrow(self):
        dx, dy = wind.Wind().get_wind_propagation_center()
        w_power = wind.Wind().power
        [p.remove() for p in self.wind_axes.patches if isinstance(p, slp.patches.FancyArrow)]
        self.wind_axes.add_patch(slp.patches.FancyArrow(
            0, 0, dx, dy,
            edgecolor='black', facecolor=(1, 0, 0), alpha=wind.Wind().power,
            overhang=0.1 * w_power, width=0.08 + 0.12 * w_power, length_includes_head=True,
            head_width=0.2 + 0.3 * w_power, head_length=0.25 + 0.35 * w_power
        ))

    @staticmethod
    def translate_iterable(any_iter: Iterable[Union[Tuple[int, int], 'cell.Cell']]) -> Iterable[Tuple[int, int]]:
        return set(map(lambda coord: coord.position if isinstance(coord, cell.Cell) else coord, any_iter))
