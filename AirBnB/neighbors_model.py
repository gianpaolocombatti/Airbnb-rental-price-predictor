from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np

from sklearn.neighbors import NearestNeighbors


class howdy_neighbor:

    def __init__(self, dataframe, columns_to_keep, columns_to_encode):
        self.columns_to_keep = columns_to_keep
        self.columns_to_encode = columns_to_encode
        self.dataframe = dataframe
        self.process_listing_df()
        self.model_new()

    def predict_w_neigh(self, obs):
        # provides nearest neightbors, 20, and output prediction:
        # make sure observation is in [[features]] format

        model = self.model
        output = model.kneighbors(obs)
        average = []
        for x in output[1]:
            for y in x:
                average.append(self.clean_df.iloc[y]['price'])
        return (np.mean(average), output[1])

    def process_listing_df(self):
        # preprocess listing df from inside airbnb
        # returns df with reduced and cleaned columns
        # also encodes categorical columns

        # cleans price column
        columns = self.columns_to_keep
        if 'price' not in columns:
            columns.append('price')
        df_copy = self.dataframe.copy()
        temp = []
        for x in df_copy['price']:
            x = x.strip('$')
            x = x.replace(',', '')
            x = float(x)
            temp.append(x)
        df_copy['price'] = temp

        # personal categorical encoder, meant to be run on df
        # also reduce features in listings:

        df_copy = df_copy[columns]
        cols_encode = self.columns_to_encode
        if 'room_type' in cols_encode:
            for x in df_copy['room_type'].value_counts().index:
                df_copy[x] = 0
                alpha = x
                for i, y in enumerate(df_copy['room_type']):
                    if y == alpha:
                        df_copy[alpha][i] = 1
                    else:
                        pass
            df_copy.drop(columns='room_type', inplace=True)
            cols_encode.remove('room_type')
        if len(cols_encode) > 0:
            for y in cols_encode:
                for i, x in enumerate(df_copy[y].value_counts().index):
                    df_copy.loc[df_copy[y] == x, y] = i

        # process bathrooms text column (if present)
        # transform into private and shared bathrooms columns
        if 'bathrooms_text' in columns:
            shared = []
            private = []
            df_copy['bathrooms_text'] = df_copy['bathrooms_text'].astype('string')
            for x in df_copy['bathrooms_text']:
                try:
                    x = x.split()
                    if 'shared' in x:
                        shared.append(float(x[0]))
                        private.append(0)
                    else:
                        try:
                            a = float(x[0])
                            private.append(a)
                            shared.append(0)
                        except:
                            private.append(.5)
                            shared.append(0)
                except:
                    shared.append(np.nan)
                    private.append(np.nan)

            df_copy.drop(columns='bathrooms_text', inplace=True)
            df_copy['shared_bathrooms'] = shared
            df_copy['private_bathrooms'] = private

        # replace nans
        for y in df_copy.columns:
            df_copy[y].replace(np.nan, 0, inplace=True)

        # feature scaling
        columns = df_copy.columns
        columns = columns.drop('price')
        for y in columns:
            df_copy[y] = (df_copy[y] - df_copy[y].mean()) / df_copy[y].std()
        for y in df_copy.columns:
            df_copy[y].replace(np.nan, 0, inplace=True)

        self.clean_df = df_copy

    def model_new(self):
        # input an observation and training dataframe to get model:
        neigh = NearestNeighbors(n_neighbors=20, algorithm='brute')
        df_temp = self.clean_df.drop(columns='price')
        neigh.fit(df_temp)

        self.model = neigh
