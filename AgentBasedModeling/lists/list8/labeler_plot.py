from typing import Dict, Union, List, Tuple
import matplotlib.pyplot as plt


def labeler_plot(data_set: Dict[Union[str, float], List[float]], labeler: str) -> Tuple[plt.Figure, plt.Axes]:
    fig = plt.figure()
    ax = fig.add_subplot()

    for label_value, adoption_rate in data_set.items():
        ax.plot(adoption_rate, label=f'{labeler}={label_value}')

    ax.legend()

    ax.set_xlabel('time')
    ax.set_ylabel('adoption rate')

    return fig, ax
