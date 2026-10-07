import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set Page Config
st.set_page_config(page_title="IJI Health Insights Interface", layout="wide")

# -----------------------------------------------------------------------------
# 1. DATA PROCESSING & IJI ENGINE PIPELINE
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_process_data():
    
    df = pd.read_csv("data.csv")
    return df

def run_iji_engine(df, trend_thresh=10.0, corr_thresh=0.70, z_thresh=2.0, iqr_multiplier=1.5):
    indicators = ['anc_coverage', 'institutional_delivery', 'immunization', 'high_risk_cases']
    insights = []
    insight_counter = 1

    # Operation 1: Trend Detection
    df_sorted = df.sort_values(by=['district', 'month'])
    for district, group in df_sorted.groupby('district'):
        group = group.sort_values('month')
        if len(group) >= 2:
            prev_row, curr_row = group.iloc[0], group.iloc[1]
            for ind in indicators:
                prev_val, curr_val = prev_row[ind], curr_row[ind]
                pct_change = ((curr_val - prev_val) / prev_val) * 100
                if abs(pct_change) >= trend_thresh:
                    severity = "HIGH" if abs(pct_change) >= 15.0 else ("MEDIUM" if abs(pct_change) >= 10.0 else "LOW")
                    direction = "dropped" if pct_change < 0 else "increased"
                    explanation = f'"{ind.replace("_", " ").title()} in {district} {direction} by {abs(pct_change):.1f}% compared to the previous month, exceeding the {trend_thresh:.0f}% threshold."'
                    
                    header_str = f"{district} — {ind} — {curr_row['month']} — {curr_val} (prev {prev_val}), Δ {pct_change:+.1f}%"
                    insights.append({
                        'id': f"INS-{insight_counter:03d}",
                        'type': 'trend',
                        'method': 'Percentage Change',
                        'indicator': ind,
                        'district': district,
                        'period': curr_row['month'],
                        'severity': severity,
                        'header': header_str,
                        'explanation': explanation
                    })
                    insight_counter += 1

    # Operation 2A: Z-Score Outlier Detection
    for ind in indicators:
        mean_val = df[ind].mean()
        std_val = df[ind].std()
        
        for _, row in df.iterrows():
            z_score = (row[ind] - mean_val) / (std_val if std_val != 0 else 1.0)
            if abs(z_score) >= z_thresh:
                severity = "HIGH" if abs(z_score) >= 2.5 else "MEDIUM"
                bound_dir = "below" if z_score < 0 else "above"
                explanation = f'"{row["district"]}\'s {ind.replace("_", " ")} of {row[ind]} is {abs(z_score):.1f}σ {bound_dir} the state mean ({mean_val:.0f}), flagging for review."'
                
                header_str = f"{row['district']} — {ind} — {row['month']} — {row[ind]} [Z-Score: {z_score:.2f}]"
                insights.append({
                    'id': f"INS-{insight_counter:03d}",
                    'type': 'outlier',
                    'method': 'Z-Score',
                    'indicator': ind,
                    'district': row['district'],
                    'period': row['month'],
                    'severity': severity,
                    'header': header_str,
                    'explanation': explanation
                })
                insight_counter += 1

    # Operation 2B: IQR (Interquartile Range) Outlier Detection
    for ind in indicators:
        q1 = df[ind].quantile(0.25)
        q3 = df[ind].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr
        
        for _, row in df.iterrows():
            val = row[ind]
            if val < lower_bound or val > upper_bound:
                bound_type = f"below lower bound ({lower_bound:.1f})" if val < lower_bound else f"above upper bound ({upper_bound:.1f})"
                dev_pct = ((lower_bound - val) / lower_bound) * 100 if val < lower_bound else ((val - upper_bound) / upper_bound) * 100
                severity = "HIGH" if dev_pct >= 25.0 else "MEDIUM"
                
                explanation = f'"{row["district"]}\'s {ind.replace("_", " ")} of {val} is an IQR anomaly ({bound_type}), flagging for review."'
                header_str = f"{row['district']} — {ind} — {row['month']} — {val} [IQR Outlier]"
                insights.append({
                    'id': f"INS-{insight_counter:03d}",
                    'type': 'outlier',
                    'method': 'IQR',
                    'indicator': ind,
                    'district': row['district'],
                    'period': row['month'],
                    'severity': severity,
                    'header': header_str,
                    'explanation': explanation
                })
                insight_counter += 1

    # Operation 3: Correlation Detection
    corr_matrix = df[indicators].corr()
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            c1, c2 = cols[i], cols[j]
            r = corr_matrix.loc[c1, c2]
            if abs(r) >= corr_thresh:
                severity = "HIGH" if abs(r) >= 0.90 else "MEDIUM"
                explanation = f'"Strong correlation (r = {r:+.2f}) observed between {c1.replace("_", " ")} and {c2.replace("_", " ")} across districts."'
                header_str = f"All Districts — {c1} & {c2} — 2026-07 to 2026-08"
                insights.append({
                    'id': f"INS-{insight_counter:03d}",
                    'type': 'correlation',
                    'method': 'Pearson Correlation',
                    'indicator': f"{c1} & {c2}",
                    'district': 'All Districts',
                    'period': '2026-07 to 2026-08',
                    'severity': severity,
                    'header': header_str,
                    'explanation': explanation
                })
                insight_counter += 1

    return pd.DataFrame(insights), corr_matrix

