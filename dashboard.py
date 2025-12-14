import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# =============================================
# PAGE CONFIGURATION
# =============================================
st.set_page_config(
    page_title="Global Terrorism Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# CUSTOM CSS STYLING - Professional Navy Blue Theme
# =============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a5f 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #1e3a5f 100%);
        border-right: 2px solid #3b82f6;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #e2e8f0;
    }

    h1, h2, h3 { color: #f1f5f9 !important; }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }

    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }

    [data-testid="stMetricLabel"] { color: #e2e8f0 !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        border-radius: 10px;
        padding: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #334155;
        border-radius: 8px;
        color: #e2e8f0;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
    }

    .stDownloadButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
    }

    .stDownloadButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(59, 130, 246, 0.4);
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd, #3b82f6);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 6s linear infinite;
        text-align: center;
    }

    @keyframes shine { to { background-position: 300% center; } }

    .subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 1rem;
    }

    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #3b82f6, transparent);
        margin: 20px 0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================
# DATA LOADING
# =============================================
@st.cache_data
def load_data():
    df = pd.read_csv('gtd_cleaned.csv')
    return df

with st.spinner(' Loading Global Terrorism Database...'):
    df = load_data()

# =============================================
# HEADER
# =============================================
st.markdown('<h1 class="main-title"> Global Terrorism Database Analysis</h1>', unsafe_allow_html=True)

# =============================================
# SIDEBAR FILTERS
# =============================================
with st.sidebar:
    st.markdown("##  Control Panel")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("###  Time Period")
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider("Select Year Range", min_year, max_year, (2000, max_year))
    
    st.markdown("###  Region")
    regions = ['All Regions'] + sorted(df['region'].dropna().unique().tolist())
    selected_region = st.selectbox("Select Region", regions)
    
    if selected_region != 'All Regions':
        countries = ['All Countries'] + sorted(df[df['region'] == selected_region]['country'].dropna().unique().tolist())
    else:
        countries = ['All Countries'] + sorted(df['country'].dropna().unique().tolist())
    selected_country = st.selectbox("Select Country", countries)
    
    st.markdown("###  Attack Type")
    attack_types = ['All Types'] + sorted(df['attack_type'].dropna().unique().tolist())
    selected_attack = st.selectbox("Attack Type", attack_types)
    
    success_filter = st.radio("Attack Outcome", ["All", "Successful", "Failed"])
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("###  Database Info")
    st.info(f" Total Records: **{len(df):,}**")
    st.info(f" Years: **{min_year} - {max_year}**")
    st.info(f" Countries: **{df['country'].nunique()}**")
    st.info(f" Groups: **{df['group_name'].nunique():,}**")

# =============================================
# APPLY FILTERS
# =============================================
df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()

if selected_region != 'All Regions':
    df_filtered = df_filtered[df_filtered['region'] == selected_region]
if selected_country != 'All Countries':
    df_filtered = df_filtered[df_filtered['country'] == selected_country]
if selected_attack != 'All Types':
    df_filtered = df_filtered[df_filtered['attack_type'] == selected_attack]
if success_filter == "Successful":
    df_filtered = df_filtered[df_filtered['success'] == 1]
elif success_filter == "Failed":
    df_filtered = df_filtered[df_filtered['success'] == 0]

# =============================================
# KPI METRICS
# =============================================
st.markdown("###  Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(" Total Attacks", f"{len(df_filtered):,}")
with col2:
    st.metric(" Total Killed", f"{df_filtered['nkill'].sum():,.0f}")
with col3:
    st.metric(" Total Wounded", f"{df_filtered['nwound'].sum():,.0f}")
with col4:
    total_cas = df_filtered['nkill'].sum() + df_filtered['nwound'].sum()
    st.metric(" Total Casualties", f"{total_cas:,.0f}")
with col5:
    success_rate = df_filtered['success'].mean() * 100
    st.metric(" Success Rate", f"{success_rate:.1f}%")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# =============================================
# MAIN TABS
# =============================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Trends", " Map", " Attacks", " Groups", " Insights", " Data"
])

