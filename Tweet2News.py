# Helper Imports
from ConfigParser import SafeConfigParser
import operator

# Natural Language Processing
import nltk
from nltk.tokenize import TweetTokenizer

# Tweepy Imports
import tweepy
from tweepy import OAuthHandler

# HTTP Imports
import requests
import webbrowser
import urlparse
import httplib

# Flask Imports
from flask import Flask
from flask import request

requests.packages.urllib3.disable_warnings()

parser = SafeConfigParser()
parser.read('config.ini')

access_token = parser.get("user_auth", "access_token")
access_token_secret = parser.get("user_auth", "access_token_secret")
consumer_key = parser.get("user_auth", "consumer_key")
consumer_secret = parser.get("user_auth", "consumer_secret")

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def chunker(tokens):
    """ Noun Phrase Proccesing on twitter tokens """
    grammar = "NP: {<DT>?<JJ>*(<NN>|<NNP>|<NNS>)}"
    cp = nltk.RegexpParser(grammar)
    result = cp.parse(tokens)
    return result


def create_keywords(tweets, **grammar):
    """ Finds keywords for tweets using NLP"""
    tweet_dict = {}
    for tweet in tweets:
        if(not tweet): continue
        tknzer = TweetTokenizer()
        tokens = tknzer.tokenize(tweet)
        tags = nltk.pos_tag(tokens)
        if "add_token" in grammar:
            sequence = [word for word in tags if(word[1] == 'NNP' or word[1] == 'NN')]
        else:
            sequence = [word for word in tags if(word[1] == 'NNP')]
        word_sequence = ' '.join(seq[0] for seq in sequence)
        tweet_dict[tweet] = word_sequence
    return tweet_dict

def search_twitter_global(keywords):
    """ Searches the twitter globe based on the given keywords """
    if not keywords: pass
    articles = []
    for tweet in tweepy.Cursor(api.search, q=keywords, rpp=100, result_type="recent", lang="en").items(100):
        if(('http://' in tweet.text or 'https://' in tweet.text) and (len(articles) != 50)):
            articles.append(tweet.text.encode("utf-8"))
    return articles

def unshorten_url(url):
    """ Unshorten the passed in url"""
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc)
    h.request('HEAD', parsed.path.encode('utf-8'))
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return response.getheader('Location')
    else:
        return url

def find_best_article(tweets):
    """ Finds the best articles from a collection of tweets that contain articles """
    tweet_cluster = {}
    for tweet in tweets:
        tkner = TweetTokenizer()
        tokens = tkner.tokenize(tweet)
        links = filter(lambda x: ("http" in x and ("twitter.com" not in x or "fb.com" not in x)), tokens)
        try:
            links = map(lambda x: unshorten_url(x), links)
        except: pass
        links = filter(lambda x: ("t.co" not in x) and ("twitter.com" not in x) and ("fb.com" not in x), links)
        for link in links:
            if(link not in tweet_cluster):
                tweet_cluster[link] = 1
            else:
                tweet_cluster[link] = tweet_cluster[link] + 1

    return tweet_cluster

def test_whole(tweet):
    """ For a given tweet, opens up two articles that relate to the tweet """
    tweet_keywords = create_keywords(tweet)
    print(tweet_keywords)
    for key, value in tweet_keywords.iteritems():
        articles = search_twitter_global(value)
        tweet_cluster = find_best_article(articles)
        sorted_x = sorted(tweet_cluster.items(), key=operator.itemgetter(1), reverse=True)
        try:
            for i in range(0, 2):
                link = sorted_x[i][0]
                open_webpage(link) #open link on on the website
        except:
            print("No article found")
        return "success"

def open_webpage(link):
    webbrowser.open(link, new=2)
