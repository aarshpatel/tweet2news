from ConfigParser import SafeConfigParser
import time
from pymongo import MongoClient
import requests
import json
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

requests.packages.urllib3.disable_warnings()

#PyMonogo Data
try:
	client = MongoClient('localhost', 27017) # create a mongoclient
	db = client['twitter_db']
	collection = db['tweet_collection']
	print("Connected Successfully")
except pymongo.errors.ConnectionFailure, e:
	print "Could not connect to monogodb: %s" % e

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
	""" Gets the home timeline tweets for a given user """
	friends = get_friends(username)
	for friend in friends:
		try:
			tweets = get_tweets_from_user(friend.screen_name)
			for tweet in tweets:
				collection.insert(tweet._json)
			time.sleep(2)
		except tweepy.TweepError:
			time.sleep(2)
			continue

espn = get_tweets_from_user("espn")
with open("espn_tweets.txt", 'a') as tweet_file:
	for tweet in espn:
		tweet_file.write(tweet.text.encode('utf-8'))

# def test_pymongo(username):
# 	friends = get_friends(username)
# 	for friend in friends[0:1]:
# 		try:
# 			tweets = get_tweets_from_user(friend.screen_name)
# 			for tweet in tweets[0:1]:
# 				#print(tweet)
# 				#tweet = json.loads(tweet)
# 				collection.insert(tweet._json)
# 				time.sleep(2)
# 		except tweepy.TweepError:
# 			time.sleep(2)
# 			continue


#get_homeline_tweets("AarshPatel")

#for tweet in collection.find():
# 	print(tweet)
