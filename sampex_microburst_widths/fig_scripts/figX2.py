"""
This script generates a histogram of all microburst widths on the left panel, and
the widths as a function of AE in the right panel.

Parameters
----------
catalog_name: str
    The name of the catalog in the config.PROJECT_DIR/data/ directory.
r2_thresh: float
    The adjusted R^2 threshold for the fits. I chose a default value of 0.9.
max_width: float
    Maximum microburst width (FWHM) in seconds to histogram. A good default is
    0.25 [seconds]
"""
import pathlib
import string

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sampex_microburst_widths import config

plt.rcParams.update({'font.size': 13})

### Script parameters ###
catalog_name = 'microburst_catalog_04.csv'
r2_thresh = 0.9
max_width = 0.5
width_bins = np.linspace(0, max_width+0.001, num=50)
ae_bins = [0, 100, 300, 1000]

# Load the catalog, drop the NaN values, and filter by the max_width and
# R^2 values.
df = pd.read_csv(pathlib.Path(config.PROJECT_DIR, 'data', catalog_name))
df.dropna(inplace=True)
df = df[df['width_s'] < max_width]
df['fwhm'] = df['fwhm'].abs()
df = df[df.adj_r2 > r2_thresh]

quantiles = [.25, .50, .75]
width_percentiles = df['width_s'].quantile(q=quantiles)

fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(10, 5))

# Left panel histogram and statistics.
ax[0].hist(df['width_s'], bins=width_bins, color='k', histtype='step', density=True)
s = (
    f"Percentiles [ms]"
    f"\n25%: {(width_percentiles.loc[0.25]*1000).round().astype(int)}"
    f"\n50%: {(width_percentiles.loc[0.50]*1000).round().astype(int)}"
    f"\n75%: {(width_percentiles.loc[0.75]*1000).round().astype(int)}"
)
ax[0].text(0.65, 0.6, s, 
        ha='left', va='top', transform=ax[0].transAxes
        )
plt.suptitle('Distribution of > 1 MeV Microburst Duration\nSAMPEX/HILT')
# Left panel tweaks
ax[0].set_xlim(0, max_width)
ax[0].set_ylabel('Probability Density')
ax[0].set_xlabel('FWHM [s]')

# Right panel histogram and statistics
for start_ae, end_ae in zip(ae_bins[:-1], ae_bins[1:]):
    df_flt = df[(df['AE'] > start_ae) & (df['AE'] < end_ae)]

    ax[1].hist(df_flt['fwhm'], bins=width_bins, histtype='step', density=True,
            label=f'{start_ae} < AE [nT] < {end_ae}', lw=2)

ax[1].legend(loc='center right', fontsize=12)
ax[1].set_xlabel('FWHM [s]')

# Subplot labels
# for a, label in zip(ax, string.ascii_lowercase):
ax[0].text(0, 0.99, f'(a) All Microbursts', va='top', transform=ax[0].transAxes, 
    weight='bold', fontsize=15)
ax[1].text(0, 0.99, f'(b) As a function of AE', va='top', transform=ax[1].transAxes, 
    weight='bold', fontsize=15)

plt.tight_layout()
plt.show()