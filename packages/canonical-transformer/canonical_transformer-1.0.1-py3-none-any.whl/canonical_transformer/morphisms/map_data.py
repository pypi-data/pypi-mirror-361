from functools import partial
import os
import json
import pandas as pd
from canonical_transformer.isomorphisms import validate_data_isomorphism
from canonical_transformer.functionals import pipe
from .basis import standardize_file_name_for_json


def map_data_to_df(data):
    df = pd.DataFrame(data)
    df = df.set_index(df.columns[0])
    if df.index.name=='index':
        df.index.name = None
    if df.index.name == '__index__':
        df.index.name = None
    return df

def map_data_to_json(data, file_folder, file_name, option_verbose=True):
    file_name = standardize_file_name_for_json(file_name)
    file_path = os.path.join(file_folder, file_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    if option_verbose:
        print(f"| Saved json to {file_path}")
    from .map_json import map_json_to_data
    data_json = map_json_to_data(file_folder, file_name)
    if validate_data_isomorphism(data, data_json):
        return data_json
    else:
        raise ValueError(f"Failed to validate isomorphism between data and data_json")

def map_data_to_csv(data, file_folder, file_name, encoding='utf-8-sig', option_verbose=True):
    from .map_df import map_df_to_csv
    return pipe(
        map_data_to_df,
        partial(map_df_to_csv, file_folder=file_folder, file_name=file_name, encoding=encoding, option_verbose=option_verbose)
    )(data)
