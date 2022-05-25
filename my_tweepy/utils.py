import requests
import time
import copy
from collections import OrderedDict


def safe_get(dct, *keys):
    # returns value of nested dict, iterate over all nested keys
    for key in keys:
        if key in dct:
            dct = dct[key]
        else:
            return None
    return dct

def get_user_value(user_json, *keys):
    # directly extracts value from json object if it exists, else returns None
    # supports nested keys, eg. -> use: 'public_metrics', 'followers_count' to get 'followers_count'
    # from its nested dict defined below:
    # 'public_metrics': {
    #       'followers_count': 1027,
    #       'following_count': 658,
    #       'tweet_count': 451,
    #       'listed_count': 7
    # }
    return safe_get(user_json, *keys)

def get_user_values(user_dcts, key):
    # extract values from list extracted from json object
    user_values = list()
    if type(user_dcts) == list:    
        for dct in user_dcts:
            if key in dct: user_values.append(dct[key])
    
    if user_values == []:
        return None
    else:
        return list(set(user_values))

def make_decorator(function, *keys):
    # feed keys to wrapped function
    def wrapper(decorated_param):
        return function(decorated_param, *keys)
    return wrapper

def make_nested_decorator(function2, function1, key2, *keys1):
    # use output of decorated function1 as input to function2
    def wrapper(decorated_param):
        return function2(function1(decorated_param, *keys1), key2)
    return wrapper


# decorators without *args 

def safe_get2(dct, keys):
    # returns value of nested dict, iterate over all nested keys
    for key in keys:
        if key in dct:
            dct = dct[key]
        else:
            return None
    return dct

def get_user_value2(user_json, keys):
    # directly extracts value from json object if it exists, else returns None
    # supports nested keys, eg. -> use: 'public_metrics', 'followers_count' to get 'followers_count'
    # from its nested dict defined below:
    # 'public_metrics': {
    #       'followers_count': 1027,
    #       'following_count': 658,
    #       'tweet_count': 451,
    #       'listed_count': 7
    # }
    return safe_get2(user_json, keys)

def get_user_values2(user_dcts, keys):
    # extract values from list extracted from json object
    user_values = list()
    if type(user_dcts) == list:    
        for dct in user_dcts:
            extracted_value = get_user_value2(dct, keys)
            if extracted_value: user_values.append(extracted_value)
    
    if user_values == []:
        return None
    else:
        return list(OrderedDict.fromkeys(user_values))


chunk_list = lambda lst,n : [lst[i:i + n] for i in range(0, len(lst), n)]

def make_users_pamars_v1(user_ids=None, screen_names=None, N=100):
    # returns list of parameters separated up to 100 user_ids
    if (user_ids == None) and (screen_names == None):
        print("Please pass either user_ids or screen_names")
        return
    elif (user_ids != None) and (screen_names != None):
        print("Please pass either user_ids or screen_names")
        return
    else:
        params_list = list()

        if user_ids:
            key = 'user_id'
            values = user_ids
        elif screen_names:
            key = 'screen_name'
            values = screen_names
        else:
            raise f"Error, shouldn't happen."
        
        for values_chunk in chunk_list(values, n=N):
            params = dict()
            params[key] = ','.join(values_chunk) 
            params_list.append(params)
        
        return params_list
                    

def get_response_v1_1(url, headers, params, max_tries=4):
    counter = 0
    while 1:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 429:
            # limit reached
            counter = 0
            print("Sleeping for 60seconds")
            time.sleep(61)
            continue
        elif resp.status_code == 200:
            # everything ok
            return resp.json()
        else:
            counter += 1
            print(f"Response: {resp.status_code}, id: {params}")
            time.sleep(1)
            if counter > max_tries:
                return None
            else:
                continue


def extend_dict(dict1, dict2):
    """extends dict1 with values from dict 2, same keys are adding to list"""
    # make sure that first extension is to empty dict
    for key, value in dict2.items():
        dict1[key] = dict1.get(key, []) + ([value] if type(value) != list else value)

def get_response_v2(url, headers, params, max_tries=4):
    counter = 0    

    while True:
        resp = requests.get(url, headers=headers, params=params)
        
        if resp.status_code == 429 or resp.status_code == 500:
            # limit reached or high demand
            print("Sleeping for 60seconds")
            time.sleep(61)
            continue
        elif resp.status_code == 200:
            return resp.json()
        else:
            counter += 1
            print(f"Response: {resp.status_code}, id: {params_}")
            time.sleep(10)
            if counter > max_tries:
                print(f'*** Returned partial/empty. ***')
                return resp.json()
            else:
                continue
    
    return resp.json()