import requests
import json
from datetime import date


from my_tweepy.utils import *

def make_decorator2(function, keys):
    # feed keys to wrapped function
    def wrapper(decorated_param):
        return function(decorated_param, keys)
    return wrapper

def make_nested_decorator2(function2, function1, keys2, keys1):
    # use output of decorated function1 as input to function2
    def wrapper(decorated_param):
        return function2(function1(decorated_param, keys1), keys2)
    return wrapper


user_params_getters_v2 = {
    'verified': make_decorator(get_user_value, 'verified'),
    'description': make_decorator(get_user_value, 'description'),
    'followers_count': make_decorator(get_user_value, 'public_metrics', 'followers_count'),
    'following_count': make_decorator(get_user_value, 'public_metrics', 'following_count'),
    'tweet_count': make_decorator(get_user_value, 'public_metrics', 'tweet_count'),
    'listed_count': make_decorator(get_user_value, 'public_metrics', 'listed_count'),
    'id': make_decorator(get_user_value, 'id'),
    'created_at': make_decorator(get_user_value, 'created_at'),
    'username': make_decorator(get_user_value, 'username'),
    'name': make_decorator(get_user_value, 'name'),
    'protected': make_decorator(get_user_value, 'protected'),
    'location': make_decorator(get_user_value, 'location'),  
    'profile_urls': make_nested_decorator(get_user_values, get_user_value, 'expanded_url', 'entities', 'url', 'urls'),
    'urls': make_nested_decorator(get_user_values, get_user_value, 'tag', 'entities', 'description','urls'),
    'hashtags': make_nested_decorator(get_user_values, get_user_value, 'tag', 'entities', 'description','hashtags'),
    'cashtags': make_nested_decorator(get_user_values, get_user_value, 'tag', 'entities', 'cashtags'),
    'mentions': make_nested_decorator(get_user_values, get_user_value, 'username', 'entities', 'description', 'mentions'),
    'fetched_at': lambda x: str(date.today()) # note that it takes x and doesn't use it, done like this for consistency
}

specified_key_order_v2 = ['id', 'username', 'name', 'location', 'protected', 'verified', 'created_at',
                       'fetched_at','followers_count','following_count','tweet_count',
                      'listed_count', 'profile_urls', 'urls', 'hashtags', 'cashtags', 'mentions', 'description']



user_params_getters_v1 = {
    'verified': make_decorator(get_user_value, 'verified'),
    'id': make_decorator(get_user_value, 'id_str'),
    'name': make_decorator(get_user_value, 'name'),
    'username': make_decorator(get_user_value, 'screen_name'),
    'location': make_decorator(get_user_value, 'location'),
    'description': make_decorator(get_user_value, 'description'),
    'protected': make_decorator(get_user_value, 'protected'),
    'followers_count': make_decorator(get_user_value, 'followers_count'),
    'following_count': make_decorator(get_user_value, 'friends_count'),
    'listed_count': make_decorator(get_user_value, 'listed_count'),
    'favourites_count': make_decorator(get_user_value, 'favourites_count'),
    'tweet_count': make_decorator(get_user_value, 'statuses_count'),
    'default_profile': make_decorator(get_user_value, 'default_profile'),
    'default_profile_image': make_decorator(get_user_value, 'default_profile_image'),
    'created_at': make_decorator(get_user_value, 'created_at'),
    'urls': make_nested_decorator(get_user_values, get_user_value, 'expanded_url', 'entities', 'url', 'urls'),
    'fetched_at': lambda x: str(date.today()) # note that it takes x and doesn't use it, done like this for consistency
}


specified_key_order_v1 = ['id', 'username', 'name', 'location', 'protected', 'verified', 'created_at',
                       'fetched_at','followers_count','following_count','tweet_count', 'favourites_count',
                      'listed_count', 'urls', 'default_profile', 'default_profile_image', 'description']



