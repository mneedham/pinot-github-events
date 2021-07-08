import altair as alt
import pandas as pd
import streamlit as st
from pinotdb import connect

st.set_page_config(layout="wide", page_title="GitHub Events")
st.title("GitHub Events")


conn = connect(host='localhost', port=8000, path='/query/sql', scheme='http')


columns = ["numLinesAdded", "numFilesChanged", "numLinesDeleted", "numComments"]

def run_query(column):
    curs = conn.cursor()
    curs.execute(f"""
    select organization, repo, 
        sum({column}) as {column}Sum
    from pullRequestMergedEvents 
    GROUP BY organization, repo
    ORDER BY {column}Sum DESC
    limit 20
    """)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    df.loc[:, 'name'] = df['repo'].str.cat(df['organization'], sep='/')
    return df

metrics = columns


left, right = st.beta_columns(2)    
with left:
    for metric in [f for idx, f in enumerate(metrics) if idx % 2 == 0]:        
        with st.spinner("Loading chart..."):
            st.header(f"Top repositories by {metric}")
            df = run_query(metric)
            metric = f"{metric}Sum"            
            chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
                y=alt.Y(metric, axis=alt.Axis(labels=True, ticks=False), title=None),
                x=alt.X('name', sort=[metric], title="Repository", axis=alt.Axis(labelAngle=45)),
                tooltip=[alt.Tooltip(metric, format=','), "name"]
            ).properties(height=500)

            st.altair_chart(chart, use_container_width=True)

with right:
    for metric in [f for idx, f in enumerate(metrics) if idx % 2 != 0]:
        with st.spinner("Loading chart..."):
            st.header(f"Top repositories by {metric}")
            df = run_query(metric)
            metric = f"{metric}Sum"
            chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
                y=alt.Y(metric, axis=alt.Axis(labels=True, ticks=False), title=None),
                x=alt.X('name', sort=[metric], title="Repository", axis=alt.Axis(labelAngle=45)),
                tooltip=[alt.Tooltip(metric, format=','), "name"]
            ).properties(height=500)

            st.altair_chart(chart, use_container_width=True)