# =============================================
# TAB 1: TRENDS
# =============================================
with tab1:
    yearly = df_filtered.groupby('year').agg({
        'nkill': 'sum', 'nwound': 'sum', 'country': 'count', 'success': 'mean'
    }).reset_index()
    yearly.columns = ['year', 'killed', 'wounded', 'attacks', 'success_rate']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly['year'], y=yearly['attacks'],
            fill='tozeroy', mode='lines', name='Attacks',
            line=dict(color='#3b82f6', width=3),
            fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig.update_layout(
            title='Attacks Over Time',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=yearly['year'], y=yearly['killed'], name='Killed', marker_color='#3b82f6'), secondary_y=False)
        fig.add_trace(go.Scatter(x=yearly['year'], y=yearly['wounded'], name='Wounded', line=dict(color='#22c55e', width=3)), secondary_y=True)
        fig.update_layout(
            title='Casualties Over Time',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if selected_region == 'All Regions':
        region_yearly = df_filtered.groupby(['year', 'region']).size().reset_index(name='attacks')
        fig = px.area(region_yearly, x='year', y='attacks', color='region',
                      title='Attacks by Region Over Time',
                      color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        monthly = df_filtered.groupby('month').size().reset_index(name='attacks')
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly = monthly[monthly['month'].between(1, 12)]
        monthly['month_name'] = monthly['month'].apply(lambda x: month_names[int(x)-1])

        fig = go.Figure(go.Barpolar(r=monthly['attacks'], theta=monthly['month_name'],
                                     marker_color=monthly['attacks'], marker_colorscale='Blues'))
        fig.update_layout(title='Monthly Pattern', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_filtered['decade'] = (df_filtered['year'] // 10 * 10).astype(str) + 's'
        decade_stats = df_filtered.groupby('decade').size().reset_index(name='attacks')
        fig = px.bar(decade_stats, x='decade', y='attacks', color='attacks',
                     title='Attacks by Decade', color_continuous_scale='Blues')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# =============================================
# TAB 2: MAP
# =============================================
with tab2:
    map_data = df_filtered[df_filtered['latitude'].notna() & df_filtered['longitude'].notna()].copy()
    
    if len(map_data) > 5000:
        map_data = map_data.sample(n=5000, random_state=42)
        st.info(" Showing 5,000 sample points for performance")
    
    if len(map_data) > 0:
        map_data['size'] = map_data['nkill'].fillna(1).clip(lower=1, upper=100)

        fig = px.scatter_geo(
            map_data, lat='latitude', lon='longitude',
            color='attack_type', size='size',
            hover_name='city',
            hover_data={'country': True, 'year': True, 'nkill': True, 'latitude': False, 'longitude': False},
            title='Global Attack Locations',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)', landcolor='#1e293b'),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    country_counts = df_filtered['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'attacks']

    fig = px.choropleth(
        country_counts, locations='country', locationmode='country names',
        color='attacks', color_continuous_scale='Blues',
        title='Attacks by Country'
    )
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      geo=dict(showframe=False, bgcolor='rgba(0,0,0,0)', landcolor='#1e293b'), height=500)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        top_countries = df_filtered.groupby('country').agg({'nkill': 'sum', 'year': 'count'}).reset_index()
        top_countries.columns = ['country', 'killed', 'attacks']
        top_countries = top_countries.nlargest(15, 'attacks')

        fig = px.bar(top_countries, x='attacks', y='country', orientation='h',
                     color='killed', color_continuous_scale='Blues',
                     title='Top 15 Countries by Attacks')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        region_stats = df_filtered.groupby('region').agg({'nkill': 'sum', 'year': 'count'}).reset_index()
        region_stats.columns = ['region', 'killed', 'attacks']

        fig = px.sunburst(region_stats, path=['region'], values='attacks', color='killed',
                          color_continuous_scale='Blues', title='Regional Distribution')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# =============================================
# TAB 3: ATTACKS
# =============================================
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        attack_counts = df_filtered['attack_type'].value_counts().reset_index()
        attack_counts.columns = ['attack_type', 'count']

        fig = px.pie(attack_counts, values='count', names='attack_type',
                     title='Attack Type Distribution', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'target_type' in df_filtered.columns:
            target_counts = df_filtered['target_type'].value_counts().head(10).reset_index()
            target_counts.columns = ['target_type', 'count']

            fig = px.bar(target_counts, x='count', y='target_type', orientation='h',
                         title='Top 10 Target Types', color='count', color_continuous_scale='Teal')
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    attack_eff = df_filtered.groupby('attack_type').agg({
        'success': 'mean', 'nkill': 'mean', 'year': 'count'
    }).reset_index()
    attack_eff.columns = ['attack_type', 'success_rate', 'avg_killed', 'total_attacks']
    attack_eff['success_rate'] = attack_eff['success_rate'] * 100

    fig = px.scatter(attack_eff, x='success_rate', y='avg_killed', size='total_attacks',
                     color='attack_type', title='Success Rate vs Lethality (Size = Total Attacks)',
                     color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.box(df_filtered[df_filtered['nkill'] <= df_filtered['nkill'].quantile(0.95)],
                 x='attack_type', y='nkill', color='attack_type',
                 title='Casualty Distribution by Attack Type',
                 color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# =============================================
# TAB 4: GROUPS
# =============================================
with tab4:
    df_groups = df_filtered[df_filtered['group_name'] != 'Unknown']

    top_groups = df_groups.groupby('group_name').agg({
        'nkill': 'sum', 'nwound': 'sum', 'year': ['count', 'min', 'max']
    }).reset_index()
    top_groups.columns = ['group_name', 'killed', 'wounded', 'attacks', 'first_year', 'last_year']
    top_groups['years_active'] = top_groups['last_year'] - top_groups['first_year'] + 1

    col1, col2 = st.columns(2)

    with col1:
        top15_attacks = top_groups.nlargest(15, 'attacks')
        fig = px.bar(top15_attacks, x='attacks', y='group_name', orientation='h',
                     color='killed', color_continuous_scale='Blues',
                     title='Top 15 Most Active Groups')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top15_deadly = top_groups.nlargest(15, 'killed')
        fig = px.bar(top15_deadly, x='killed', y='group_name', orientation='h',
                     color='attacks', color_continuous_scale='Teal',
                     title='Top 15 Deadliest Groups')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)

    top5 = top_groups.nlargest(5, 'attacks')['group_name'].tolist()
    group_timeline = df_groups[df_groups['group_name'].isin(top5)].groupby(['year', 'group_name']).size().reset_index(name='attacks')

    fig = px.line(group_timeline, x='year', y='attacks', color='group_name',
                  title='Top 5 Groups Activity Timeline', markers=True,
                  color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    if len(top_groups) > 0:
        top20 = top_groups.nlargest(20, 'attacks')
        fig = px.treemap(top20, path=['group_name'], values='attacks', color='killed',
                         color_continuous_scale='Blues', title='Group Comparison (Size=Attacks, Color=Killed)')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# =============================================
# TAB 5: INSIGHTS
# =============================================
with tab5:
    st.markdown("### Region x Attack Type Heatmap")
    heatmap_data = pd.crosstab(df_filtered['region'], df_filtered['attack_type'])

    fig = px.imshow(heatmap_data, title='Attack Frequency Matrix',
                    color_continuous_scale='Blues', aspect='auto')
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        success_region = df_filtered.groupby('region')['success'].mean().reset_index()
        success_region['success'] = success_region['success'] * 100
        success_region = success_region.sort_values('success', ascending=True)

        fig = px.bar(success_region, x='success', y='region', orientation='h',
                     title='Success Rate by Region', color='success', color_continuous_scale='Teal')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        lethality = df_filtered.groupby('region')['nkill'].mean().reset_index()
        lethality = lethality.sort_values('nkill', ascending=True)

        fig = px.bar(lethality, x='nkill', y='region', orientation='h',
                     title='Avg Fatalities per Attack by Region', color='nkill', color_continuous_scale='Blues')
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Correlation Analysis")
    corr_cols = ['nkill', 'nwound', 'success', 'year']
    corr_data = df_filtered[corr_cols].corr()

    fig = px.imshow(corr_data, title='Variable Correlations', color_continuous_scale='RdBu', text_auto='.2f')
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("####  Averages")
        st.write(f"• Killed per attack: **{df_filtered['nkill'].mean():.2f}**")
        st.write(f"• Wounded per attack: **{df_filtered['nwound'].mean():.2f}**")
        st.write(f"• Success rate: **{df_filtered['success'].mean()*100:.1f}%**")
    
    with col2:
        st.markdown("####  Maximums")
        st.write(f"• Deadliest attack: **{df_filtered['nkill'].max():,.0f}** killed")
        st.write(f"• Most wounded: **{df_filtered['nwound'].max():,.0f}** wounded")
        st.write(f"• Peak year: **{yearly.loc[yearly['attacks'].idxmax(), 'year']}**")
    
    with col3:
        st.markdown("####   Top Categories")
        st.write(f"• Most attacks: **{df_filtered['country'].mode().iloc[0]}**")
        st.write(f"• Common type: **{df_filtered['attack_type'].mode().iloc[0]}**")
        if 'target_type' in df_filtered.columns:
            st.write(f"• Common target: **{df_filtered['target_type'].mode().iloc[0]}**")

# =============================================
# TAB 6: DATA
# =============================================
with tab6:
    st.markdown("###  Filtered Data Explorer")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df_filtered):,}")
    with col2:
        st.metric("Columns", f"{len(df_filtered.columns)}")
    with col3:
        st.metric("% of Total", f"{len(df_filtered)/len(df)*100:.1f}%")
    
    display_cols = ['year', 'month', 'country', 'city', 'region', 'attack_type', 
                    'target_type', 'group_name', 'nkill', 'nwound', 'success']
    display_cols = [c for c in display_cols if c in df_filtered.columns]
    
    st.dataframe(
        df_filtered[display_cols].sort_values('year', ascending=False).head(1000),
        use_container_width=True,
        height=500
    )
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label=" Download Filtered Data (CSV)",
            data=csv,
            file_name='terrorism_filtered_data.csv',
            mime='text/csv'
        )
    with col2:
        st.download_button(
            label=" Download Summary Stats",
            data=df_filtered.describe().to_csv(),
            file_name='terrorism_summary_stats.csv',
            mime='text/csv'
        )

# =============================================
# FOOTER
# =============================================
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p> <b>CS-366 Data Visualization Project</b> | Global Terrorism Database Analysis</p>
</div>
""", unsafe_allow_html=True)
