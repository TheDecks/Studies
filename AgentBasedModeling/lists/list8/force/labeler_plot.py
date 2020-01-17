from typing import Dict, Union, List, Tuple
import matplotlib.pyplot as plt


def labeler_plot_2(
        data_set_1: Dict[Union[str, float], List[float]],
        data_set_2: Dict[Union[str, float], List[float]],
        labeler: str
) -> Tuple[plt.Figure, plt.Axes]:
    fig = plt.figure()
    ax = fig.add_subplot()

    for label_value, adoption_rate in data_set_1.items():
        ax.plot(adoption_rate, label=f'{labeler}={label_value}')

    ax.set_prop_cycle(None)

    ax.legend()

    for label_value, adoption_rate in data_set_2.items():
        ax.plot(adoption_rate, ':', label=f'{labeler}={label_value}')

    ax.set_xlabel('time')
    ax.set_ylabel('adopters')

    return fig, ax
