from typing import List, Union, Tuple

from AnalysisOfUnstructuredData.helpers.hsc.namespaces import HSCNamespace as hscnm
from bs4 import BeautifulSoup
import urllib.request
import re


class HSCDataScrapper:

    def __init__(self, url: str = hscnm.publications_html):
        _resp = urllib.request.urlopen(url)
        _html_text = _resp.read()
        self.soup = BeautifulSoup(_html_text, "html.parser")
        self.h2s = [el.text.replace(':', '').strip().upper() for el in self.soup.find_all(['h2'])]

    def restrict_sections(self, by: Union[str, List[str]]):
        if isinstance(by, str):
            by = [by]
        self.h2s = list(map(lambda x: x.strip().upper(), by))

    def source_entries_split(self) -> List[Tuple[str, List[str], List[str], str]]:
        all_entries = []
        for section, contents in self._get_source_entries_list():
            contents = contents.replace('\r\n', ' ')
            hsc_professors = re.findall(
                '<font .*?><[bB]>([A-Z][a-z]?[.][ ]?[A-Z][-a-zA-Z]*?)[ ]?</[bB]></font>', contents
            )
            others = re.findall('<font .*?>([A-Z][a-z]?[.][ ]?[A-Z][a-z]*?)[ ]?</font>', contents)
            title = re.search('<.*?><.*?>(".*?")<.*?><.*?>', contents).group(1)
            all_entries.append((section, hsc_professors, others, title))
        return all_entries

    def _get_source_entries_list(self):
        section = None
        for node in self.soup.findAll(['h2', 'li']):

            if node.name == 'h2':
                section_name = node.text.replace(':', '').strip().upper()
                if section_name in self.h2s:
                    section = section_name
                else:
                    section = None
            elif section is not None:
                yield section, str(node).translate({
                    ord('ą'): 'a', ord('ć'): 'c', ord('ę'): 'e', ord('ł'): 'l', ord('ń'): 'n',
                    ord('ó'): 'o', ord('ś'): 's', ord('ż'): 'z', ord('ź'): 'z',
                    ord('Ą'): 'A', ord('Ć'): 'C', ord('Ę'): 'E', ord('Ł'): 'L', ord('Ń'): 'N',
                    ord('Ó'): 'O', ord('Ś'): 'S', ord('Ż'): 'Z', ord('Ź'): 'Z'
                })
