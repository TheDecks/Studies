from typing import Tuple, Optional, List

import pandas as pd
import re
import bokeh.plotting as bplt
import bokeh.layouts as blay
import math
import folium

import AnalysisOfUnstructuredData.lists.list4.data_feeder as dataf
from AnalysisOfUnstructuredData.helpers.tweet.place import Place
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.resources import INLINE
from bokeh.embed import file_html
from bokeh.models import LabelSet


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

    def create_pie_charts(self, summariser: str = 'Occurrences') -> List:
        df = self.summarised()
        plots = []
        for country in self.countries:
            df_temp = df[df['Country'] == country.name].copy()
            if not df_temp.empty:
                df_temp["Angle"] = df_temp[summariser] / df_temp[summariser].sum() * 2 * math.pi
                no_colors = df_temp.shape[0]
                select = no_colors if no_colors >= 3 else 3
                cols = Category20c[select][:no_colors]
                df_temp["Color"] = cols
                plot = bplt.figure(title=f"{summariser} share", width=200, height=200)
                plot.wedge(
                    x=0, y=0, radius=1,
                    start_angle=cumsum('Angle', include_zero=True),
                    end_angle=cumsum('Angle'),
                    line_color="white", fill_color='Color', # legend='Activity',
                    source=df_temp
                )
                plots.append(plot)
            else:
                plots.append(None)
        return plots

    def create_bar_plots(self, summariser: str = 'Occurrences') -> List:
        df = self.summarised()
        plots = []
        for country in self.countries:
            df_temp = df[df['Country'] == country.name].copy()
            if not df_temp.empty:
                no_colors = df_temp.shape[0]
                select = no_colors if no_colors >= 3 else 3
                cols = Category20c[select][:no_colors]
                df_temp["Color"] = cols
                plot = bplt.figure(x_range=df_temp['Activity'], title=f"{summariser}", width=200, height=300)
                plot.xaxis.major_label_orientation = math.pi / 2
                plot.vbar(x='Activity', top=summariser, source=df_temp, fill_color='Color', width=0.7)
                plots.append(plot)
            else:
                plots.append(None)
        return plots

    def create_summarising_plot(self):
        occ_pies = self.create_pie_charts()
        time_bars = self.create_bar_plots('Time')
        distance_bars = self.create_bar_plots("Distance")
        pace_bars = self.create_bar_plots("Pace")
        all_plot = []
        for i in range(len(occ_pies)):
            if occ_pies[i] is not None:
                all_plot.append(blay.grid([
                    [occ_pies[i], time_bars[i]],
                    [distance_bars[i], pace_bars[i]]
                ]))
            else:
                all_plot.append(None)
        return all_plot

    def draw_map(self, file_path: str):
        my_map = folium.Map(location=[0, 0], zoom_start=2)
        poses = [country.middle() for country in self.countries]
        plots = self.create_summarising_plot()
        for i in range(len(plots)):
            if plots[i] is not None:
                html = file_html(plots[i], INLINE)

                iframe = folium.IFrame(html=html, width=420, height=620)
                folium.Marker(
                    poses[i], tooltip=self.countries[i].name,
                    popup=folium.Popup(iframe, max_width=420)
                ).add_to(my_map)

        my_map.save(file_path)


if __name__ == "__main__":
    from AnalysisOfUnstructuredData.helpers.tweet import cities_countries as c
    tracker = EndomondoTracker(
        consumer_key='eHJQ09OKnHAEtWaSfCDmSP5Se',
        consumer_secret='zzzPq6DxrjSyo5hne4PuxJjX0AoTG5DDccO2xZZGHTSgNmLlTc',
        access_token='1199289795463319553-PCe8pxHGts77prqpQ0KhP3O6ENHrWK',
        access_token_secret='Ou8JSTqcxGTPb2XlfSjGLsmv05J4Zt1ATJJeJQLOMtkRA'
    )
    for city in c.cities.values():
        tracker.add_city(city)
    for country in c.countries.values():
        tracker.add_country(country)
    tracker.prepare_tweets_df(10000)
    tracker.draw_map('maps.html')