# Load base data
df = load_and_process_data()

# -----------------------------------------------------------------------------
# 2. SIDEBAR LIVE FILTERS
# -----------------------------------------------------------------------------
st.sidebar.title("🎛️ Live Filters & Thresholds")

district_filter = st.sidebar.selectbox("Filter District:", ["All"] + list(df['district'].unique()))
severity_filter = st.sidebar.multiselect("Severity Level:", ["LOW", "MEDIUM", "HIGH"], default=["LOW", "MEDIUM", "HIGH"])
type_filter = st.sidebar.multiselect("Insight Type:", ["trend", "outlier", "correlation"], default=["trend", "outlier", "correlation"])
outlier_method_filter = st.sidebar.multiselect("Outlier Algorithms:", ["Z-Score", "IQR"], default=["Z-Score", "IQR"])

st.sidebar.markdown("---")
st.sidebar.subheader("Threshold Controls")
trend_threshold = st.sidebar.slider("Trend Breach Threshold (% Change):", 5.0, 50.0, 10.0, step=2.5)
z_threshold = st.sidebar.slider("Z-Score Threshold (σ):", 1.5, 3.5, 2.0, step=0.1)
iqr_multiplier = st.sidebar.slider("IQR Multiplier:", 1.0, 3.0, 1.5, step=0.1)

# Run Engine
insights_df, corr_matrix = run_iji_engine(
    df, 
    trend_thresh=trend_threshold, 
    corr_thresh=0.70, 
    z_thresh=z_threshold, 
    iqr_multiplier=iqr_multiplier
)

# Apply Filters
filtered_df = insights_df[
    (insights_df['severity'].isin(severity_filter)) &
    (insights_df['type'].isin(type_filter))
]

# Filter specifically by Outlier Method if type contains outlier
if 'outlier' in type_filter:
    non_outliers = filtered_df[filtered_df['type'] != 'outlier']
    outliers_filtered = filtered_df[
        (filtered_df['type'] == 'outlier') & (filtered_df['method'].isin(outlier_method_filter))
    ]
    filtered_df = pd.concat([non_outliers, outliers_filtered]).sort_values('id')

if district_filter != "All":
    filtered_df = filtered_df[
        (filtered_df['district'] == district_filter) | (filtered_df['district'] == 'All Districts')
    ]

# -----------------------------------------------------------------------------
# 3. INTERFACE VISUALIZATIONS & OUTPUTS
# -----------------------------------------------------------------------------
st.title("🏥 IJI Automated Health Metrics & Insight Dashboard")

# Top KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Insights", len(filtered_df))
kpi2.metric("High Severity", len(filtered_df[filtered_df['severity'] == 'HIGH']))
kpi3.metric("Medium Severity", len(filtered_df[filtered_df['severity'] == 'MEDIUM']))
kpi4.metric("Low Severity", len(filtered_df[filtered_df['severity'] == 'LOW']))

col1, col2 = st.columns([1, 1])

# Panel 1: Severity Counts Bar Chart
with col1:
    fig1, ax1 = plt.subplots(figsize=(6, 4.2))
    if not filtered_df.empty:
        palette = {'LOW': '#2ecc71', 'MEDIUM': '#f39c12', 'HIGH': '#e74c3c'}
        sns.countplot(data=filtered_df, x='severity', order=['LOW', 'MEDIUM', 'HIGH'], palette=palette, ax=ax1)
        ax1.set_title("1. Severity Counts (Filtered)", fontweight='bold')
        ax1.set_ylabel("Count")
        for p in ax1.patches:
            h = p.get_height()
            if h > 0:
                ax1.annotate(f'{int(h)}', (p.get_x() + p.get_width() / 2., h / 2.),
                             ha='center', va='center', color='white', fontweight='bold')
    else:
        ax1.text(0.5, 0.5, "No Insights Found for Active Filters", ha='center', va='center')
    st.pyplot(fig1)

