__version__ = '0.0.14'

import pkgutil
import pandas as pd # type: ignore
from io import StringIO  # noqa: F401

def load_dataset(file_name):
    data = pkgutil.get_data('pyCDM4F', f'Data/{file_name}')
    if data is None:
        raise FileNotFoundError(f"File '{file_name}' does not exist in the Data directory.")
    return pd.read_csv(StringIO(data.decode('utf-8')))

