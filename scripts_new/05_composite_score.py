import pandas as pd
import numpy as np

# create function for normalisation (Min-Max)
def scale_01_to_1(series, invert=False):
    x_min = series.min()
    x_max = series.max()
    
    if x_max == x_min:
        return pd.Series(0.1, index=series.index)
    
    if not invert:
        return 0.1 + 0.9 * ((series - x_min) / (x_max - x_min))
    else:
        return 0.1 + 0.9 * ((x_max - series) / (x_max - x_min))

# normalisation of rule based - red flag
df_summary['norm_proporsi_redflag'] = scale_01_to_1(df_summary['proporsi_redflag'], invert=False)

# normalisation of modified z score
df_summary['norm_mean_Zi_new'] = scale_01_to_1(df_summary['mean_Zi_new'], invert=True)

# normalisation of isolation forest
df_summary['norm_mean_if'] = scale_01_to_1(df_summary['mean_if'], invert=True)

df_summary[[
    'port', 
    'proporsi_redflag', 'norm_proporsi_redflag',
    'mean_Zi_new', 'norm_mean_Zi_new',
    'mean_if', 'norm_mean_if'
]]

# calculate composite index based on equal weighting
df_summary['Composite_Index']= (1/3)*(df_summary['norm_proporsi_redflag']+
                                      df_summary['norm_mean_Zi_new']+
                                      df_summary['norm_mean_if'])
