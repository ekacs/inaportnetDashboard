# label definition of risk score
labels_risk = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

# classified risk score based on percent20
df_summary['Fraud_Risk'] = pd.qcut(
    df_summary['Composite_Index'], 
    q=5,                            
    labels=labels_risk,
    duplicates='drop'               
)

# sort by composite index
df_summary = df_summary.sort_values(by='Composite_Index', ascending=False)
