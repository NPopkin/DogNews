import requests
import os
from pprint import pprint
import json
import time
import datetime
import dateutil
import pandas as pd


def send_request(begin_date, end_date):
    apikey = '65762071-2d17-46f6-820a-9063fed15614'
    query = "dog"
    query_fields = "body"
    section = "news"  # https://open-platform.theguardian.com/documentation/section
    from_date = begin_date
    to_date = end_date
    #orderBy = "relevance" #f"&orderBy={orderBy}" \
    query_url = f"https://content.guardianapis.com/search?" \
                f"api-key={apikey}" \
                f"&q={query}" \
                f"&query-fields={query_fields}" \
                f"&section={section}" \
                f"&from-date={from_date}" \
                f"&to-date={to_date}" \
                f"&show-fields=headline,byline,body,publication"

    r = requests.get(query_url)
    pprint(r.json())
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
    articles = response['response']
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
    response = send_request("1950-01-01", "1960-01-01")
    df = parse_response(response)
    total += len(df)

    dates = ["1950-01-01", "1960-01-01", "1970-01-01", "1980-01-01", "1990-01-01", "2000-01-01", "2010-01-01", "2020-01-01"]
    for d in range(1, len(dates) - 1):
        begin_date = dates[d]
        end_date = dates[d + 1]
        done_flag = False
        if not done_flag:
            response = send_request(begin_date, end_date)
            df_temp = parse_response(response)
            if df_temp.shape[0] == 0:
                done_flag = True
            total += len(df_temp)
            df = pd.concat([df, df_temp])
            time.sleep(5)

    df.to_csv('guardian_1950_2020.csv', index=False)
    print('Number of articles collected: ' + str(total))


get_data()
