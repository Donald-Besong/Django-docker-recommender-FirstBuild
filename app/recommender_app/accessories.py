import numpy as np
import pandas as pd
import string
import pickle
import sys
import os
from .validators import validate_new_data
# from validators import validate_new_data
# sys.path.append("..")
from donald_project import settings
from pathlib import Path
import inspect
import cProfile
import pstats


def iterRead(csvfile):

    dtypes = {
        'isbn': str,
        'user_id': str,
        'rating': int
    }
    data = pd.read_csv(csvfile, dtype=dtypes)
    # print(data)
    return data

def unpickle(pklfile):
    file_dir = Path(settings.MEDIA_ROOT) / pklfile
    bp_file = open(file_dir, 'rb')
    unpickled = pickle.load(bp_file)
    return unpickled

def unpickleS3():
    import boto3
    s3_client = boto3.client(
        's3',
        region_name='eu-west-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    # print("******** bucket {} from ****{}**************".format(settings.AWS_STORAGE_BUCKET_NAME, inspect.stack()[0][3]))
    model_pklfile = 'static/model.pkl'
    model_data = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=model_pklfile)
    model_body = model_data['Body'].read()
    model = pickle.loads(model_body)
    bp_pklfile = 'static/book_pivot.pkl'
    bp_data = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=bp_pklfile)
    bp_body = bp_data['Body'].read()
    book_pivot = pickle.loads(bp_body)

    rwb_pklfile = 'static/ratings_with_books.pkl'
    rwb_data = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=rwb_pklfile)
    rwb_body = rwb_data['Body'].read()
    ratings_with_books = pickle.loads(rwb_body)
    return model, book_pivot, ratings_with_books

def iterReadS3(csvfile):
    dtypes = {
        'isbn': str,
        'user_id': str,
        'rating': int
    }
    # new_data = pd.read_csv(csvfile, dtype=dtypes)
    # print(data)
    import boto3
    s3_client = boto3.client(
        's3',
        region_name='eu-west-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    new_data = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=csvfile)
    new_data = pd.read_csv(new_data['Body'], dtype=dtypes)

    return new_data

def user_movies(csvfile):
    # *****************begin reading arguments
    new_data_raw = iterRead(csvfile)
    assert validate_new_data(new_data_raw)
    new_data = new_data_raw.copy()[['isbn', 'rating']]

    bp_pklfile = 'book_pivot.pkl'
    book_pivot = unpickle(bp_pklfile)
    book_pivot_deep = book_pivot.copy()
    book_pivot_deep.reset_index(inplace=True)
    ind = book_pivot.index
    book_pivot_deep['isbn'] = ind
    model_pklfile = 'model.pkl'
    model = unpickle(model_pklfile)
    rwb_pklfile = 'ratings_with_books.pkl'
    ratings_with_books = unpickle(rwb_pklfile)
    d = book_pivot_deep.merge(new_data, on='isbn', how='left')  # align new_data PROBLEM
    # to do: fill the isbn in the new data to ahave ten digits. don by saving correct datatypes
    d.rating.fillna(0, inplace=True)
    # print("#***{}********{}*********".format(type(ratings_with_books), type(new_data)))
    # ********************
    new_rating = np.array(d.rating).reshape(1, -1)  # because rating is the column name of our new data
    distance, suggestion = model.kneighbors(new_rating)
    # todo:
    # 1. ensure that new_data_raw.user_id is all the same value
    # 2. ensure that new_data_raw.isbn are each unique and are in books
    # 3. ensure that len(new_data) >= 20
    user_ids = book_pivot.columns
    match0 = suggestion[0][0]  # match0 is the position of a column in bp
    match0 = user_ids[match0]  # because the columns of bp = user_id

    match1 = suggestion[0][1]
    match1 = user_ids[match1]
    match2 = suggestion[0][2]
    match2 = user_ids[match2]

    match0_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match0, 'isbn'])
    match1_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match1, 'isbn'])
    match2_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match2, 'isbn'])
    newuser_titles = set(new_data.isbn)
    match_titles = match0_titles.union(match1_titles)  # or the | operator
    match_titles = match_titles.union(match2_titles)
    recommendation_titles = match_titles.difference(newuser_titles)
    # print("match0={},match1={},match1={}".format(match0, match1, match2))
    # print(len(match0_titles))
    # print(len(match1_titles))
    # print(len(match2_titles))
    # print(len(match_titles)); these are isbn. filter titles from ratings
    k = lambda x: x in recommendation_titles
    booksi = list(map(k, ratings_with_books.isbn))
    books = list(set(ratings_with_books.title[booksi]))
    randmax = len(books)
    selectedi = np.random.randint(0, randmax, 5)
    selected_books = [books[i] for i in selectedi]
    return selected_books  # reshape(1,-1) #book_pivot


def user_movies_s3(csvfile):
    # *****************begin reading arguments
    new_data_raw = iterReadS3(csvfile)
    assert(validate_new_data(new_data_raw))
    print("***book_pivot {} ".format('xxxxxxxxxxxxxx'))
    model, book_pivot, ratings_with_books = unpickleS3()

    new_data = new_data_raw.copy()[['isbn', 'rating']]
    book_pivot_deep = book_pivot.copy()
    book_pivot_deep.reset_index(inplace=True)
    ind = book_pivot.index
    book_pivot_deep['isbn'] = ind

    d = book_pivot_deep.merge(new_data, on='isbn', how='left')  # align new_data PROBLEM
    # to do: fill the isbn in the new data to ahave ten digits. don by saving correct datatypes
    d.rating.fillna(0, inplace=True)

    new_rating = np.array(d.rating).reshape(1, -1)  # because rating is the column name of our new data
    distance, suggestion = model.kneighbors(new_rating)
    user_ids = book_pivot.columns
    match0 = suggestion[0][0]  # match0 is the position of a column in bp
    match0 = user_ids[match0]  # because the columns of bp = user_id

    match1 = suggestion[0][1]
    match1 = user_ids[match1]
    match2 = suggestion[0][2]
    match2 = user_ids[match2]

    match0_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match0, 'isbn'])
    match1_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match1, 'isbn'])
    match2_titles = set(ratings_with_books.loc[ratings_with_books.user_id == match2, 'isbn'])
    newuser_titles = set(new_data.isbn)
    match_titles = match0_titles.union(match1_titles)  # or the | operator
    match_titles = match_titles.union(match2_titles)
    recommendation_titles = match_titles.difference(newuser_titles)
    k = lambda x: x in recommendation_titles
    booksi = list(map(k, ratings_with_books.isbn))
    books = list(set(ratings_with_books.title[booksi]))
    randmax = len(books)
    selectedi = np.random.randint(0, randmax, 5)
    selected_books = [books[i] for i in selectedi]
    return selected_books
