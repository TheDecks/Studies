from bs4 import BeautifulSoup
import urllib.request

from AnalysisOfUnstructuredData.helpers.book import paragraph as par


class HTMLBook:

    def __init__(self, code: str, header_type: str = 'h4', plain_text_type: str = 'p'):
        self.soup = BeautifulSoup(code, 'html.parser')
        self.headers = header_type
        self.text = plain_text_type

    def __iter__(self):

        header_count = 0
        text_count = 0
        curr_header = None
        for tag in self.soup.find_all([self.headers, self.text]):
            if tag.name == self.headers:
                curr_header = tag.text.replace('\r\n', ' ')
                header_count += 1
                text_count = 0
            else:
                text_count += 1
                yield header_count, curr_header, text_count, par.Paragraph(
                    tag.text.replace('\r\n', ' ').replace('  ', ' ')
                )

    @staticmethod
    def from_url(url: str, header_type: str = 'h4', plain_text_type: str = 'p'):
        _resp = urllib.request.urlopen(url)
        _html_text = _resp.read().decode('utf-8')
        return HTMLBook(_html_text, header_type, plain_text_type)


if __name__ == '__main__':
    # gc = geonamescache.GeonamesCache()
    # for k, v in  gc.get_cities().items():
    #     print(k,':',v)
    a = HTMLBook.from_url('https://www.gutenberg.org/files/103/103-h/103-h.htm')
    for h_no, header, t_no, text in a:
        print(h_no, header, t_no)
        print(text.find_proper_names_candidates())
