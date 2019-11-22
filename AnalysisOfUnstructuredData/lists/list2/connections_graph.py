from typing import Tuple, Optional, List, Union, Dict

import networkx as nx
from matplotlib import collections as colls, pyplot as plt, text as text
from AnalysisOfUnstructuredData.lists.list2 import data_feeder as df
from AnalysisOfUnstructuredData.helpers.hsc import relation as rel, publisher as per
import itertools
import AnalysisOfUnstructuredData.helpers.mpld3 as mpld3


class ConnectionsGraph:

    _person_name: str
    _person_surname: str
    data_f: df.HSCDataScrapper
    sections_values_dict: Dict[str, float]
    publishers: Dict[int, per.Publisher]
    relations: Dict[Tuple[int, int], rel.PublisherRelation]
    pos: Dict[int, Tuple[float, float]]

    table_hint_css = """
    table
    {
      border-collapse: collapse;
    }
    th
    {
      background-color: #ffac33;
    }
    td
    {
      background-color: #feecd2;
    }
    table, th, td
    {
      font-family:Arial, Helvetica, sans-serif;
      border: 1px solid black;
      text-align: left;
    }
    """

    def __init__(
            self, restrictors: Union[str, List[str]] = 'research papers',
            single_person: Optional[Tuple[str, str]] = None, keep_non_hsc: bool = False
    ):
        self.graph = nx.Graph()
        self.also_check_others = keep_non_hsc
        self.person_to_check = single_person
        self.data_f = df.HSCDataScrapper()
        self.data_f.restrict_sections(restrictors)
        self.sections_values_dict = self.initialize_sections_values()
        self.publishers = {}
        self.relations = {}
        self.pos = {}

    @staticmethod
    def create_node_label(publisher: 'per.Publisher') -> str:
        lab = f"{publisher.name}. {'-'.join(publisher.surname)}: {publisher.publishing_power}"

        return lab

    @property
    def person_to_check(self):
        return f"{self._person_name}.{self._person_surname}"

    @person_to_check.setter
    def person_to_check(self, set_val:  Optional[Tuple[str, str]]):
        if set_val is None:
            self._person_name = ''
            self._person_surname = ''
        else:
            self._person_name = set_val[0].strip()[:1].upper()
            self._person_surname = set_val[1].strip().lower().capitalize()

    def initialize_sections_values(self) -> Dict[str, float]:
        return {el: 1 for el in self.data_f.h2s}

    def update_section_publish_value(self, section: str, value: float):
        section = section.upper().strip()
        if value < 0:
            raise ValueError("Publishing anything shouldn't be penalized.")
        if section not in self.sections_values_dict.keys():
            raise KeyError('No section {}. Maybe it got restricted earlier?'.format(section))
        else:
            self.sections_values_dict[section] = value

    def create_publishers_and_relations(self):
        data_entries = self.data_f.source_entries_split()
        data_entries.reverse()
        for entry in data_entries:
            section, hsc_authors, other_authors, title = entry
            section_value = self.sections_values_dict[section]
            if self.person_to_check in map(lambda x: x.replace(' ', ''), hsc_authors + other_authors) \
                    or self.person_to_check == '.':
                publishers = self._get_involved_publishers(hsc_authors)
                if self.also_check_others:
                    publishers.extend(self._get_involved_publishers(other_authors, is_other=True))
                links = self._get_links_of_publishers(publishers)
                for p in publishers:
                    p.publishing_power += section_value
                for l in links:
                    l.add_publication(section, title)

    def _get_involved_publishers(self, names: List[str], is_other: bool = False) -> List[per.Publisher]:
        involved = []
        for name_surnames in names:
            found = False
            for _, publisher in self.publishers.items():
                if publisher.check_person(name_surnames):
                    involved.append(publisher)
                    found = True
                    break
            if not found:
                name, sur = name_surnames.split('.')
                p = per.Publisher(name, sur, is_other)
                self.publishers[p.id] = p
                involved.append(p)
        return involved

    def _get_links_of_publishers(self, publishers: List[per.Publisher]):
        links = []
        publishers.sort(key=lambda x: x.id)
        all_pairs = itertools.combinations(publishers, 2)
        for p1, p2 in all_pairs:
            if (p1.id, p2.id) in self.relations.keys():
                links.append(self.relations[(p1.id, p2.id)])
            else:
                lnk = rel.PublisherRelation(p1, p2)
                self.relations[(p1.id, p2.id)] = lnk
                links.append(lnk)
        return links

    def setup_nodes(self):
        for p_id, publisher in self.publishers.items():
            if publisher.is_other:
                color = 'blue'
            else:
                color = 'red'
            self.graph.add_node(
                p_id, size=publisher.publishing_power,
                color=color, label=ConnectionsGraph.create_node_label(publisher)
            )

    def setup_edges(self):
        for l_id, link in self.relations.items():
            self.graph.add_edge(l_id[0], l_id[1], weight=link.times_linked)

    def draw_graph(self):
        self.pos = nx.spring_layout(
            self.graph, k=24/(len(self.graph.nodes)**(1/2)),
            iterations=100, weight=None, scale=5
        )
        fig = plt.figure()
        ax = fig.add_subplot()
        nodes = self.graph.nodes
        edges = self.graph.edges
        self._draw_nodes(ax, nodes)
        self._draw_edges(ax, edges)
        nodes_handles, weight_labels_handles = ConnectionsGraph._retrieve_handles_for_html(ax)
        pt = self._get_nodes_plugin(nodes, nodes_handles)
        ptt = self._get_edges_plugin(edges, weight_labels_handles)
        mpld3.plugins.connect(fig, pt, ptt)
        mpld3.show(fig)

    def _draw_nodes(self, ax: plt.Axes, nodes: nx.classes.reportviews.NodeView):
        color = nx.get_node_attributes(self.graph, 'color')
        size = nx.get_node_attributes(self.graph, 'size')
        sizes = [size[n] for n in nodes]
        colors = [color[n] for n in nodes]
        nx.draw_networkx_nodes(self.graph, nodelist=nodes, pos=self.pos, ax=ax, node_color=colors, node_size=sizes)

    def _draw_edges(self, ax: plt.Axes, edges: nx.classes.reportviews.EdgeView):
        weight = nx.get_edge_attributes(self.graph, 'weight')
        weights = [weight[l] for l in edges]
        m_w = max(weights)
        widths = [w / m_w * 1.5 for w in weights]
        nx.draw_networkx_edges(self.graph, edgelist=edges, pos=self.pos, ax=ax, width=widths, arrows=False)
        nx.draw_networkx_edge_labels(self.graph, pos=self.pos, edge_labels=weight, font_size=8)

    @staticmethod
    def _retrieve_handles_for_html(ax: plt.Axes):
        nodes_collection = None
        all_text_collector = []
        for child in ax.get_children():
            if isinstance(child, colls.PathCollection):
                nodes_collection = child
            elif isinstance(child, text.Text):
                all_text_collector.append(child)
        _x = []
        _y = []
        for t in all_text_collector:
            x, y = t.get_position()
            _x.append(x)
            _y.append(y)
        weights_scatter = ax.scatter(_x, _y, alpha=0, s=5)
        return nodes_collection, weights_scatter

    def _get_nodes_plugin(self, nodes: nx.classes.reportviews.NodeView, handles):
        lab = nx.get_node_attributes(self.graph, 'label')
        labs = [lab[n] for n in nodes]
        return mpld3.plugins.PointLabelTooltip(handles, labels=labs)

    def _get_edges_plugin(self, edges: nx.classes.reportviews.EdgeView, handles):
        labs = [self.relations[tuple(sorted(l))].html_label() for l in edges]
        return mpld3.plugins.PointHTMLTooltip(handles, labels=labs, css=ConnectionsGraph.table_hint_css)


if __name__ == '__main__':
    # cg = ConnectionsGraph(single_person=('A', 'Wylomanska'))
    cg = ConnectionsGraph(restrictors=['research papers', 'books'])
    cg.create_publishers_and_relations()
    cg.setup_edges()
    cg.setup_nodes()
    cg.draw_graph()
