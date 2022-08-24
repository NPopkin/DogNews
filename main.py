import gensim
import pandas as pd
import numpy as np
# to preprocess text
import re
import nltk
from gensim.models import Word2Vec
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
import matplotlib.cm as cm
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


# First load and remove unnecessary/empty data from the dataset
def get_data():
    # load data set
    data = pd.read_csv("../DogNews/nyt_1950_2020.csv")
    # change date to type datetime
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    # drop any empty lead paragraphs
    data.dropna(subset=['lead_paragraph'], inplace=True)
    # drop snippet column
    data.drop(columns=['snippet'], inplace=True)
    # drop duplicates
    lead_paragraph = data['lead_paragraph']
    data.drop_duplicates(subset='lead_paragraph', keep='last', inplace=True)

    headline = data['headline']
    data.drop_duplicates(subset=['headline', 'date'], keep='last', inplace=True)
    return data


def process_text(text):
    # convert to lowercase, remove punctuations and characters and strip
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
    # removes non alpha char
    regex = re.compile('[^a-zA-Z]')
    regex.sub('', text)
    # tokenize
    text_lst = text.split()
    # remove stopwords
    stopwords = nltk.corpus.stopwords.words("english")
    text_lst = [word for word in text_lst if word not in stopwords]

    # stemming (remove -ing, -ly, ...)
    ps = nltk.stem.porter.PorterStemmer()
    text_lst = [ps.stem(word) for word in text_lst]

    # lemmatisation (convert the word into root word)
    lem = nltk.stem.wordnet.WordNetLemmatizer()
    text_lst = [lem.lemmatize(word) for word in text_lst]

    # convert back to string from list
    text = " ".join(text_lst)
    return text


data = get_data()
data["lead_paragraph_clean"] = data["lead_paragraph"].apply(lambda x: process_text(x))
data["headline_clean"] = data["headline"].apply(lambda x: process_text(x))

# Word2Vec Model

tokens = data["lead_paragraph_clean"].apply(lambda x: nltk.word_tokenize(x))
w2v_model = Word2Vec(sentences=tokens, vector_size=100, window=8, min_count=100, alpha=0.03,seed=42, workers=4)
vocab=w2v_model.wv.key_to_index



# topic modeling
dictionary = gensim.corpora.Dictionary(tokens)
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
# Create doc2bow dictionary
bow_corpus = [dictionary.doc2bow(doc) for doc in tokens]

# Create TFIDF model
from gensim import corpora, models
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
# LDA model
if __name__ == '__main__':
    lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=4, id2word=dictionary, passes=2, workers=4)
    for idx, topic in lda_model_tfidf.print_topics(-1):
        print('Topic: {} Word: {}'.format(idx, topic))
