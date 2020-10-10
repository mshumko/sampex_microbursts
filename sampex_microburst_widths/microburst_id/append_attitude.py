import pathlib
from datetime import datetime, date

import numpy as np
import pandas as pd

from sampex_microburst_widths import config
from sampex_microburst_widths.misc import load_hilt_data

class Append_Attitude:
    def __init__(self, catalog_path):
        self.catalog_path = catalog_path

        self.load_catalog()
        return
    
    def loop(self):
        """

        """
        #self.prev_date = pd.Timestamp.min


        for unique_date in self.unique_dates:
            # Load attitude data if it has not been loaded yet,
            # or if the unique_date is not in the file (then 
            # load the next attitude file)
            if ((not hasattr(self, 'attitude')) or 
                (self.attitude.attitude[self.attitude.attitude.index.date == unique_date].shape[0] == 0)):
                print('Loading attitude file')
                self.attitude = load_hilt_data.Load_SAMPEX_Attitude(unique_date)
           
                merged = pd.merge_asof(self.catalog, self.attitude.attitude, left_index=True, 
                                    right_index=True, tolerance=pd.Timedelta(seconds=10),
                                    direction='nearest')
                print(merged.dropna(subset=['MLT']))
            

        return

    def load_catalog(self):
        """
        Load the SAMPEX catalog and parse the datetime column.
        """
        self.catalog = pd.read_csv(self.catalog_path, 
            index_col=0, parse_dates=True)
        self.catalog['date'] = self.catalog.index.date
        attitude_keys = ['GEO_Long', 'GEO_Lat', 'Altitude', 'L_Shell']
        for attitude_key in attitude_keys:
            self.catalog[attitude_key] = np.nan
        self.unique_dates = self.catalog.date.unique()
        return

if __name__ == "__main__":
    cat_path = pathlib.Path(config.PROJECT_DIR, 'data', 'microburst_test_catalog.csv')
    a = Append_Attitude(cat_path)
    a.loop()