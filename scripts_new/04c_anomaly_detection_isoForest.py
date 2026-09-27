#3 Isolation Forest - Unsupervised machine learning

import pandas as pd
from sklearn.ensemble import IsolationForest

# determine the feature to use
features = ['gt', 'approval_minutes', 'hour', 'day']
X = df_PKK[features].copy()

if X['day'].dtype == 'object':
    X = pd.get_dummies(X, columns=['day'], drop_first=True)

# model initialisation and training
iso_forest = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
iso_forest.fit(X)

# 3. Ambil Nilai Mentah (Raw Score)

# raw score range -1.0 hingga 0.0 (negative means anomaly)
df_PKK['raw_score'] = iso_forest.score_samples(X)

# value < 0 = Anomaly, Nilai > 0 = Normal
df_PKK['decision_score'] = iso_forest.decision_function(X)

df_PKK['raw_score'] = pd.to_numeric(df_PKK['raw_score'], errors='coerce')

# mean raw score on each port
df_if_mean = df_PKK.groupby('port').agg(
    mean_if=('raw_score', 'mean')
).reset_index()

# join to summary
df_summary = df_summary.merge(df_if_mean, on='port', how='left')

# result
df_summary.sort_values(by='mean_if', ascending=False).head()
