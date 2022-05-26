import pandas as pd
import ast
import numpy as np
import os
import sys
import my_tweepy.utils, my_tweepy.functions, my_tweepy.json_getters

import dataset_builder.utils

from tqdm import tqdm

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
    df_arxiv['arxiv_identifiers'] = all_arxiv_identifiers_list


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

    tweetid2arxiv = dict(zip(df.tweet_id.astype(str), df.arxiv_identifiers))
    df_tweets['arxiv_identifiers'] = df_tweets['tweet_id'].astype(str).map(tweetid2arxiv)


    column_author_mapper = dict(list(map(lambda x: (x, f"author.{x}"), df_users.columns)))
    df_users.rename(columns = column_author_mapper, inplace = True)
    # df_users.rename(columns={'author.author_id':'author_id'}, inplace=True)

    column_arxiv_mapper = dict(list(map(lambda x: (x, f"arxiv.{x}"), df_arxiv.columns)))
    df_arxiv.rename(columns = column_arxiv_mapper, inplace=True)


    # convert created_at to datatime object
    df_users['author.created_at'] = pd.to_datetime(df_users['author.created_at'], format='%a %b %d %H:%M:%S %z %Y')
    df_tweets['created_at'] = pd.to_datetime(df_tweets['created_at'], format='%Y-%m-%dT%H:%M:%S.%fZ')


    def prepare_time(timestamp):
        return timestamp.hour + timestamp.minute/60 + timestamp.second/3600


    df_tweets['created_at_hours'] = df_tweets['created_at'].apply(prepare_time)
    df_users['author.created_at_seconds'] = df_users['author.created_at'].apply(lambda x: int(x.timestamp()))
    df_tweets['created_at_seconds'] = df_tweets['created_at'].apply(lambda x: int(x.timestamp()))

    list_columns = ['urls', 'hashtags', 'cashtags', 'mentions', 'context_annotations_domain_ids', 
                    'context_annotations_domain_names', 'context_annotations_entity_names',
                    'arxiv_identifiers', 'referenced_tweets_ids', 'referenced_tweets_types',
                    'unwound_urls', 'display_urls', 'typed_urls']

    value_columns = ['tweet_id', 'created_at', 'fetched_at', 'lang', 'possibly_sensitive', 'source',
                    'reply_settings', 'retweet_count', 'reply_count', 'like_count', 'quote_count',
                    'in_reply_to_user_id',
                    'created_at_hours', 'created_at_seconds'
                    ]

    arxiv_columns = ['arxiv.title', 'arxiv.authors', 'arxiv.summary',
                    'arxiv.comment', 'arxiv.primary_category', 'arxiv.journal_ref']

    thread_columns = ['text', 'arxiv.title', 'arxiv.authors', 'arxiv.summary', 'arxiv.comment',
    'arxiv.primary_category', 'arxiv.journal_ref']

    def merge_instances(df, sep='<ARXIV_SEP>'):
        merged = dict()
        for column in df.columns:
            merged[column] = [f'{sep}'.join(df[column].astype(str).values)]
        return merged
    

    empty_row = dict(zip(arxiv_columns, [None]*len(arxiv_columns)))

    arxiv_tweet_parts = pd.DataFrame()

    for arxiv_identifiers in tqdm(df_tweets['arxiv_identifiers'].values):
        arxiv_identifiers = set(arxiv_identifiers)
        if len(arxiv_identifiers) != 0:
            df_tweet_papers = df_arxiv[df_arxiv['arxiv.arxiv_identifiers'].isin(arxiv_identifiers)]
            df_arxiv_filtered = pd.DataFrame.from_dict(merge_instances(df_tweet_papers[arxiv_columns]))
        else:
            df_arxiv_filtered = empty_row
        arxiv_tweet_parts = arxiv_tweet_parts.append(df_arxiv_filtered,ignore_index=True)
    

    df_tweets = pd.concat([df_tweets, arxiv_tweet_parts], axis=1)
    df_tweets.reset_index(drop=True, inplace=True)

    df_final = pd.DataFrame()
    thread_sep = '<THREAD_SEP>'

    for conversation_id in tqdm(df.conversation_id.unique()):
        mask = df.conversation_id == str(conversation_id)
        
        thread_tweets = df_tweets[df_tweets['conversation_id'] == str(conversation_id)]
        thread_tweets = thread_tweets.sort_values(by='tweet_id')
        if len(thread_tweets) == 0: continue
        thread_author_id = thread_tweets['author_id'].values[0]
        thread_user = df_users[df_users['author.author_id'] == thread_author_id]
        thread_user.reset_index(drop=True, inplace=True)
        
        part_dict = dict()
        
        # handle text columns
        for thread_column in thread_columns:
            column_values = thread_tweets[thread_column].values
            column_values = list(filter(lambda x: (str(x) != 'nan') and (str(x) != 'None') and (str(x) != ''), column_values))
            row_element = f'{thread_sep}'.join(column_values)
            part_dict[thread_column] = [row_element]

        # handle list columns
        for list_column in list_columns:
            column_values = thread_tweets[list_column].values
            column_values = list(map(lambda x: ast.literal_eval(str(x)) if (str(x) != 'nan' and (str(x) != 'None')) else [], column_values))
            part_dict[list_column] = part_dict.get(list_column, []) + [column_values]

        # handle value columns
        for value_column in value_columns:
            column_values = thread_tweets[value_column].values
            part_dict[value_column] = [column_values]
        
        df_part = pd.DataFrame.from_dict(part_dict)
        df_part = pd.concat([df_part, thread_user], axis=1)
        df_final = df_final.append(df_part)
        

    df_final.reset_index(drop=True, inplace=True)


    
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