tweet_params_getters_v2 = {
    'text': make_decorator(get_user_value, 'text'),
    'source': make_decorator(get_user_value, 'source'),
    'created_at': make_decorator(get_user_value, 'created_at'),
    'conversation_id': make_decorator(get_user_value, 'conversation_id'),
    'tweet_id': make_decorator(get_user_value, 'id'),
    'lang': make_decorator(get_user_value, 'lang'),
    'possibly_sensitive': make_decorator(get_user_value, 'possibly_sensitive'),
    'in_reply_to_user_id': make_decorator(get_user_value, 'in_reply_to_user_id'),
    'author_id': make_decorator(get_user_value, 'author_id'),
    'reply_settings': make_decorator(get_user_value, 'reply_settings'),
    'retweet_count': make_decorator(get_user_value, 'public_metrics', 'retweet_count'),
    'reply_count': make_decorator(get_user_value, 'public_metrics', 'reply_count'),
    'like_count': make_decorator(get_user_value, 'public_metrics', 'like_count'),
    'quote_count': make_decorator(get_user_value, 'public_metrics', 'quote_count'),
    'urls': make_nested_decorator(get_user_values, get_user_value, 'expanded_url', 'entities', 'urls'),
    'typed_urls': make_nested_decorator(get_user_values, get_user_value, 'url', 'entities', 'urls'),
    'unwound_urls':make_nested_decorator(get_user_values, get_user_value, 'unwound_url', 'entities', 'urls'),
    'display_urls':make_nested_decorator(get_user_values, get_user_value, 'display_url', 'entities', 'urls'),
    'hashtags': make_nested_decorator(get_user_values, get_user_value, 'tag', 'entities', 'hashtags'), 
    'cashtags': make_nested_decorator(get_user_values, get_user_value, 'tag', 'entities', 'cashtags'),
    'mentions': make_nested_decorator(get_user_values, get_user_value, 'username', 'entities', 'mentions'),
    'referenced_tweets_types': make_nested_decorator(get_user_values, get_user_value, 'type', 'referenced_tweets'),
    'referenced_tweets_ids': make_nested_decorator(get_user_values, get_user_value, 'id', 'referenced_tweets'),
    'context_annotations_domain_ids': make_nested_decorator2(get_user_values2, get_user_value2, ['domain', 'id'], ['context_annotations']),
    'context_annotations_domain_names': make_nested_decorator2(get_user_values2, get_user_value2, ['domain', 'name'], ['context_annotations']),
    'context_annotations_entity_names': make_nested_decorator2(get_user_values2, get_user_value2, ['entity', 'name'], ['context_annotations']),
    'fetched_at': lambda x: str(date.today()) # note that it takes x and doesn't use it, done like this for consistency
}


specified_tweet_key_order_v2 = ['tweet_id', 'conversation_id', 'author_id', 'created_at', 'fetched_at',  'lang',
                                'possibly_sensitive', 'source', 'reply_settings', 'retweet_count', 'reply_count',
                                'like_count', 'quote_count', 'in_reply_to_user_id', 'referenced_tweets_types', 
                                'referenced_tweets_ids', 'urls', 'unwound_urls', 'display_urls', 'typed_urls',
                                'hashtags', 'cashtags', 'mentions', 'context_annotations_domain_ids',
                                'context_annotations_domain_names', 'context_annotations_entity_names', 'text']



def get_specified_values(fetched_json, specified_key_order=None, params_getters=None):
    if specified_key_order == None:
        raise 'please specify key order'

    if params_getters == None:
        raise 'please specify params getters'

    specified_values = list()
    
    for specified_key in specified_key_order:
        value = None
        
        if specified_key in params_getters:
            getter = params_getters[specified_key]
            value = getter(fetched_json)
            
        specified_values.append(value)
    
    return specified_values

def get_specified_tweet_values(tweet_json, specified_key_order=None, version=2):
    if version == 2:
        tweet_params_getters = tweet_params_getters_v2
        if specified_key_order == None: specified_key_order = specified_tweet_key_order_v2
    else:
        raise "Specify correct version, only version 2 supported"
    
    specified_values = list()
    
    for specified_key in specified_key_order:
        value = None
        
        if specified_key in tweet_params_getters:
            getter = tweet_params_getters[specified_key]
            value = getter(tweet_json)
            
        specified_values.append(value)
    
    return specified_values