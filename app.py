import altair as alt
import pandas as pd
import streamlit as st
from pinotdb import connect
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from overview import overview
from breakdown import breakdown

st.set_page_config(layout="wide", page_title="GitHub Events")

PAGES = {
    "Overview": overview,
    "Breakdown": breakdown,
}


st.sidebar.title("GitHub Events")

radio_list = list(PAGES.keys())
selection = st.sidebar.radio("Select Dashboard", radio_list)

page = PAGES[selection]
page()