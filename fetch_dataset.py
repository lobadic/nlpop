import pandas as pd
import ast
import numpy as np
import os
import sys
import my_tweepy.utils, my_tweepy.functions, my_tweepy.json_getters

import dataset_builder.utils

def load_dataset(path='./data/nlpop_dataset.csv'):
    # load and fix format of arxiv identifiers
    df = pd.read_csv(path)
    df["arxiv_identifiers"] = df["arxiv_identifiers"].apply(lambda x: x.replace("'/", "'"))

    # parse identifiers string
    df["arxiv_identifiers"] = df["arxiv_identifiers"].apply(lambda x: ast.literal_eval(x))

    # fetch all arxiv identifiers 
    all_arxiv_identifiers = set()
    for arxiv_identifiers in df["arxiv_identifiers"].values:
        all_arxiv_identifiers.update(arxiv_identifiers)
    all_arxiv_identifiers_list = list(all_arxiv_identifiers)

    # fetch arxiv data
    arxiv_reponse = dataset_builder.utils.fetch_arxiv_data(all_arxiv_identifiers_list)
    rows = np.array(list(map(dataset_builder.utils.parse_result, arxiv_reponse)))

    # create arxiv dataframe
    pd_dict = dataset_builder.utils.make_dict(dataset_builder.utils.column_names, rows)
    df_arxiv = pd.DataFrame.from_dict(pd_dict)
    df_arxiv['arxiv_id'] = all_arxiv_identifiers_list


    if os.path.exists('./bearer_token.txt'):
        with open('./bearer_token.txt', 'r') as f:
            api_bearer_token = f.read().strip()
    else:
        raise 'bearer_token.txt doesnt exist'

    headers = {
        "Authorization": f"Bearer {api_bearer_token}"
    }

    root_params = {
        'expansions' : 'entities.mentions.username,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
        'tweet.fields' : 'author_id,context_annotations,conversation_id,created_at,entities,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,geo'
    }

    # load tweets and create dataframe
    rows_tweets = my_tweepy.functions.get_tweets_v2(headers, root_params, df.tweet_id.astype(str).values, verbose=True, every=25)
    df_tweets = pd.DataFrame(rows_tweets, columns = my_tweepy.json_getters.specified_tweet_key_order_v2)


    # load user data
    user_ids = df_tweets.author_id.unique()
    rows_users = my_tweepy.functions.get_users_info_v1(headers, user_ids=user_ids.tolist())
    df_users = pd.DataFrame(rows_users, columns = my_tweepy.json_getters.specified_key_order_v1)


    # prepare autor data for merging
    df_users.rename(columns={'id':'author_id'}, inplace=True)
    column_author_mapper = dict(list(map(lambda x: (x, f"author.{x}"), df_users.columns)))
    column_tweet_mapper = dict(list(map(lambda x: (x, f"tweet.{x}"), df_tweets.columns)))
    df_users.rename(columns = column_author_mapper, inplace = True)
    df_tweets.rename(columns = column_tweet_mapper, inplace = True)
    df_users.rename(columns={'author.author_id':'author_id'}, inplace=True)
    df_tweets.rename(columns={'tweet.author_id':'author_id'}, inplace=True)

    #
    df_final = pd.merge(df_users, df_tweets, on='author_id', how='left')
    df_final['tweet.created_at']

    # convert created_at to datatime object
    df_final['author.created_at'] = pd.to_datetime(df_final['author.created_at'], format='%a %b %d %H:%M:%S %z %Y')
    df_final['tweet.created_at'] = pd.to_datetime(df_final['tweet.created_at'], format='%Y-%m-%dT%H:%M:%S.%fZ')


    def prepare_time(timestamp):
        return timestamp.hour + timestamp.minute/60 + timestamp.second/3600


    df_final['tweet.created_at_hours'] = df_final['tweet.created_at'].apply(prepare_time)
    df_final['author.created_at_seconds'] = df_final['author.created_at'].apply(lambda x: int(x.timestamp()))
    df_final['tweet.created_at_seconds'] = df_final['tweet.created_at'].apply(lambda x: int(x.timestamp()))
    return df_final

if __name__ == "__main__":
    import os
    os.makedirs('./cache', exist_ok=True)
    
    df = load_dataset(path='./data/nlpop_dataset.csv')
    df.to_csv('./cache/finat.csv', sep=',', index=False)

    df = load_dataset(path='./data/train.csv')
    df.to_csv('./cache/train.csv', sep=',', index=False)

    df = load_dataset(path='./data/valid.csv')
    df.to_csv('./cache/valid.csv', sep=',', index=False)

    df = load_dataset(path='./data/test.csv')
    df.to_csv('./cache/test.csv', sep=',', index=False)