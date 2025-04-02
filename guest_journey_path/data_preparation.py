import pandas as pd

def prepare_data(data_path):
    # read file and convert to DataFrame
    df = pd.read_csv(data_path)

    # create ordered sequences lists
    # subset path matrix
    path_matrix = df[['hollywood', 'minion_land', 'far_far_away', 'lost_world', 'ancient_egypt', 'scifi_city', 'new_york']]
    path_matrix = path_matrix[path_matrix.any(axis='columns')]

    # sort path matrix to return paths
    ordered_sequences = path_matrix.apply(lambda x: x.dropna().sort_values().index.tolist(), axis=1)

    # extract relevent responses from survey data
    target_rows = path_matrix.index.values.tolist()
    target_entries = df.loc[target_rows]

    # concatenate ordered sequences to target_entries data for easy retrival
    target_entries = pd.concat([target_entries, ordered_sequences], axis=1)
    target_entries = target_entries.rename(columns={'Unnamed: 0' : 'response_id', 0:'sequences'})

    return target_entries



