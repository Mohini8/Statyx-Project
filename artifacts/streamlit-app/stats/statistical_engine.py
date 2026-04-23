import pandas as pd
import numpy as np

def descriptive_statistics(df):

    numeric = df.select_dtypes(include=np.number)

    return numeric.describe().T