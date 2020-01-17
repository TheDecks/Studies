from typing import Dict, List, Optional, Set

from AnalysisOfUnstructuredData.lists.list5 import person, hidden_prints

import requests
from bs4 import BeautifulSoup
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import matplotlib.collections as colls
import networkx as nx
import itertools
import AnalysisOfUnstructuredData.helpers.mpld3 as mpld3


class BookParser:

    chapter_pages: Dict[int, List[int]]
    page_sentences: Dict[int, List[str]]
    people: Set[person.Person]

    def __init__(self, url: str):
        _resp = requests.get(url)
        _html_text = _resp.text
        self.soup = BeautifulSoup(_html_text, 'html.parser')
        self.chapter_pages = {}
        self.page_sentences = {}
        self.people = set()
        self.tf_idf_vectorizer = TfidfVectorizer(
            analyzer='word',
            stop_words=stopwords.words('english')
        )
        self.sentiment_analyser = SentimentIntensityAnalyzer()

    @property
    def text(self):
        return ' '.join(map(' '.join, self.page_sentences.values()))

    def feed_info(self, page_buffer_size: int = 4000, mentions_thresholds: int = 3, no_texts: int = 6):
        self.pagify(page_buffer_size)
        self.create_people(mentions_thresholds)
        self.teach_tf_idf(no_texts)

    def pagify(self, page_buffer_size: int = 4000):
        chapter_counter = 0
        page_counter = 0
        page_buffer = 0
        for tag in self.soup.find_all(['a', 'p']):
            if tag.name == 'a':
                try:
                    name = tag['name']
                except KeyError:
                    continue
                if 'chap' in name:
                    chapter_counter += 1
                    if page_buffer > 0:
                        page_buffer = 0
                        page_counter += 1
                    self.chapter_pages[chapter_counter] = []
                elif 'note' in name:
                    return
            elif chapter_counter > 0:
                sentences = nltk.sent_tokenize(tag.text)
                for sentence in sentences:
                    sentence = sentence.replace('\r\n', ' ')
                    if page_counter not in self.chapter_pages[chapter_counter]:
                        self.chapter_pages[chapter_counter].append(page_counter)
                    page_buffer += len(sentence)
                    if page_counter not in self.page_sentences.keys():
                        self.page_sentences[page_counter] = []
                    self.page_sentences[page_counter].append(sentence)
                    if page_buffer > page_buffer_size:
                        page_buffer = 0
                        page_counter += 1

    def create_people(self, mentions_thresholds: int = 3):
        for _, names in self.characters_in_pages().items():
            for name in names:
                self._create_person(name)
        self.people = {someone for someone in self.people if someone.mentions >= mentions_thresholds}

    def _create_person(self, name: str):
        name = BookParser.clean_name_entry(name)
        if name == '':
            return
        for someone in self.people:
            if someone.is_mentioned(name):
                someone.update_from_entry(name)
                someone.mentions += 1
                return
        self.people.add(person.Person.from_entry(name))

    def teach_tf_idf(self, no_texts: int = 6):
        with hidden_prints.HiddenPrints():
            from nltk.book import text1, text2, text3, text4, text5, text6
            texts = [text1, text2, text3, text4, text5, text6][:no_texts]
            sample = [' '.join(text.tokens) for text in texts]
            self.tf_idf_vectorizer.fit(sample)

    def characters_in_pages(self, page_numbers: Optional[List[int]] = None) -> Dict[int, List[str]]:
        if page_numbers is None:
            page_numbers = self.page_sentences.keys()
        page_names = {}
        for page in page_numbers:
            sentences = self.page_sentences[page]
            names = []
            for sentence in sentences:
                tree = BookParser.create_nltk_tree(sentence)
                names.extend(BookParser.extract_label(tree))
            page_names[page] = names
        return page_names

    @staticmethod
    def create_nltk_tree(sentence: str) -> nltk.Tree:
        return nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)))

    @staticmethod
    def extract_label(tree: nltk.Tree, label: str = 'PERSON') -> List[str]:
        """
        nltk parses sentence as nested tree structure. Function iteratively searches for a tree labeled as >label<.
        As of
        https://gist.github.com/onyxfish/322906?fbclid=IwAR0Qt7gGkrDDCeozS2Thd3qBjx_mgClqGI7GhcmQsONtIuqiB81KkXHWaxk .
        """
        entity_names = []
        if hasattr(tree, 'label') and tree.label:
            if tree.label() == label:
                entity_names.append(' '.join([child[0] for child in tree]))
            else:
                for child in tree:
                    entity_names.extend(BookParser.extract_label(child))
        return entity_names

    @staticmethod
    def clean_name_entry(name_entry: str) -> str:
        new_entry = re.sub('[A-Z][a-z]*[.] ?', '', name_entry)
        new_entry = re.sub('[Cc]aptain ?', '', new_entry)
        return new_entry.strip()

    def character_counter(self, pages: Optional[List[int]] = None) -> Dict[int, Dict[person.Person, int]]:
        page_character_counter = {}
        for page, names in self.characters_in_pages(pages).items():
            character_counter = {}
            page_character_counter[page] = character_counter
            for name in names:
                try:
                    someone = self._find_person(name)
                except ValueError:
                    continue
                if someone in character_counter.keys():
                    character_counter[someone] += 1
                else:
                    character_counter[someone] = 1
        return page_character_counter

    def _find_person(self, name: str):
        name = BookParser.clean_name_entry(name)
        for someone in self.people:
            if someone.is_mentioned(name):
                return someone
        raise ValueError(f'Person entry not found for "{name}" entry.')

    def keywords(self, n: int = 20) -> Dict[str, float]:
        fitted_matrix = self.tf_idf_vectorizer.transform([self.text])
        word_score = {}
        names = self.tf_idf_vectorizer.get_feature_names()
        for ind, score in zip(fitted_matrix.indices, fitted_matrix.data):
            word_score[names[ind]] = score
        occurrence_list = [(v, k) for k, v in word_score.items()]
        occurrence_list.sort(reverse=True)
        return {k: v for v, k in occurrence_list[:n]}

    def sentiment(self, per: str = 'page', split_into_sentence_chunks: int = 5) -> Dict[int, Dict[str, float]]:
        if per == 'chapter':
            to_iter = {}
            for chapter, pages in self.chapter_pages.items():
                to_iter[chapter] = []
                for page in pages:
                    to_iter[chapter].extend(self.page_sentences[page])
        else:
            to_iter = self.page_sentences
        number_polarity = {}
        for enum, sentences in to_iter.items():
            sentence_chunk_counter = 0
            sentiment = {'pos': 0, 'neg': 0, 'neu': 0, 'compound': 0}
            chunks = 0
            while sentence_chunk_counter < len(sentences):
                this_chunk = ' '.join(sentences[
                                      sentence_chunk_counter:sentence_chunk_counter + split_into_sentence_chunks
                                      ])
                this_polarity = self._get_chunk_sentiment(this_chunk)
                sentence_chunk_counter += split_into_sentence_chunks
                chunks += 1
                for polarity, val in this_polarity.items():
                    sentiment[polarity] += val
            number_polarity[enum] = {pol: val / chunks for pol, val in sentiment.items()}
        return number_polarity

    def _get_chunk_sentiment(self, chunk: str) -> Dict[str, float]:
        polarity = self.sentiment_analyser.polarity_scores(chunk)
        return polarity

    def sentiment_plot(self, per: str = 'page', split_into_sentence_chunks: int = 5):
        ind, pos, neg, compound = [], [], [], []
        snt = self.sentiment(per, split_into_sentence_chunks)
        ind = sorted(snt.keys())
        for i in ind:
            pos.append(snt[i]['pos'])
            neg.append(snt[i]['neg'])
            compound.append(snt[i]['compound'])
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.plot(ind, pos, 'g', label='positive')
        ax.plot(ind, neg, 'r', label='negative')
        ax.plot(ind, compound, 'grey', label='compound')
        ax.set_xlim(min(ind), len(ind))
        ax.axhline(y=0, linestyle=':')
        ax.legend()
        ax.set_xlabel(per)
        ax.set_ylabel('sentiment')
        plt.show()

    def co_occurrence_graph(self, pages: Optional[List[int]] = None):
        graph = nx.Graph()
        nodes_sizes = {}
        for page, characters in self.characters_in_pages(pages).items():
            new_chars = set()
            for char in characters:
                try:
                    someone = self._find_person(char)
                except ValueError:
                    continue
                graph.add_node(someone, label=' '.join(someone.identifiers))
                new_chars.add(someone)
                if someone not in nodes_sizes:
                    nodes_sizes[someone] = 1
                else:
                    nodes_sizes[someone] += 1
            # print(new_chars)
            for edge in itertools.combinations(new_chars, 2):
                if edge not in graph.edges:
                    graph.add_edge(*edge, weight=1)
                else:
                    # print('here')
                    graph[edge[0]][edge[1]]['weight'] += 1
        nx.set_node_attributes(graph, nodes_sizes, 'size')
        return graph

    @staticmethod
    def draw_graph(graph: nx.Graph):
        pos = nx.spring_layout(graph, k=24/(len(graph.nodes)**(1/2)), iterations=100, weight=None, scale=5)
        fig = plt.figure()
        ax = fig.add_subplot()
        attrs = nx.get_node_attributes(graph, 'size')
        nx.draw_networkx_nodes(graph, pos=pos, ax=ax, node_size=[attrs[node] * 10 for node in graph.nodes])
        print([graph[edge[0]][edge[1]]['weight'] for edge in graph.edges])
        nx.draw_networkx_edges(graph, pos=pos,
                               width=[(graph[edge[0]][edge[1]]['weight'] / 1.5) ** (3/2) for edge in graph.edges])
        mpld3.plugins.connect(fig, BookParser._get_nodes_plugin(graph, BookParser._retrieve_handles_for_html(ax)))
        mpld3.show(fig)
        plt.show()

    @staticmethod
    def _retrieve_handles_for_html(ax: plt.Axes) -> Optional[colls.PatchCollection]:
        nodes_collection = None
        for child in ax.get_children():
            if isinstance(child, colls.PathCollection):
                nodes_collection = child
        return nodes_collection

    @staticmethod
    def _get_nodes_plugin(graph, handles):
        lab = nx.get_node_attributes(graph, 'label')
        labs = [lab[n] for n in graph.nodes]
        return mpld3.plugins.PointLabelTooltip(handles, labels=labs)


if __name__ == "__main__":
    bp = BookParser('https://www.gutenberg.org/files/51060/51060-h/51060-h.htm')

    print('Initializing information...')
    bp.feed_info()

    print('Character mentions pro page: ')
    chars_count = bp.character_counter()
    for pg, character_counters in chars_count.items():
        print(pg)
        for ch, counter in character_counters.items():
            print(ch, ':', counter)

    print('Top n keywords: ')
    kwds = bp.keywords(20)
    for kwd, score in kwds.items():
        print(kwd, ':', score)

    print('Sentiment pro page: ')
    for pg, sents in bp.sentiment(split_into_sentence_chunks=3).items():
        print(pg, sents)
    bp.sentiment_plot('page')

    print('Sentiment pro chapter: ')
    for ch, sents in bp.sentiment(per='chapter', split_into_sentence_chunks=3).items():
        print(ch, sents)
    bp.sentiment_plot('chapter')

    print('Co-occurrence graph: ')
    g = bp.co_occurrence_graph()
    bp.draw_graph(g)
