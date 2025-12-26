import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="QualSteam Analytics | Zydus",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION ---
# Relative paths for GitHub deployment
# Ensure your repo has a folder named 'data' containing these CSVs
DATA_FILES = {
    "Scenario 1": "data/df_1_cleaned.csv",
    "Scenario 2": "data/df_2_cleaned.csv",
    "Scenario 3": "data/df_3_cleaned.csv",
    "Scenario 4": "data/df_4_cleaned.csv"
}

# Column Mapping
COLS = {
    'timestamp': 'Timestamp',
    'temp_sp': 'Process Temp SP',
    'temp_pv': 'Process Temp',
    'steam_flow': 'Steam Flow Rate',
    'valve_out': 'QualSteam Valve Opening',
    'p1': 'Inlet Steam Pressure',
    'p2': 'Outlet Steam Pressure',
    'p2_sp': 'Pressure SP'
}

# --- LOADER ---
@st.cache_data
def load_data(filepath):
    # Try loading from local path (standard)
    try:
        df = pd.read_csv(filepath)
        df[COLS['timestamp']] = pd.to_datetime(df[COLS['timestamp']])
        return df
    except FileNotFoundError:
        return None

# --- PLOTTING STANDARD ---
def plot_dashboard(df, plot_title):
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.25, 0.25, 0.25, 0.25],
        subplot_titles=(
            "Temperature Analysis",
            "Pressure Dynamics",
            "Steam Flow Rate",
            "Control Valve Output"
        )
    )

    # --- ROW 1: TEMPERATURE ---
    # Trace 1: Setpoint (Black Dotted)
    fig.add_trace(go.Scatter(
        x=df[COLS['timestamp']], y=df[COLS['temp_sp']],
        name='Process Temp SP', mode='lines',
        line=dict(color='black', width=2, dash='dot')
    ), row=1, col=1)

    # Trace 2: Actual (Deep Red)
    fig.add_trace(go.Scatter(
        x=df[COLS['timestamp']], y=df[COLS['temp_pv']],
        name='Process Temp', mode='lines',
        line=dict(color='#D32F2F', width=2)
    ), row=1, col=1)

    # --- ROW 2: PRESSURE ---
    # Trace 1: Setpoint (Indigo Dotted)
    if COLS['p2_sp'] in df.columns:
        fig.add_trace(go.Scatter(
            x=df[COLS['timestamp']], y=df[COLS['p2_sp']],
            name='Pressure SP', mode='lines',
            line=dict(color='#1A237E', width=2, dash='dot')
        ), row=2, col=1)

    # Trace 2: Inlet P1 (Teal/Dark Green)
    if COLS['p1'] in df.columns:
        fig.add_trace(go.Scatter(
            x=df[COLS['timestamp']], y=df[COLS['p1']],
            name='Inlet P1', mode='lines',
            line=dict(color='#004D40', width=2)
        ), row=2, col=1)

    # Trace 3: Outlet P2 (Dark Blue + Fill)
    fig.add_trace(go.Scatter(
        x=df[COLS['timestamp']], y=df[COLS['p2']],
        name='Outlet P2', mode='lines',
        line=dict(color='#00008B', width=2),
        fill='tozeroy', fillcolor='rgba(0, 0, 139, 0.1)'
    ), row=2, col=1)

    # --- ROW 3: STEAM FLOW ---
    # Trace 1: Flow (Violet + Fill)
    if COLS['steam_flow'] in df.columns:
        fig.add_trace(go.Scatter(
            x=df[COLS['timestamp']], y=df[COLS['steam_flow']],
            name='Flow Rate', mode='lines',
            line=dict(color='#7B1FA2', width=2),
            fill='tozeroy', fillcolor='rgba(123, 31, 162, 0.1)'
        ), row=3, col=1)

    # --- ROW 4: VALVE OUTPUT ---
    # Trace 1: Valve (Goldenrod + Fill)
    fig.add_trace(go.Scatter(
        x=df[COLS['timestamp']], y=df[COLS['valve_out']],
        name='Valve %', mode='lines',
        line=dict(color='#B8860B', width=2),
        fill='tozeroy', fillcolor='rgba(184, 134, 11, 0.1)'
    ), row=4, col=1)

    # --- LAYOUT & STYLING ---
    fig.update_layout(
        height=900,
        title_text=plot_title,
        title_font=dict(color='black', size=16),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.02,
            xanchor='right', x=1
        ),
        font=dict(color='black')
    )

    # Axis Updates
    common_axis = dict(
        showgrid=True,
        gridcolor='#f0f0f0',
        linecolor='black',
        ticks='outside',
        tickcolor='black'
    )
    
    fig.update_xaxes(**common_axis)
    fig.update_yaxes(**common_axis)

    # Specific Y-Axis Labels
    fig.update_yaxes(title_text="Temp (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Bar", row=2, col=1)
    fig.update_yaxes(title_text="kg/hr", row=3, col=1)
    fig.update_yaxes(title_text="%", range=[0, 105], row=4, col=1)
    
    return fig

# --- MAIN APP LAYOUT ---

# Sidebar
st.sidebar.title("QualSteam Analytics")
st.sidebar.markdown("---")
selected_scenario = st.sidebar.radio("Select Forensic Scenario:", list(DATA_FILES.keys()))

st.sidebar.markdown("---")
st.sidebar.info("Data source: Zydus LifeSciences Site Logs")

# Main Content
# Load Data
file_path = DATA_FILES[selected_scenario]
df = load_data(file_path)

if df is not None:
    # 1. Header Design (Fixed Orientation)
    st.title("QualSteam Forensic Dashboard")
    
    # Extract Metadata
    date_str = df[COLS['timestamp']].dt.date.iloc[0].strftime('%Y-%m-%d')
    
    # Create a nice header block
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 🏭 **Zydus LifeSciences**")
    with col2:
        st.markdown(f"📅 **Date:** {date_str}")
    with col3:
        st.markdown(f"📂 **View:** {selected_scenario}")

    st.markdown("---")
    
    # 2. Key Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Process Temp", f"{df[COLS['temp_pv']].mean():.1f} °C", delta_color="off")
    m2.metric("Max Outlet Pressure", f"{df[COLS['p2']].max():.2f} bar")
    
    # Handle optional columns safely
    total_steam = f"{df[COLS['steam_flow']].sum() / 60:.0f} kg" if COLS['steam_flow'] in df.columns else "N/A"
    avg_valve = f"{df[COLS['valve_out']].mean():.1f} %" if COLS['valve_out'] in df.columns else "N/A"
    
    m3.metric("Total Steam Consumed", total_steam) 
    m4.metric("Avg Valve Opening", avg_valve)

    st.markdown("---")

    # 3. Visualization
    # Title logic for the plot itself
    plot_title = f"Forensic Trace: {selected_scenario} ({date_str})"
    fig = plot_dashboard(df, plot_title)
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.error(f"⚠️ Data file not found: `{file_path}`")
    st.warning("Please ensure the CSV files are in the `data/` folder of your repository.")
