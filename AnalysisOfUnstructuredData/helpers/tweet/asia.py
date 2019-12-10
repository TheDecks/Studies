import tweepy
import pandas as pd
import pprint as pp
import re
from geopy.geocoders import Nominatim as nm
import numpy as np


class CityTweets:

    def __init__(self):
        consumer_key = 'eHJQ09OKnHAEtWaSfCDmSP5Se'
        consumer_secret = 'zzzPq6DxrjSyo5hne4PuxJjX0AoTG5DDccO2xZZGHTSgNmLlTc'
        access_token = '1199289795463319553-PCe8pxHGts77prqpQ0KhP3O6ENHrWK'
        access_token_secret = 'Ou8JSTqcxGTPb2XlfSjGLsmv05J4Zt1ATJJeJQLOMtkRA'
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.tweets_df = pd.DataFrame()

    @staticmethod
    def get_location_info(city_name):
        geo_locator = nm(user_agent='myapplication', timeout=60)
        location = geo_locator.geocode(city_name, exactly_one=False)[0]
        return location.raw['display_name'], location.raw['lat'], location.raw['lon'], location.raw['boundingbox']

    @staticmethod
    def get_coordinates_radius(city_name):
        loc_info = CityTweets.get_location_info(city_name)
        lat = loc_info[1]
        lon = loc_info[2]
        boundaries = [float(i) for i in loc_info[3]]
        rad = (40075.704 / 360 * np.sqrt((boundaries[1] - boundaries[0]) ** 2 + (
                np.cos(boundaries[0] * np.pi / 180) * (boundaries[3] - boundaries[2])) ** 2)) / 2 + 5
        return lat, lon, rad

    def get_tweets(self, city_name, tag='#Endomondo'):
        location = list(CityTweets.get_coordinates_radius(city_name))[0:2]
        radius = CityTweets.get_coordinates_radius(city_name)[2]
        tweets = []
        for tweet in tweepy.Cursor(self.api.search,
                                   tweet_mode='extended',
                                   q=tag,
                                   count=100,
                                   geocode=str(location[0]) + ',' + str(location[1]) + ',' + str(radius) + 'km').items():
            if tweet.coordinates is not None:
                tweets.append((city_name, *tweet.coordinates['coordinates'], tweet.full_text))
        self.tweets_df = pd.DataFrame(tweets)
        self.tweets_df.columns = ['City', 'Longitude', 'Latitude', 'Tweet']

    def get_activities(self):
        activities = []
        patterns = ['I was out ', 'I just finished ']
        # for tweet in self.tweets_df['Tweet']:
        #     pp.pprint(tweet)
        #     activity = tweet.partition(patterns[0])[2]
        #     if len(activity) > 0:
        #         activities.append(activity)
        #         print(activity)
        #     activity = tweet.partition(patterns[1])[2]
        #     if len(activity) > 0:
        #         activities.append(activity)
        #         print(activity)
        # return activities
        for tweet in self.tweets_df['Tweet']:
            pp.pprint(tweet)
            index = tweet.find('out ')
            activity = tweet[index + 1:]
            print(activity)
            if len(activity) > 0:
                activities.append(activity)
            index = tweet.find('finished ')
            activity = tweet[index + 1:]
            print(activity)
            if len(activity) > 0:
                activities.append(activity)
        return activities


if __name__ == '__main__':
    test = CityTweets()
    my_city = 'Madrid'
    print(test.get_coordinates_radius(my_city))
    test.get_tweets(my_city)
    print(test.tweets_df)
    print(test.get_activities())
    print(len(test.get_activities()))