
# Imports
from pymongo import MongoClient
import json
#import libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

df = pd.read_csv('IMDB-Movie-Data.csv')
df['Movie_id'] = range(0, 1000)

# List of columns required
cols = ['Title', 'Genre', 'Actors', 'Director']

# check null
df[cols].isnull().values.any()
# function to concat all req cols into string


def all_features(data):
    important_features = []
    for i in range(0, data.shape[0]):
        important_features.append(
            data['Title'][i]+' '+data['Genre'][i]+' '+data['Actors'][i]+' '+data['Director'][i])
    return important_features


df['important_features'] = all_features(df)
# convert text to matrix of token counts
cm = CountVectorizer().fit_transform(df['important_features'])
# cosine similarity
cs = cosine_similarity(cm)


def top_match(title, rankUpto, cs):
    if(df[df.Title == title]['Movie_id'].empty):
        print('The movie not in the list !!')
        return
    else:
        movie_id = df[df.Title == title]['Movie_id'].values[0]

    scores = list(enumerate(cs[movie_id]))

    # sort list based on similarity value

    sorted_list = sorted(scores, key=lambda x: x[1], reverse=True)
    sorted_list = sorted_list[1:]

    rank = 0
    result_list = []
    for item in sorted_list:
        movie_title = df[df.Movie_id == item[0]]['Title'].values[0]
        movie_id=item[0]
        rank += 1
        dict={"rank":rank,"movie_title":movie_title,"similarity":round(item[1]*100, 2),"id":movie_id}
        dict_copy = dict.copy()
        result_list.append(dict_copy)

        if(rank >= rankUpto):
            break
    return result_list


def all_features_top10(data):
    top10 = []
    for i in range(0, data.shape[0]):
        temp = top_match(data['Title'][i], 20, cs)
        top10.append(temp)
    return top10


df['top10_matches'] = all_features_top10(df)


# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://dbUser:dbUser@cluster0.clcld.mongodb.net/movies?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")

db = client['movies']
collection = db['movies']
df.reset_index(inplace=True)
data_dict = df.to_dict("records")
# Insert collection
collection.insert_many(data_dict)


# mongodb+srv://dbUser:dbUser@cluster0.clcld.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
