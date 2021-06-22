from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.impute import SimpleImputer
from category_encoders import OneHotEncoder
from sklearn.preprocessing import StandardScaler

def bathroom_text_encoder(df):
  df1 = df.copy()
  df1['bathrooms_text'] = df['bathrooms_text'].astype('string')
  shared = []
  private = []
  for x in df1['bathrooms_text']:

    try:
      x = x.split()
      if x[0] == 'shared' or x[0] == 'Shared':
        shared.append(1)
        private.append(0)
      elif x[0] == 'private' or x[0] == 'Private':
        shared.append(0)
        private.append(1)
      elif x[1] == 'shared' or x[1] == 'Shared':
        shared.append(float(x[0]))
        private.append(0)
      else:
        shared.append(0)
        private.append(float(x[0]))
    except:
      shared.append(0)
      private.append(0)

  return shared, private

def pipeline_model(df, cols_to_keep):

  #handles bathroom_text:
  df_copy = df[cols_to_keep]

  shared, private = bathroom_text_encoder(df_copy)

  if shared:
    df_copy.drop(columns='bathrooms_text', inplace=True)
    df_copy['shared_bathrooms'] = shared
    df_copy['private_bathrooms'] = private
    cols_to_keep.remove('bathrooms_text')

  X = df_copy.drop(columns=['price'])
  y = df_copy['price']

  pipe = make_pipeline(OneHotEncoder(cols=['room_type']), StandardScaler(), SimpleImputer(strategy='most_frequent'), KNeighborsRegressor(algorithm='brute', n_neighbors=20))

  pipe.fit(X, y)
  oh = pipe.named_steps['onehotencoder']
  stand = pipe.named_steps['standardscaler']
  simp = pipe.named_steps['simpleimputer']
  kneigh = pipe.named_steps['kneighborsregressor']

  return pipe, oh, stand, simp, kneigh
