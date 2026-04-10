import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image

st.set_page_config(layout="wide")

# -----------------------------
# LOAD DATA (Improvement 1: caching)
# -----------------------------
@st.cache_data
def load_data():
    data = pd.read_csv('CholeraPumps_Deaths.csv')
    df = pd.DataFrame(data, columns=['count','geometry'])

    df = df.replace({'<Point><coordinates>': ''}, regex=True)
    df = df.replace({'</coordinates></Point>': ''}, regex=True)

    split = df['geometry'].str.split(',', n=1, expand=True)
    df['lon'] = split[0].astype(float)
    df['lat'] = split[1].astype(float)

    df.drop(columns=['geometry'], inplace=True)

    return df

df = load_data()

# Separate pumps
pumps_df = df[df['count'] == -999]
deaths_df = df[df['count'] != -999]

# -----------------------------
# SIDEBAR (Improvement 2: better UI)
# -----------------------------
st.sidebar.title("Controls")

death_to_filter = st.sidebar.slider('Minimum number of deaths', 0, 15, 2)

show_pumps = st.sidebar.checkbox('Show pumps', value=True)

color = st.sidebar.color_picker("Choose death color", "#FF0000")

# Convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

rgb_color = hex_to_rgb(color)

# -----------------------------
# FILTER DATA
# -----------------------------
filtered_df = deaths_df[deaths_df['count'] >= death_to_filter]

# -----------------------------
# MAIN PAGE
# -----------------------------
st.title("John Snow’s 1854 Cholera Map")
st.markdown("Interactive visualization of cholera deaths and water pumps.")

# -----------------------------
# METRICS (Improvement 3)
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric("Deaths shown", len(filtered_df))

with col2:
    st.metric("Pumps shown", len(pumps_df) if show_pumps else 0)

# -----------------------------
# MAP
# -----------------------------
layers = [
    pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[lon, lat]',
        get_color=f'[{rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, 160]',
        get_radius='count * 2',
    )
]

if show_pumps:
    layers.append(
        pdk.Layer(
            'ScatterplotLayer',
            data=pumps_df,
            get_position='[lon, lat]',
            get_color='[0, 0, 255, 160]',
            get_radius=50,
        )
    )

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=51.5134,
        longitude=-0.1365,
        zoom=15.5,
        pitch=0,
    ),
    layers=layers,
))

# -----------------------------
# DESCRIPTION
# -----------------------------
st.markdown("""
- Colored dots represent cholera deaths  
- Size reflects number of deaths  
- Blue dots represent water pumps  
""")

# -----------------------------
# ORIGINAL IMAGE
# -----------------------------
st.subheader('Original map of John Snow')
image = Image.open('Snow-cholera-map-1.jpg')
st.image(image, use_column_width=True)
