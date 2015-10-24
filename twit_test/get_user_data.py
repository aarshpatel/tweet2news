from ConfigParser import SafeConfigParser
import time
import requests
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

requests.packages.urllib3.disable_warnings()

parser = SafeConfigParser()
parser.read('config.ini');

access_token = parser.get("user_auth", "access_token")
access_token_secret = parser.get("user_auth", "access_token_secret")
consumer_key = parser.get("user_auth", "consumer_key")
consumer_secret = parser.get("user_auth", "consumer_secret")

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def get_friends(user_id):
    users = []
    page_count = 0
    for user in tweepy.Cursor(api.friends, id=user_id, count=200).pages():
        page_count += 1
        users.extend(user)
    return users

def get_tweets_from_user(username):
	""" Gets tweets from screen_name """
	user = api.user_timeline(screen_name = username, count = 50, include_rts = True)
	return user

def get_homeline_tweets(username):
	friends = get_friends(username)
	with open('tweets.json', 'a') as tweet_file:
		for u in friends:
			try:
				tweet = get_tweets_from_user(u.screen_name)
				tweet_file.write(str(tweet))
				time.sleep(2)
			except tweepy.TweepError:
				time.sleep(2)
				continue


get_homeline_tweets("AarshPatel")

