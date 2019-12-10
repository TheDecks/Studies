from typing import Generator

import tweepy


class TweeterFeeder:

    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def search(self, query: str, limit_items: int = 10000) -> Generator[tweepy.Status, None, None]:
        for tweet in tweepy.Cursor(
                self.api.search, q=query, tweet_mode='extended', count=150
        ).items(limit_items):
            if tweet.coordinates is not None:
                yield tweet


if __name__ == "__main__":
    feeder = TweeterFeeder(
        consumer_key='eHJQ09OKnHAEtWaSfCDmSP5Se',
        consumer_secret='zzzPq6DxrjSyo5hne4PuxJjX0AoTG5DDccO2xZZGHTSgNmLlTc',
        access_token='1199289795463319553-PCe8pxHGts77prqpQ0KhP3O6ENHrWK',
        access_token_secret='Ou8JSTqcxGTPb2XlfSjGLsmv05J4Zt1ATJJeJQLOMtkRA'
    )
