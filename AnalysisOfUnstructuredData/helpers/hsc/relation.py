from typing import Dict, Tuple

from AnalysisOfUnstructuredData.helpers.hsc.publisher import Publisher


class PublisherRelation:

    titles_types: Dict[str, str]
    _id: Tuple[int, int]

    def __init__(self, publisher_1: Publisher, publisher_2: Publisher):
        self.publisher_1 = publisher_1
        self.publisher_2 = publisher_2
        self.titles_types = {}
        self.id = (publisher_1.id, publisher_2.id)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, set_val: Tuple[int, int]):
        if set_val[0] > set_val[1]:
            self._id = (set_val[1], set_val[0])
        else:
            self._id = set_val

    def add_publication(self, publication_type: str, title: str):
        self.titles_types[title] = publication_type

    @property
    def times_linked(self):
        return len(self.titles_types)

    def __eq__(self, other: 'PublisherRelation'):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def html_label(self) -> str:
        lab = """{} publications of {}. {} and {}. {}.
<table border="1" class="dataframe">\n\t<thead>\n\t\t<tr style="text-align: left;">\n\t\t\t<th>Type</th>
\t\t\t<th>Title</th>\n\t\t</tr>\n\t</thead>\n\t<tbody>\n""".format(
            self.times_linked,
            self.publisher_1.name, '-'.join(self.publisher_1.surname),
            self.publisher_2.name, '-'.join(self.publisher_2.surname)
        )
        lab += '\n'.join(["\t\t<tr>\n\t\t\t<td>{}</td>\n\t\t\t<td>{}</td>\n\t\t</tr>".format(p_type, title)
                          for title, p_type in self.titles_types.items()])
        lab += '\n\t</tbody>\n</table>'
        return lab
