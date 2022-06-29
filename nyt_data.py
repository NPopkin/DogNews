import requests
import os
from pprint import pprint
import json
import time
import datetime
import dateutil
import pandas as pd


def send_request(i):
    apikey = 'ijobGfJ5GXleHBMzVTpoySL5vvhMT6Vc'
    # https://api.nytimes.com/svc/search/v2/articlesearch.json?q=<QUERY>&api-key=<APIKEY>
    # Use - https://developer.nytimes.com/docs/articlesearch-product/1/routes/articlesearch.json/get to explore API
    query = "dog"
    begin_date = "19000101"  # YYYYMMDD
    end_date = "19500101"  # YYYYMMDD
    document_type = "article"
    filter_query = "\"title:(\"dog\") and body:(\"breed\") \""  # http://www.lucenetutorial.com/lucene-query-syntax.html
    page = i  # <0-100>
    sort = "relevance"  # newest, oldest
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
    if article['document_type'] == 'article' and (article['type_of_material'] == 'News' or article['type_of_material'] == 'Archives'):
        return True
    return False


def parse_response(response):
    '''Parses and returns response as pandas data frame.'''
    data = {'headline': [],
            'date': [],
            'doc_type': [],
            'material_type': [],
            'section': [],
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
            if 'section' in article:
                data['section'].append(article['section_name'])
            else:
                data['section'].append(None)
            data['doc_type'].append(article['document_type'])
            if 'type_of_material' in article:
                data['material_type'].append(article['type_of_material'])
            else:
                data['material_type'].append(None)
            if 'snippet' in article:
                data['snippet'].append(article['snippet'])
            else:
                data['snippet'].append(None)
            if 'lead_paragraph' in article:
                data['lead_paragraph'].append(article['lead_paragraph'])
            else:
                data['lead_paragraph'].append(None)
            if 'source' in article:
                data['source'].append(article['source'])
            else:
                data['source'].append(None)
            keywords = [keyword['value'] for keyword in article['keywords'] if keyword['name'] == 'subject']
            data['keywords'].append(keywords)
    return pd.DataFrame(data)


def get_data():
    '''Sends and parses request/response to/from NYT Archive API for given dates.'''
    total = 0
    if not os.path.exists('headlines'):
        os.mkdir('headlines')
    response = send_request('0')
    pprint(response)
    df = parse_response(response)
    total += len(df)
    done_flag=False
    for i in range(1, 99):
        if not done_flag:
            print(str(i))
            response = send_request(str(i))
            pprint(response)
            df_temp = parse_response(response)
            print (df_temp)
            print (df_temp.shape[0])
            total += len(df_temp)
            df = pd.concat([df,df_temp])
            time.sleep(7)

    df.to_csv('nyt_1900_1950.csv', index=False)
    print('Number of articles collected: ' + str(total))


get_data()
