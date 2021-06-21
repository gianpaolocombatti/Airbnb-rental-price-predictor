import pandas as pd
import numpy as np
import re
import os
path = os.getcwd()
pickle_path = os.path.abspath(os.path.join(path, './AirBnB.pkl'))
nc_path = os.path.abspath(os.path.join(path, './asheville_nc_listings.csv'))
austin_path = os.path.abspath(os.path.join(path, './austin_tx_listings.csv'))
broward_path = os.path.abspath(os.path.join(path, './broward_fl_listings.csv'))
cambridge_path = os.path.abspath(os.path.join(path, './cambridge_ma_listings.csv'))
chicago_path = os.path.abspath(os.path.join(path, './chicago_il_listings.csv'))
columbus_path = os.path.abspath(os.path.join(path, './columbus_oh_listings.csv'))


def clean_bathrooms(df):
    # Not Used
    idx = 0
    out = []
    for item in df['bathrooms_text']:
        idx += 1
        item = str(item)
        if item.find('half') != -1:
            num = .5
            out.append(num)
        elif not hasNumbers(item):
            out.append(np.nan)
        else:
            try:
                num = []
                for t in item.split():
                    try:
                        num.append(float(t))
                    except ValueError:
                        pass
                out.append(num)
            except:
                out.append(np.nan)
        if len(out) != idx:
            print(item)
            print("Error")
    df.drop(columns=['bathrooms_text', 'bathrooms'], inplace=True)
    df['bathrooms'] = out
    return df


def hasNumbers(input):
    try:
        out = any(char.isdigit() for char in input)
    except:
        out = False
    return out


def load_data():
    cities = ['Asheville, NC', 'Austin, TX', 'Broward, FL', 'Cambridge, MA', 'Chicago, IL', 'Columbus, OH']
    paths = [nc_path, austin_path, broward_path, cambridge_path, chicago_path, columbus_path]
    df = pd.DataFrame()
    for city, path in zip(cities, paths):
        city_df = pd.read_csv(path)
        city_df['City'] = city
        if city == 'Asheville, NC':
            df = city_df
        else:
            df = pd.concat([city_df, df])

    drop_cols = ['host_picture_url', 'host_thumbnail_url', 'listing_url', 'picture_url', 'host_has_profile_pic']

    df = df.drop(columns=drop_cols)
    for col in df.columns:
        df[col].fillna(value="Missing", inplace=True)
    df.to_pickle(pickle_path)
    print("Saved Pickle Successfully")
    # print(df.columns)
    print(df.shape)
    return df

