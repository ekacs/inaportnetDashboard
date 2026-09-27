#1 RULE BASED THEORY
# red flag 1 - short duration (approval <= 10 seconds)

df_PKK['red_flag1'] = (df_PKK['approval_minutes'] <= (10 / 60)).astype(int)

# red flag 2 - long duration (approval > 8 hours)

df_PKK['red_flag2'] = (df_PKK['approval_minutes'] > (480)).astype(int)

# red flag 3 - response within 00.00 - 04.00 (low supervisory)

df_PKK['red_flag3'] = np.where((df_PKK['response'].dt.hour >= 0) & (df_PKK['response'].dt.hour < 4), 1, 0)

#red flag 4 - GT manipulation (change GT less than 6 months)

temp = df_PKK[['vessel_name', 'gt', 'submission']].reset_index()
merged = pd.merge(temp, temp, on='vessel_name', suffixes=('_1', '_2'))

cond_different_row = merged['index_1'] != merged['index_2']
cond_different_gt = merged['gt_1'] != merged['gt_2']
cond_within_6_months = (merged['submission_1'] - merged['submission_2']).dt.days.abs() <= 180

flagged_indices = merged[cond_different_row & cond_different_gt & cond_within_6_months]['index_1'].unique()

df_PKK['red_flag4'] = 0
df_PKK.loc[flagged_indices, 'red_flag4'] = 1

# red flag 5 - same vessel in 2 ports within 2 hours

cand_vessels_5 = df_PKK.groupby('vessel_name')['port'].nunique()
cand_vessels_5 = cand_vessels_5[cand_vessels_5 > 1].index

flagged_idx_5 = set()

if len(cand_vessels_5) > 0:
    df_cand5 = df_PKK[df_PKK['vessel_name'].isin(cand_vessels_5)][['vessel_name', 'port', 'submission']].reset_index()
    
    for _, group in df_cand5.groupby('vessel_name'):
        m = pd.merge(group, group, on='vessel_name', suffixes=('_1', '_2'))
        
        cond_diff_row = m['index_1'] != m['index_2']
        cond_diff_port = m['port_1'] != m['port_2']
        cond_within_2h = (m['submission_1'] - m['submission_2']).abs() < pd.Timedelta(hours=2)
        
        match = m[cond_diff_row & cond_diff_port & cond_within_2h]['index_1']
        flagged_idx_5.update(match)

df_PKK['red_flag5'] = 0
df_PKK.loc[list(flagged_idx_5), 'red_flag5'] = 1

#summaries red flag based on rule based
df_summary = df_PKK.groupby('port').agg(
    volume=('port', 'count'),                   # Jumlah total transaksi/baris per port
    red_flag1=('red_flag1', 'sum'),             # Jumlah indikasi red_flag1
    red_flag2=('red_flag2', 'sum'),             # Jumlah indikasi red_flag2
    red_flag3=('red_flag3', 'sum'),             # Jumlah indikasi red_flag3
    red_flag4=('red_flag4', 'sum'),             # Jumlah indikasi red_flag4
    red_flag5=('red_flag5', 'sum')              # Jumlah indikasi red_flag5
).reset_index()

df_summary['total_red_flags'] = (
    df_summary['red_flag1'] + 
    df_summary['red_flag2'] + 
    df_summary['red_flag3'] + 
    df_summary['red_flag4'] + 
    df_summary['red_flag5']
)
df_summary['proporsi_redflag'] = (
    df_summary['total_red_flags'] / df_summary['volume']*100
)

df_summary.sort_values(by='total_red_flags', ascending=False).head()


#visualisation of red flag score
import matplotlib.pyplot as plt
import seaborn as sns


# targeted port to review
target_keywords = [
    'lahewa', 'susoh', 'benete', 'lombok', 'selat panjang', 
    'rangga ilung', 'tanjung uban', 'bungku', 'batam', 
    'tanjung priok', 'tanjung perak'
]

plt.figure(figsize=(12, 7))
sns.set_theme(style="whitegrid")

# plot all ports based on proportion vs volume
sns.scatterplot(
    data=df_summary, 
    x='volume', 
    y='proporsi_redflag', 
    s=100,            
    color='#3498db',     
    alpha=0.6,           
    edgecolor='black'
)

# Provide label based on targeted ports
for i in range(len(df_summary)):
    port_name = str(df_summary['port'].iloc[i]).strip()
    x_val = df_summary['volume'].iloc[i]
    y_val = df_summary['proporsi_redflag'].iloc[i]
    
    # Cek apakah ada kata kunci target yang terkandung di dalam nama pelabuhan
    if any(keyword in port_name.lower() for keyword in target_keywords):
        
        # Gambar ulang titik target dengan warna MERAH agar lebih menonjol
        plt.scatter(x_val, y_val, color='#e74c3c', s=130, zorder=5, edgecolor='black')
        
        # Tambahkan teks nama pelabuhan di sebelah titik
        plt.annotate(
            port_name, 
            (x_val, y_val),
            textcoords="offset points", 
            xytext=(7, 4), 
            ha='left',
            fontsize=9,
            fontweight='bold',
            color='#2c3e50',
            zorder=6
        )

# customize the title and x-y label
plt.title('Transaction volume vs Red flag proportion', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Volume', fontsize=11)
plt.ylabel('Red Flag (%)', fontsize=11)

plt.tight_layout()
plt.show()

