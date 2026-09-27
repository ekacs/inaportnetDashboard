## PERBANDINGAN DETAIL FUNGSI

### 1. RULE-BASED ANOMALY DETECTION

| Kriteria                                    | scripts_new (04a)                | modules/analysis.py                   | Keterangan            |
| ------------------------------------------- | -------------------------------- | ------------------------------------- | --------------------- |
| **Red Flag 1**: Quick Approval              | `approval_minutes <= 10/60`      | `approval_minutes <= 10.0/60.0`       | **SAMA**              |
| **Red Flag 2**: Long Duration               | `approval_minutes > 480`         | `approval_minutes > 480.0`            | **SAMA**              |
| **Red Flag 3**: Low Oversight (00:00-04:00) | `response.hour in [0,1,2,3]`     | `hour in [0,1,2,3]`                   | **SAMA** (kolom beda) |
| **Red Flag 4**: GT Manipulation             | Vessel-level GT std comparison   | Vessel-level GT std comparison        | **SAMA**              |
| **Red Flag 5**: Same Vessel 2 Ports < 2 jam | `submission` datetime comparison | `submission_time` datetime comparison | **SAMA** (kolom beda) |

---

### 2. STATISTICAL ANOMALY DETECTION (Modified Z-Score)

| Komponen        | scripts_new (04b)                     | modules/analysis.py                                              | Keterangan                                |
| --------------- | ------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------- |
| **Model**       | OLS regression                        | OLS regression                                                   | **SAMA**                                  |
| **Target**      | `log(approval_minutes)`               | `log(approval_minutes)`                                          | **SAMA**                                  |
| **Features**    | `daily_approval`, `gt`, `day`, `hour` | `daily_approval`, `gt`, `day`, `hour`, `gt_category`, `hour_cat` | **BEDA** (analysis.py tambah kategorikal) |
| **Z-Score**     | `0.6745 * (residual - median) / MAD`  | `0.6745 * (residual - median) / MAD`                             | **SAMA**                                  |
| **Threshold**   | `Zi < -1`                             | `Modified Z <= -2.5`                                             | **BEDA** (threshold berbeda)              |
| **Aggregation** | `mean_Zi`                             | `statistical_index` (min-max scaled)                             | **BEDA** (skala berbeda)                  |

**Issue**: Threshold di `scripts_new` adalah `Zi < -1`, tapi di `modules/analysis.py` menggunakan `Modified Z <= -2.5`. Ini menghasilkan jumlah outlier berbeda.

---

### 3. ISOLATION FOREST DETECTION

| Komponen                   | scripts_new (04c)                       | modules/analysis.py                     | Keterangan               |
| -------------------------- | --------------------------------------- | --------------------------------------- | ------------------------ |
| **Contamination**          | `0.05`                                  | `0.07`                                  | **BEDA**                 |
| **Features**               | `gt`, `approval_minutes`, `hour`, `day` | `gt`, `approval_minutes`, `hour`, `day` | **SAMA**                 |
| **Features Preprocessing** | `pd.get_dummies(day)`                   | `pd.get_dummies(day)`                   | **SAMA**                 |
| **Skor**                   | `raw_score` (mean)                      | `ml_index` (min-max scaled)             | **BEDA** (skala berbeda) |

**Issue**: Contamination rate berbeda (5% vs 7%) menghasilkan jumlah outlier berbeda.

---

### 4. COMPOSITE SCORE (CFRSI)

| Komponen          | scripts_new (05_composite_score.py) | modules/analysis.py            | Keterangan |
| ----------------- | ----------------------------------- | ------------------------------ | ---------- |
| **Normalization** | Min-Max [0.1, 1.0]                  | Min-Max [0.10, 1.00]           | **SAMA**   |
| **Weights**       | Equal weighting (1/3)               | Equal weighting (1/3)          | **SAMA**   |
| **Formula**       | `(norm_rf + norm_zi + norm_if) / 3` | `(rule_based + stat + ml) / 3` | **SAMA**   |

---

### 5. RISK CATEGORISATION

| Komponen       | scripts_new (05_risk_categorisation.py) | modules/analysis.py                                  | Keterangan               |
| -------------- | --------------------------------------- | ---------------------------------------------------- | ------------------------ |
| **Method**     | `pd.qcut` (quantile-based)              | Custom threshold                                     | **BEDA**                 |
| **Categories** | Very Low, Low, Medium, High, Very High  | Sangat Rendah, Rendah, Sedang, Tinggi, Sangat Tinggi | **BEDA** (label berbeda) |

**Issue**: `scripts_new` menggunakan quantile-based (`pd.qcut`) yang membagi data secara merata ke 5 kategori. `modules/analysis.py` menggunakan custom threshold berdasarkan nilai CFRSI.



## RINGKASAN

| Aspek                | scripts_new         | modules/analysis.py  | Rekomendasi                        |
| -------------------- | ------------------- | -------------------- | ---------------------------------- |
| **Rule-Based**       | ✅                   | ✅                    | SAMA - tidak perlu diubah          |
| **Statistical**      | ⚠️ Threshold Zi < -1 | ⚠️ Modified Z <= -2.5 | Sesuaikan threshold ke -2.5        |
| **Isolation Forest** | ⚠️ Contamination 5%  | ⚠️ Contamination 7%   | Sesuaikan contamination ke 7%      |
| **CFRSI Formula**    | ✅                   | ✅                    | SAMA - tidak perlu diubah          |
| **Risk Category**    | ⚠️ Quantile-based    | ⚠️ Custom threshold   | Pilih satu metode secara konsisten |

---

## KESIMPULAN

Implementasi di `modules/analysis.py` **sudah benar** secara logika. Perbedaan dengan `scripts_new` hanya pada:

1. Threshold anomaly detection (Z-score: -1 vs -2.5)
2. Contamination rate (5% vs 7%)
3. Risk categorization method
