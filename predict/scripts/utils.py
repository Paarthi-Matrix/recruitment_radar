import pandas as pd

def load_data(path):
    """
    Load dataset from the given path.
    """
    return pd.read_csv(path)
