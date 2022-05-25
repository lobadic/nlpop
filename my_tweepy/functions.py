from my_tweepy.utils import *
from my_tweepy.json_getters import *
import math

def get_users_info_v1(headers, user_ids=None, screen_names=None, N=100, verbose=False, every=50):
    rows_users = list()
    url = 'https://api.twitter.com/1.1/users/lookup.json'
    paramss = make_users_pamars_v1(user_ids, screen_names, N)
    for i, params in enumerate(paramss):
        if verbose and i%every==0: print(f'Currently at request {i}')
        user_jsons = get_response_v1_1(url, headers, params)
        for user_json in user_jsons:
            row = get_specified_values(user_json, specified_key_order=specified_key_order_v1, params_getters=user_params_getters_v1)
            rows_users.append(row)
    return rows_users

def get_tweets_v2(headers, root_params, tweet_ids, verbose=False, every=50):
    rows_tweets = list()
    
    k = 100
    for i in range(math.ceil(len(tweet_ids)/k)):
        url = f"https://api.twitter.com/2/tweets?ids={','.join(tweet_ids[k*i:(i+1)*k])}"
    
        if verbose and i%every==0: print(f'Currently at request {i}')
        tweet_jsons = get_response_v2(url, headers=headers, params=root_params)
        
        if 'data' not in tweet_jsons: continue
        for tweet in tweet_jsons['data']:
            row = get_specified_values(tweet, specified_key_order=specified_tweet_key_order_v2, params_getters=tweet_params_getters_v2)
            rows_tweets.append(row)

    return rows_tweets