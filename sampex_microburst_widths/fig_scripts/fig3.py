"""
This script makes Figure 2: a dial plot of the microburst width as a 
function of L and MLT

Parameters
----------
catalog_name: str
    The name of the catalog in the config.PROJECT_DIR/data/ directory.
r2_thresh: float
    The adjusted R^2 threshold for the fits. I chose a default value of 0.9.
max_width_ms: float
    Maximum microburst width (FWHM) in milliseconds to histogram. A good default is
    500 ms.
percentiles: np.array
    The distribution percentiles for the FWHM distributions in L-MLT space. 
    This script implicitly assumes that you supply 3 percentile values, between
    0 and 100, for the 4 subplots (3 percentiles and 1 microburst occurrence 
    distribution)
"""
import pathlib
import string

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors

from sampex_microburst_widths import config
from sampex_microburst_widths.stats import dial_plot

plt.rcParams.update({'font.size': 13})
cmap = 'viridis'

catalog_name = 'microburst_catalog_04.csv'

### Script parameters
statistics_thresh=100 # Don't calculate stats if less microbursts in the bin.
percentiles = np.array([50])
r2_thresh = 0.9
max_width_ms = 500
L_bins = np.linspace(2, 8.1, num=20)
L_labels = [2,4,6]
MLT_bins = np.linspace(0, 24, num=40)

df = pd.read_csv(pathlib.Path(config.PROJECT_DIR, 'data', catalog_name))
df.dropna(inplace=True)
df['width_ms'] = 1000*df['width_s'] # Convert seconds to ms.
df['fwhm_ms'] = 1000*df['fwhm']
df = df[df['width_ms'] < max_width_ms]
df['fwhm_ms'] = df['fwhm_ms'].abs()
df = df[df.adj_r2 > r2_thresh]

num_microbursts_H, _, _ = np.histogram2d(df['MLT'], df['L_Shell'],
                                        bins=[MLT_bins, L_bins])
H = np.nan*np.zeros(
    (len(MLT_bins), len(L_bins), len(percentiles))
                    )

for i, (start_MLT, end_MLT) in enumerate(zip(MLT_bins[:-1], MLT_bins[1:])):
    for j, (start_L, end_L) in enumerate(zip(L_bins[:-1], L_bins[1:])):
        df_flt = df.loc[(
            (df['MLT'] > start_MLT) &  (df['MLT'] < end_MLT) &
            (df['L_Shell'] > start_L) &  (df['L_Shell'] < end_L)
            ), 'fwhm_ms']
        if df_flt.shape[0] >= statistics_thresh:
            H[i, j, :] = df_flt.quantile(percentiles/100)

fig = plt.figure(figsize=(9, 4))
ax = [plt.subplot(1, 2, i, projection='polar') for i in range(1, 3)]

for i, ax_i in enumerate(ax[:-1]):
    d = dial_plot.Dial(ax_i, MLT_bins, L_bins, H[:, :, i])
    d.draw_dial(L_labels=L_labels,
            mesh_kwargs={'cmap':cmap},
            colorbar_kwargs={'label':f'microburst duration [ms]', 'pad':0.1})
    annotate_str = f'({string.ascii_lowercase[i]}) {percentiles[i]}th percentile'
    ax_i.text(-0.2, 1.2, annotate_str, va='top', transform=ax_i.transAxes, 
            weight='bold', fontsize=15)

d4 = dial_plot.Dial(ax[-1], MLT_bins, L_bins, num_microbursts_H)
d4.draw_dial(L_labels=L_labels,
            mesh_kwargs={'norm':matplotlib.colors.LogNorm(), 'cmap':cmap},
            colorbar_kwargs={'label':'Number of microbursts', 'pad':0.1})
annotate_str = f'({string.ascii_lowercase[len(ax)-1]}) Microburst occurrence'
ax[-1].text(-0.2, 1.2, annotate_str, va='top', transform=ax[-1].transAxes, 
            weight='bold', fontsize=15)

for ax_i in ax:
    ax_i.set_rlabel_position(235)
plt.suptitle(f'Distribution of SAMPEX microburst durations in L-MLT', fontsize=20)

plt.tight_layout()
plt.show()