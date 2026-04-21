import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Hospital Performance Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('hospital_appointment_no_show_5000.csv')
    # Data Cleaning for Scatter Plot & Calculations
    df['age'] = df['age'].fillna(df['age'].median())
    df['distance_km'] = df['distance_km'].fillna(df['distance_km'].median())
    df.loc[df['age'] < 1, 'age'] = 1
    # Mapping numbers to readable status
    df['Status'] = df['no_show'].map({0: 'Attended', 1: 'Missed'})
    return df

try:
    df = load_data()

    st.title("🏥 Patient Attendance & Operational Insights")
    st.markdown("---")

    # 2. GLOBAL FILTERS (Command Center)
    st.sidebar.header("Global Filters")
    
    selected_dept = st.sidebar.multiselect(
        "Select Department", 
        df['department'].unique(), 
        default=df['department'].unique()
    )
    
    selected_insurance = st.sidebar.multiselect(
        "Select Insurance Status", 
        df['insurance_status'].unique(), 
        default=df['insurance_status'].unique()
    )

    # Applying all sidebar filters to the data
    mask = (df['department'].isin(selected_dept)) & (df['insurance_status'].isin(selected_insurance))
    df_filtered = df[mask]

    # 3. TOP ROW
    row1_col1, row1_col2, row1_col3 = st.columns([2, 2, 2])

    with row1_col1:
        st.subheader("Attendance by Gender")
        gender_data = df_filtered.groupby(['gender', 'Status']).size().reset_index(name='Count')
        fig_gen = px.bar(gender_data, x='gender', y='Count', color='Status', barmode='group',
                         color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'})
        st.plotly_chart(fig_gen, use_container_width=True)

    with row1_col2:
        st.subheader("Department Performance")
        dept_perf = df_filtered.groupby(['department', 'Status']).size().reset_index(name='Count')
        fig_dept = px.bar(dept_perf, y='department', x='Count', color='Status', orientation='h',
                          color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'})
        st.plotly_chart(fig_dept, use_container_width=True)

    with row1_col3:
        # THE SUNBURST: Shows Insurance -> Status Hierarchy
        st.subheader("Insurance & Status Breakdown")
        sun_data = df_filtered.groupby(['insurance_status', 'Status']).size().reset_index(name='Count')
        
        fig_sun = px.sunburst(
            sun_data, 
            path=['insurance_status', 'Status'], 
            values='Count',
            color='Status',
            color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'}
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    st.markdown("---")

    # 4. MIDDLE ROW
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Impact of Waiting Time on Attendance")
        wait_trend = df_filtered.groupby(['waiting_days', 'Status']).size().reset_index(name='Count')
        fig_wait = px.line(wait_trend, x='waiting_days', y='Count', color='Status', markers=True,
                           color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'})
        st.plotly_chart(fig_wait, use_container_width=True)

    with row2_col2:
        st.subheader("Geographic Attendance Analysis")
        city_data = df_filtered.groupby(['city_type', 'Status']).size().reset_index(name='Count')
        fig_city = px.line(city_data, x='city_type', y='Count', color='Status', markers=True,
                           category_orders={"city_type": ["Rural", "Suburban", "Urban"]},
                           color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'})
        st.plotly_chart(fig_city, use_container_width=True)

    st.markdown("---")

    # 5. BOTTOM ROW: SCATTER PLOT
    st.subheader("📍 Correlation: Distance vs. Waiting Days")
    sample_size = min(1000, len(df_filtered))
    if sample_size > 0:
        sample_df = df_filtered.sample(sample_size)
        fig_scatter = px.scatter(sample_df, x="distance_km", y="waiting_days", color="Status",
                                 size="age", hover_data=['department', 'age', 'insurance_status'],
                                 opacity=0.6, size_max=15,
                                 color_discrete_map={'Attended': '#1f77b4', 'Missed': '#ff7f0e'})
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("Adjust filters to view patient correlation.")

except Exception as e:
    st.error(f"Error: {e}")