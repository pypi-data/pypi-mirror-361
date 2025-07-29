import os
import json
from .map_data import map_data_to_df
from .map_df import map_df_to_csv
from canonical_transformer.functionals import pipe
from functools import partial


def map_json_to_data(file_folder, file_name):
    file_path = os.path.join(file_folder, file_name)
    with open(file_path, 'r') as f:
        return json.load(f)
    
def map_json_to_df(file_folder, file_name):
    return pipe(
        map_json_to_data,
        map_data_to_df
    )(file_folder, file_name)

def map_json_to_csv(file_folder, file_name, encoding='utf-8-sig', option_verbose=True, file_folder_csv=None, file_name_csv=None):
    file_folder_csv = file_folder if file_folder_csv is None else file_folder_csv
    file_name_csv = file_name.replace('.json', '.csv').replace('json-', 'dataset-') if file_name_csv is None else file_name_csv
    df = map_json_to_df(file_folder, file_name)
    return map_df_to_csv(df, file_folder_csv, file_name_csv, encoding, option_verbose)