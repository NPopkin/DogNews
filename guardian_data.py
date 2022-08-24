import requests
import os
from pprint import pprint
import json
import time
import datetime
import dateutil
import pandas as pd


def send_request(i, begin_date, end_date):
    apikey = '65762071-2d17-46f6-820a-9063fed15614'
    query = "dog"
    query_fields = "body"
    section = "news"  # https://open-platform.theguardian.com/documentation/section
    from_date = begin_date
    to_date = end_date
    page_size="50"
    page=i
    #orderBy = "relevance" #f"&orderBy={orderBy}" \
    query_url = f"https://content.guardianapis.com/search?" \
                f"api-key={apikey}" \
                f"&q={query}" \
                f"&query-fields={query_fields}" \
                f"&section={section}" \
                f"&from-date={from_date}" \
                f"&to-date={to_date}" \
                f"&page-size={page_size}" \
                f"&page={page}" \
                f"&show-fields=headline,byline,publication"
#body
    r = requests.get(query_url)
    pprint(r.json())
    return r.json()



def is_news(article):
    if 'type' not in article:
        return False
    if article['type'] == 'article' and (
            article['sectionId'] == 'news' or article['sectionName'] == 'News'):
        return True
    return False


def add_data(data, article, col):
    if col in article:
        data[col].append(article[col])
    else:
        data[col].append(None)


def parse_response(response):
    '''Parses and returns response as pandas data frame.'''
    data = {'webPublicationDate':[],
            'webTitle': [],
            }
    if response['response']['status']=='error':
        return pd.DataFrame()
    articles = response['response']['results']
    for article in articles:  # For each article, make sure it falls within our date range
        if is_news(article):
            add_data(data, article, 'webPublicationDate')
            add_data(data, article, 'webTitle')
    return pd.DataFrame(data)


def get_data():
    '''Sends and parses request/response to/from NYT Archive API for given dates.'''
    total = 0
    if not os.path.exists('headlines'):
        os.mkdir('headlines')
    response = send_request('1', "1990-01-01", "2000-01-01")
    df = parse_response(response)
    total += len(df)

    dates = [ "1990-01-01", "2000-01-01", "2010-01-01", "2020-01-01"]
    for d in range(1, len(dates) - 1):
        begin_date = dates[d]
        end_date = dates[d + 1]
        done_flag = False
        for i in range(1, 50):
            if not done_flag:
                response = send_request(str(i), begin_date, end_date)
                df_temp = parse_response(response)
                if df_temp.shape[0] == 0:
                    done_flag = True
                total += len(df_temp)
                df = pd.concat([df, df_temp])
                time.sleep(1)

    df.to_csv('guardian_2000_2020.csv', index=False)
    print('Number of articles collected: ' + str(total))


get_data()

