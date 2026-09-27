#2 Statistical method - Modified z score
# regression model as predicted duration
import numpy as np
import statsmodels.api as sm
import pandas as pd


df_reg = df_PKK[['approval_minutes',
                 'daily_approval',
                 'gt',
                 'day',
                 'hour']].copy()

# Log transformation
df_reg['log_approval_minutes'] = np.log1p(df_reg['approval_minutes'])

df_reg = pd.get_dummies(df_reg,
                        columns=['day'],
                        drop_first=True,
                        dtype=int)

# change variables into categorical
df_reg['gt_category'] = pd.qcut(
    df_reg['gt'],
    q=4,
    labels=['Q1', 'Q2', 'Q3', 'Q4']
)

df_reg = pd.get_dummies(
    df_reg,
    columns=['gt_category'],
    drop_first=True,
    dtype=int
)

df_reg = df_reg.drop(columns=['gt'])

def hour_category(hour):
    if 0 <= hour < 8:
        return 'Night'
    elif 8 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 16:
        return 'Afternoon'
    elif 16 <= hour < 24:
        return 'Evening'

df_reg['hour_cat'] = df_reg['hour'].apply(hour_category)

df_reg = pd.get_dummies(
    df_reg,
    columns=['hour_cat'],
    drop_first=True,
    dtype=int
)

df_reg = df_reg.drop(columns=['hour'])


# independent variables
X = df_reg.drop(columns=['approval_minutes',
                         'log_approval_minutes'])

# dependent variable
y = df_reg['log_approval_minutes']

# Pastikan semua numerik
X = X.apply(pd.to_numeric)
y = pd.to_numeric(y)

X = sm.add_constant(X)

# model estimation
model = sm.OLS(y, X).fit()

print(model.summary())

# calculate predicted duration

df_PKK['expected_response'] = np.expm1(log_preds)
df_PKK['expected_response'] = df_PKK['expected_response'].clip(lower=0)
df_PKK.head()

# clculate residual
df_PKK['residual'] = df_PKK['approval_minutes'] - df_PKK['expected_response']

# Median residual
median_residual = df_PKK['residual'].median()

# MAD: Median Absolute Deviation
MAD = (df_PKK['residual'] - median_residual).abs().median()

# Modified Z-Score
df_PKK['Zi'] = 0.6745 * (df_PKK['residual'] - median_residual) / MAD

df_PKK['Zi'] = pd.to_numeric(df_PKK['Zi'], errors='coerce')


# mean zi - aggregate to each port
df_zi_mean = df_PKK.groupby('port').agg(
    mean_Zi=('Zi', 'mean')
).reset_index()

# join summary
df_summary = df_summary.merge(df_zi_mean, on='port', how='left')

# result
df_summary.sort_values(by='mean_Zi', ascending=False).head()


#justification of anomaly score to -1
df_PKK['Zi'] = pd.to_numeric(df_PKK['Zi'], errors='coerce')

df_filtered = df_PKK[df_PKK['Zi'] < -1]
df_zi_new = df_filtered.groupby('port').agg(
    mean_Zi_new=('Zi', 'mean')
).reset_index()

df_summary = df_summary.merge(df_zi_new, on='port', how='left')

# 5. fill 0 when port doesn's have anomaly transaction
df_summary['mean_Zi_new'] = df_summary['mean_Zi_new'].fillna(0)

df_summary
