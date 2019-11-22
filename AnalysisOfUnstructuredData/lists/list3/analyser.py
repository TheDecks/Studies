from typing import Dict, Tuple, List

from AnalysisOfUnstructuredData.helpers.book import html_book, city
from math import cos, asin, sqrt, pi
import geonamescache
import itertools


def map_distance(coords_1: Tuple[float, float], coords_2: Tuple[float, float]):
    lat1, lon1 = coords_1
    lat2, lon2 = coords_2
    p = pi/180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))


class BookAnalyser:

    cities_info: Dict[str, List[city.CityEntry]]
    path: List[List[city.CityEntry]]
    sp_offset: float

    def __init__(self, h_book: html_book.HTMLBook):
        self.book = h_book
        self.cities_info = {}
        self.path = []
        self.sp_offset = 0

    def create_cities_dictionary(self, population_threshold: int = 78000):
        gc = geonamescache.GeonamesCache()
        for _, entry in gc.get_cities().items():
            if entry['population'] >= population_threshold:
                if entry['name'] not in self.cities_info:
                    self.cities_info[entry['name']] = [city.CityEntry(
                        entry['name'], entry['latitude'], entry['longitude'], entry['population']
                    )]
                else:
                    self.cities_info[entry['name']].append(city.CityEntry(
                        entry['name'], entry['latitude'], entry['longitude'], entry['population']
                    ))

    def define_starting_point(self, city_name: str = 'London'):
        self.path.append([max(self.cities_info[city_name], key=lambda cty: cty.population)])
        self.cities_info[city_name] = [max(self.cities_info[city_name], key=lambda cty: cty.population)]
        self.sp_offset = - self.path[0][0].longitude

    def create_unrestricted_path(self):
        for h_no, header, t_no, text in self.book:
            if h_no >= 7:
                for city_name in text.find_proper_names_candidates():
                    city_name = BookAnalyser.get_modern_name(city_name)
                    if city_name in self.cities_info:
                        self.path.append(self.cities_info[city_name])

    def filter_path_by_occurrences(self, min_occurrences: int = 2):
        counter_dict = {}
        for possibilities in self.path:
            if possibilities:
                city_name = possibilities[0].name
                if city_name not in counter_dict:
                    counter_dict[city_name] = 1
                else:
                    counter_dict[city_name] += 1
        city_names_filtered = {cty for cty in counter_dict if counter_dict[cty] >= min_occurrences}
        # city_names_filtered.remove('Nagasaki')
        for path_position, possibilities in enumerate(self.path):
            city_name = possibilities[0].name
            if city_name not in city_names_filtered:
                self.path[path_position] = []

    def filter_path_by_longitude_distance(
            self, distance_threshold: float, start_from: int = 1
    ) -> Tuple[int, List[List[city.CityEntry]]]:
        last_recorded_valid = 0
        remainer = []
        for path_position, possibilities in enumerate(self.path[start_from:]):
            swap_elements = False
            positions = [cty.position for cty in self.path[path_position + start_from - 1]]
            possibilities_filtered = [
                direction for direction in possibilities if any([
                    map_distance(direction.position, prev_position) < distance_threshold
                    and (prev_position[1] + self.sp_offset) % 360 < (
                            direction.longitude + self.sp_offset) % 360
                    for prev_position in positions
                ])
            ]
            if not possibilities_filtered:
                possibilities_filtered = self.get_betweeners(
                    possibilities, path_position + start_from - 1, distance_threshold
                )
                swap_elements = True
            self.path[path_position + start_from] = possibilities_filtered
            if swap_elements:
                last = self.path[path_position + start_from - 1]
                self.path[path_position + start_from] = last
                self.path[path_position + start_from - 1] = possibilities_filtered
            if possibilities_filtered:
                last_recorded_valid = path_position + start_from
                remainer = []
            else:
                remainer.append(possibilities)
        return last_recorded_valid, remainer

    def get_betweeners(self, possibilities: List[city.CityEntry], position: int, distance_threshold: float):
        previous, nxt = self.get_last_non_empty(position)
        return [
            direction for direction in possibilities if any([
                (prev_city.longitude + self.sp_offset) % 360 < (
                        direction.longitude + self.sp_offset) % 360 < (next_city.longitude + self.sp_offset) % 360
                and map_distance(direction.position, prev_city.position) < distance_threshold
                and map_distance(direction.position, next_city.position) < distance_threshold
                for prev_city, next_city in itertools.product(previous, nxt)
            ])
        ]

    def get_last_non_empty(self, pos: int):
        try:
            first = []
            second = []
            while not second:
                second = self.path[pos]
                pos -= 1
            while not first:
                first = self.path[pos]
                pos -= 1
            return first, second
        except IndexError:
            return [], []

    def jump_location_on_path(self, pos: int):
        curr_lon = max([cty.longitude for cty in self.path[pos]])
        ret_pos = -1
        current_smallest_distance = 100000000
        for path_position, possibilities in enumerate(self.path[pos + 1:]):
            if any([
                (direction.longitude + self.sp_offset) % 360 > (curr_lon + self.sp_offset) % 360
                for direction in possibilities
            ]):

                new_smallest_distance = min([
                    map_distance(direction.position, self.path[pos][0].position) for direction in possibilities
                ])
                if new_smallest_distance < current_smallest_distance:
                    ret_pos = pos + 1 + path_position
                    current_smallest_distance = new_smallest_distance
        for i in range(pos + 1, ret_pos):
            self.path[i] = []
        return ret_pos

    def process_whole_path(
            self,
            starting_city: str = 'London', distance_threshold: int = 3100,
            finish_threshold: int = 300, min_occurrences: int = 2
    ):
        self.define_starting_point(starting_city)
        self.create_unrestricted_path()
        self.filter_path_by_occurrences(min_occurrences)
        first = []
        i = 0
        while not first:
            first = self.path[i]
            i += 1
        processed_positions = 1
        while True:
            processed_positions, remaining_to_process = self.filter_path_by_longitude_distance(
                distance_threshold, processed_positions
            )
            if any([
                map_distance(direction.position, first[0].position) < finish_threshold
                for direction in self.path[-1]
            ]):
                break
            else:
                self.path[processed_positions] = self.path[-1]
                self.path = self.path[:processed_positions + 1] + remaining_to_process
                processed_positions = self.jump_location_on_path(processed_positions) + 1
            if processed_positions < 0:
                break
        self.path.append(first)

    @staticmethod
    def get_modern_name(city_name: str) -> str:
        if city_name == 'Bombay':
            return 'Mumbai'
        elif city_name == 'Calcutta':
            return 'Kolkata'
        elif city_name == 'New York':
            return 'New York City'
        else:
            return city_name

    def print_path_pretty(self):
        print('----------------------')
        for e in self.path:
            if e:
                print(e)
        print('----------------------')

    @property
    def visited_cities(self):

        def _cities_gen(path: List[List[city.CityEntry]]):
            for found_cities in path:
                if found_cities:
                    if len(found_cities) == 1:
                        current = found_cities[0]
                    else:
                        current = min(found_cities, key=lambda cty: map_distance(current.position, cty.position))
                    yield current

        return _cities_gen(self.path)

    def save_path_on_map(self, path: str):
        import folium
        my_map = folium.Map(location=[0, 180 + self.sp_offset], zoom_start=2)
        all_list = [cty for cty in self.visited_cities]
        poses = [all_list[0].position] + [(cty.latitude, cty.longitude % 360) for cty in all_list[1:]]
        folium.PolyLine(poses).add_to(my_map)
        for (pos, cty) in zip(poses, all_list):
            folium.Marker(
                pos, tooltip='See town info',
                popup=folium.Popup(cty.html_popup, max_width=100)
            ).add_to(my_map)
        my_map.save(path)