# Panel 2: Indicator Correlation Heatmap
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 4.2))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax2, cbar=True)
    ax2.set_title("2. Correlation Heatmap Across Indicators", fontweight='bold')
    st.pyplot(fig2)

# Panel 3: Per-District Metric Trend Visualizer with Outlier Annotations
st.subheader("📈 3. Per-District Metric Trend Visualizer (With Outlier Markers)")

plot_districts = [district_filter] if district_filter != "All" else list(df['district'].unique())
indicators = ['anc_coverage', 'institutional_delivery', 'immunization', 'high_risk_cases']

num_districts = len(plot_districts)
if num_districts == 1:
    fig3, axes3 = plt.subplots(1, 1, figsize=(10, 4))
    axes_list = [axes3]
else:
    cols_count = 3
    rows_count = (num_districts + cols_count - 1) // cols_count
    fig3, axes3 = plt.subplots(rows_count, cols_count, figsize=(15, 3.8 * rows_count), sharex=True)
    axes_list = axes3.flatten()

# Extract flagged outliers from active filters to plot on chart
outlier_records = filtered_df[filtered_df['type'] == 'outlier']

for idx, dist in enumerate(plot_districts):
    ax = axes_list[idx]
    d_data = df[df['district'] == dist].sort_values('month')
    
    # Base Trend Lines
    for ind in indicators:
        ax.plot(d_data['month'], d_data[ind], marker='o', linewidth=2, label=ind.replace('_', ' ').title())
    
    # Overlay Outlier Annotations/Markers
    dist_outliers = outlier_records[outlier_records['district'] == dist]
    for _, out_row in dist_outliers.iterrows():
        month_val = out_row['period']
        ind_col = out_row['indicator']
        
        # Get actual data point value
        matched_pt = d_data[(d_data['month'] == month_val)]
        if not matched_pt.empty and ind_col in matched_pt.columns:
            y_val = matched_pt[ind_col].values[0]
            
            # Styling based on outlier detection method
            marker_symbol = 'X' if out_row['method'] == 'Z-Score' else '*'
            marker_color = '#e74c3c' if out_row['severity'] == 'HIGH' else '#e67e22'
            
            # Plot highlight halo around outlier point
            ax.scatter(month_val, y_val, s=180, color=marker_color, marker=marker_symbol, zorder=5)
            ax.annotate(
                f"Outlier ({out_row['method']})", 
                (month_val, y_val),
                textcoords="offset points", 
                xytext=(0, 10), 
                ha='center',
                fontsize=8,
                fontweight='bold',
                color=marker_color,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=marker_color, lw=1)
            )

    ax.set_title(f"District: {dist}", fontweight='bold', fontsize=11)
    ax.set_xlabel("Month")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle='--', alpha=0.5)
    if idx == 0:
        ax.legend(fontsize=8, loc='best')

if num_districts > 1:
    for idx in range(num_districts, len(axes_list)):
        fig3.delaxes(axes_list[idx])

plt.tight_layout()
st.pyplot(fig3)

# -----------------------------------------------------------------------------
# 4. AUTOMATED INSIGHT LIST & CSV DOWNLOAD
# -----------------------------------------------------------------------------
st.subheader("📋 4. Automated Insight List")

if not filtered_df.empty:
    # Convert filtered insights to CSV buffer
    csv_buffer = filtered_df[['id', 'type', 'method', 'severity', 'district', 'indicator', 'period', 'header', 'explanation']].to_csv(index=False)

    # Download Button
    st.download_button(
        label="📥 Download Insights CSV",
        data=csv_buffer,
        file_name="iji_automated_insights.csv",
        mime="text/csv",
        help="Click to download the current filtered list of insights as a CSV file."
    )

    # Render Blockquote Callouts with Explicit Black Text
    for _, row in filtered_df.iterrows():
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid #BDC3C7;
                padding: 10px 15px;
                margin-bottom: 15px;
                background-color: #F9F9F9;
                color: #000000;
                font-size: 15px;
                line-height: 1.5;
            ">
                <span style="color: #000000; font-weight: normal;">
                    {row['header']} — Severity: <strong>{row['severity']}</strong> {row['explanation']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No insights matching the selected filters.")