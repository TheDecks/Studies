from typing import Tuple, Optional, List

import pandas as pd
import re
import bokeh.plotting as bplt
import math

import AnalysisOfUnstructuredData.lists.list4.data_feeder as dataf
from AnalysisOfUnstructuredData.helpers.tweet.place import Place
from bokeh.palettes import Category20c
from bokeh.transform import cumsum


class EndomondoTracker:

    cities: List[Place]
    countries: List[Place]

    def __init__(self, **kwargs):
        self.feeder = dataf.TweeterFeeder(**kwargs)
        self.tweets_df = pd.DataFrame()
        self.cities = []
        self.countries = []

    def add_city(self, c: Place):
        self.cities.append(c)

    def add_country(self, c: Place):
        self.countries.append(c)

    def create_twitters_data_frame(self, n: int):
        rows = []
        for tweet in self.feeder.search("#Endomondo", n):
            rows.append(self._prepare_tweet_row(tweet))
        self.tweets_df = pd.DataFrame(rows)
        self.tweets_df.columns = ["id", "Lat", "Long", "Text"]
        self.tweets_df['OriginalText'] = self.tweets_df['Text']

    def _prepare_tweet_row(self, tweet: dataf.tweepy.Status) -> Tuple[str, float, float, str]:
        long, lat = tweet.coordinates["coordinates"]
        return tweet.id_str, lat, long, tweet.full_text

    def strip_unnecessary_text_right(self):
        self.tweets_df['Text'] = self.tweets_df['Text'].apply(
            lambda t:
            re.search("(.*) with #[Ee]ndomondo", t).group(1)
            if re.search("(.*) with #[Ee]ndomondo", t)
            else ''
        )

    def strip_unnecessary_text_left(self):
        self.tweets_df['Text'] = self.tweets_df['Text'].apply(
            lambda t:
            re.search("I just finished (.*)", t).group(1)
            if re.search("I just finished (.*)", t)
            else t
        )
        self.tweets_df['Text'] = self.tweets_df['Text'].apply(
            lambda t:
            re.search("I was out (.*)", t).group(1)
            if re.search("I was out (.*)", t)
            else t
        )

    def restrict_to_meaningful_rows(self):
        self.tweets_df = self.tweets_df[self.tweets_df["Text"] != '']

    def find_time(self):
        self.tweets_df['Time'] = self.tweets_df["Text"].apply(
            lambda t:
            re.search(r"(\d{1,2}h:)?(\d{1,2}m:)?\d{1,2}s", t).group(0)
            if re.search(r"(\d{1,2}h)?(\d{1,2}m)?\d{1,2}s", t)
            else None
        )
        self.tweets_df['Text'] = self.tweets_df["Text"].apply(
            lambda t:
            re.sub(r"(in )?(\d{1,2}h:)?(\d{1,2}m:)?\d{1,2}s( of)?", '', t).strip()
        )

    def find_distance(self):
        def distance_unit_from_text(t: str):
            if re.search(r"\d*[.]\d* [a-z].*", t) is not None:
                return tuple(map(str.strip, re.search(r"\d*[.]\d* [a-z].*", t).group(0).split()))
            else:
                return None, None
        self.tweets_df['Distance'], self.tweets_df['Unit'] = zip(*self.tweets_df["Text"].apply(distance_unit_from_text))
        self.tweets_df['Text'] = self.tweets_df["Text"].apply(
            lambda t:
            re.sub(r"\d*[.]\d* [a-z].*", '', t).strip()
        )

    def get_remainer_as_activity(self):
        self.tweets_df['Activity'] = self.tweets_df['Text']
        self.tweets_df = self.tweets_df.drop(columns=["Text"])

    def unify(self):
        def parse_time(time_str: Optional[str]):
            if time_str is None:
                return None
            seconds = 0
            multipliers = pd.np.cumprod([1, 60, 60, 24, 7])
            for i, time_unit in enumerate(time_str.split(':')[::-1]):
                seconds += int(time_unit[:-1]) * multipliers[i]
            return seconds

        self.tweets_df['Distance'] = self.tweets_df.apply(
            lambda row:
            float(row['Distance'])
            if row['Unit'] == 'km'
            else (
                float(row['Distance']) * 1.60934
                if row['Distance'] is not None
                else None
            ), axis=1
        )
        self.tweets_df['Time'] = self.tweets_df['Time'].apply(
            parse_time
        )
        self.tweets_df = self.tweets_df.drop(columns=["Unit"])

    def identify_cities(self):
        self.tweets_df['City'] = self.tweets_df.apply(
            lambda row: EndomondoTracker.try_match_place_from_list(row['Lat'], row['Long'], self.cities), axis=1
        )

    def identify_countries(self):
        self.tweets_df['Country'] = self.tweets_df.apply(
            lambda row: EndomondoTracker.try_match_place_from_list(row['Lat'], row['Long'], self.countries), axis=1
        )

    def prepare_tweets_df(self, max_tweets: int = 500):
        self.create_twitters_data_frame(max_tweets)
        self.strip_unnecessary_text_right()
        self.strip_unnecessary_text_left()
        self.restrict_to_meaningful_rows()
        self.find_time()
        self.find_distance()
        self.get_remainer_as_activity()
        self.identify_cities()
        self.identify_countries()
        self.unify()

    @staticmethod
    def try_match_place_from_list(lat: float, long: float, places: List[Place]):
        for place in places:
            if place.contains_map_point((lat, long)):
                return place.name
        return None

    def summarised(self, by: str = "Country"):

        df = self.tweets_df.copy()
        df['Pace'] = df['Distance'] * 1000 / df['Time']
        size = lambda x: len(x)
        if by == "Country":
            ret = df[["Country", "Activity", "Time", "Distance", "Pace"]].groupby(by=["Country", "Activity"]).agg({
                'Distance': 'mean', 'Time': 'mean', 'Pace': ['mean', 'size']
            }).reset_index()
        else:
            ret = df[["City", "Activity", "Time", "Distance", "Pace"]].groupby(by=["City", "Activity"]).agg({
                'Distance': 'mean', 'Time': 'mean', 'Pace': ['mean', 'size']
            }).reset_index()
        ret.columns = ["Country", "Activity", "Distance", "Time", "Pace", "Occurrences"]
        return ret

    def create_pie_charts_map(self):
        df = self.summarised()
        for country in self.countries:
            df_temp = df[df['Country'] == country.name].copy()
            if not df_temp.empty:
                df_temp["Angles"] = df_temp['Occurrences'] / df_temp['Occurrences'].sum() * 2 * math.pi
                no_colors = df_temp.shape[0]
                select = no_colors if no_colors >= 3 else 3
                cols = Category20c[select][:no_colors]
                df_temp["Color"] = cols
                plot = bplt.figure()
                print(df_temp)
                plot.wedge(
                    x=0, y=0, radius=1,
                    start_angle=cumsum('Angle', include_zero=True),
                    end_angle=cumsum('Angle'),
                    line_color="white", fill_color='Color', legend='Country',
                    source=df_temp
                )
                #bplt.output_file()
                bplt.show(plot)
                break


if __name__ == "__main__":
    from AnalysisOfUnstructuredData.helpers.tweet import cities_countries as c
    tracker = EndomondoTracker(
        consumer_key='eHJQ09OKnHAEtWaSfCDmSP5Se',
        consumer_secret='zzzPq6DxrjSyo5hne4PuxJjX0AoTG5DDccO2xZZGHTSgNmLlTc',
        access_token='1199289795463319553-PCe8pxHGts77prqpQ0KhP3O6ENHrWK',
        access_token_secret='Ou8JSTqcxGTPb2XlfSjGLsmv05J4Zt1ATJJeJQLOMtkRA'
    )
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    for city in c.cities.values():
        tracker.add_city(city)
    for country in c.countries.values():
        tracker.add_country(country)
    tracker.prepare_tweets_df(200)
    print(tracker.summarised())
    tracker.create_pie_charts_map()
