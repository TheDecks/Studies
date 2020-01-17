from typing import Dict, List
import matplotlib.pyplot as plt


def flexibility_probability_concentration_plot(data_set: Dict[float, Dict[str, List[float]]]) -> plt.Figure:

    fig = plt.figure()

    ax = fig.add_subplot()

    for flex, prob_con in data_set.items():
        ps = prob_con['p']
        cs = prob_con['concentration']
        ax.plot(ps, cs, '.', label=f"f={flex:.2f}")

    ax.legend()

    ax.set_xlabel('p')
    ax.set_ylabel('concentration')

    return fig
