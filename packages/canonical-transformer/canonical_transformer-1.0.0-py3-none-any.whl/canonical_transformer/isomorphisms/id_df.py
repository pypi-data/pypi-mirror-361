from canonical_transformer.morphisms import *

def iD_df(df):
    return map_data_to_df(map_df_to_data(df))

def iD_data(data):
    return map_df_to_data(map_data_to_df(data))

def is_df_isomorphic(df):
    return df.equals(iD_df(df))

def is_data_isomorphic(data):
    return data == iD_data(data)