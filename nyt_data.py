import requests
import os
from pprint import pprint
import json
import time
import datetime
import dateutil
import pandas as pd


def send_request(i, begin_date, end_date):
    apikey = 'ijobGfJ5GXleHBMzVTpoySL5vvhMT6Vc'
    query = "dog"
    document_type = "article"
    filter_query = "\"title:(\"dog\") and body:(\"dog\") \""  # http://www.lucenetutorial.com/lucene-query-syntax.html
    page = i  # <0-100>
    sort = "relevance"  # newest, oldest,relevance
    query_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?" \
                f"q={query}" \
                f"&api-key={apikey}" \
                f"&begin_date={begin_date}" \
                f"&end_date={end_date}" \
                f"&document_type={document_type}" \
                f"&fq={filter_query}" \
                f"&page={page}" \
                f"&sort={sort}"
    r = requests.get(query_url)
    # pprint(r.json())
    return r.json()


def is_news(article):
    if 'type_of_material' not in article:
        return False
    if 'document_type' not in article:
        return False
    if article['document_type'] == 'article' and (
            article['type_of_material'] == 'News' or article['type_of_material'] == 'Archives'):
        return True
    return False


def add_data(data, article, col):
    if col in article:
        data[col].append(article[col])
    else:
        data[col].append(None)


def parse_response(response):
    '''Parses and returns response as pandas data frame.'''
    data = {'headline': [],
            'date': [],
            'document_type': [],
            'type_of_material': [],
            'section_name': [],
            'keywords': [],
            'snippet': [],
            'source': [],
            'lead_paragraph': []}
    articles = response['response']['docs']
    for article in articles:  # For each article, make sure it falls within our date range
        if is_news(article):
            date = dateutil.parser.parse(article['pub_date']).date()
            data['date'].append(date)
            data['headline'].append(article['headline']['main'])
            keywords = [keyword['value'] for keyword in article['keywords'] if keyword['name'] == 'subject']
            data['keywords'].append(keywords)
            add_data(data, article, 'section_name')
            add_data(data, article, 'document_type')
            add_data(data, article, 'type_of_material')
            add_data(data, article, 'snippet')
            add_data(data, article, 'lead_paragraph')
            add_data(data, article, 'source')
    return pd.DataFrame(data)


def get_data():
    '''Sends and parses request/response to/from NYT Archive API for given dates.'''
    total = 0
    if not os.path.exists('headlines'):
        os.mkdir('headlines')
    response = send_request('0', "19500101", "19600101")
    df = parse_response(response)
    total += len(df)

    dates = ["19500101", "19600101", "19700101", "19800101", "19900101", "20000101", "20100101", "20200101"]  # YYYYMMDD
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
                time.sleep(7)

    df.to_csv('nyt_1950_2020.csv', index=False)
    print('Number of articles collected: ' + str(total))


get_data()
