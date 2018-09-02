import twitter
from datetime import datetime
import time
from random import choice
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from _thread import start_new_thread

analyzer = SentimentIntensityAnalyzer()

api = twitter.Api(consumer_key='',
                  consumer_secret='',
                  access_token_key='',
                  access_token_secret='')

tweets_list = []


def streamTweets():
    while True:
        trending = api.GetTrendsWoeid(23424977)
        hashtags = []
        for i in trending:
            i = i.AsDict()
            if 'tweet_volume' not in i.keys() or 'query' not in i.keys():
                continue
            hashtags.append({'query': i['query'], 'tweet_volume': i['tweet_volume']})
        trending = sorted(hashtags, key=lambda k: k['tweet_volume'])[::-1][:5]

        query = choice(trending)
        # print(query)

        tweets = api.GetSearch(raw_query="q={}".format(query['query']))
        for tweet in tweets:
            try:
                t = datetime.utcnow().timestamp() - datetime.strptime(tweet.AsDict()['created_at'],
                                                                      '%a %b %d %X %z %Y').timestamp()

                if tweet.AsDict()['lang'] != 'en' or (
                        'favorited' in tweet.AsDict().keys() and tweet.AsDict()['favorited']):
                    continue

                f2f = int(tweet.AsDict()['user']['friends_count']) - int(tweet.AsDict()['user']['followers_count'])

                tweets_list.append(
                    {'id': tweet.AsDict()['id'],
                     'tweet': tweet.AsDict()['text'],
                     # 'following': int(tweet.AsDict()['user']['friends_count']),
                     'followers': int(tweet.AsDict()['user']['followers_count']),
                     'f2f': f2f,
                     'sentiment': analyzer.polarity_scores(tweet.AsDict()['text'])['compound'],
                     'likes': int(tweet.AsDict()['favorite_count']) if 'favorite_count' in tweet.AsDict().keys() else 0,
                     }
                )
            except Exception as e:
                print('Error', e)
                continue
        time.sleep(100)
        if len(tweets_list) > 100:
            del tweets_list[:100]


def likeTweets():
    print('Liking Thread Started')
    while True:
        if len(tweets_list) < 10:
            time.sleep(10)
            continue
        for i in range(len(tweets_list)):
            tweet_1 = tweets_list[i]
            for y in range(len(tweets_list)):
                tweet_2 = tweets_list[y]
                if tweet_1['id'] == tweet_2['id']:
                    continue
                if tweet_1['sentiment'] > tweet_2['sentiment']:
                    tweets_list[i], tweets_list[y] = tweets_list[y], tweets_list[i]

        selected_tweets = tweets_list[:10]

        for i in range(len(selected_tweets)):
            tweet_1 = selected_tweets[i]
            for y in range(len(selected_tweets)):
                tweet_2 = selected_tweets[y]
                if tweet_1['id'] == tweet_2['id']:
                    continue
                if tweet_1['f2f'] > tweet_2['f2f']:
                    selected_tweets[i], selected_tweets[y] = selected_tweets[y], selected_tweets[i]

        selected_tweets = selected_tweets[:3]

        for i in range(len(selected_tweets)):
            tweet_1 = selected_tweets[i]
            for y in range(len(selected_tweets)):
                tweet_2 = selected_tweets[y]
                if tweet_1['id'] == tweet_2['id']:
                    continue
                if tweet_1['followers'] > tweet_2['followers']:
                    selected_tweets[i], selected_tweets[y] = selected_tweets[y], selected_tweets[i]

        selected_tweets = selected_tweets[:2]

        for i in range(len(selected_tweets)):
            tweet_1 = selected_tweets[i]
            for y in range(len(selected_tweets)):
                tweet_2 = selected_tweets[y]
                if tweet_1['id'] == tweet_2['id']:
                    continue
                if tweet_1['likes'] < tweet_2['likes']:
                    selected_tweets[i], selected_tweets[y] = selected_tweets[y], selected_tweets[i]

        selected_tweet = selected_tweets[0]

        if selected_tweet['sentiment'] < 0.1:
            tweets_list.remove(selected_tweet)
            continue

        api.CreateFavorite(status_id=selected_tweet['id'])
        print(selected_tweet)
        tweets_list.remove(selected_tweet)
        time.sleep(1200)


if __name__ == "__main__":
    _ = start_new_thread(likeTweets, ())
    streamTweets()
