import altair as alt
import pandas as pd
import streamlit as st
from pinotdb import connect

st.set_page_config(layout="wide", page_title="GitHub Events")
st.title("GitHub Events")

conn = connect(host='localhost', port=8000, path='/query/sql', scheme='http')

@st.cache
def get_orgs():

    orgs_query = """
    select organization, count(*) AS count
    from pullRequestMergedEvents 
    group by organization
    order by count DESC
    limit 50
    """

    curs = conn.cursor()
    curs.execute(orgs_query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    return df['organization'].values

org = st.selectbox('Choose an organization', get_orgs())

metrics = ["numLinesAdded", "numFilesChanged", "numLinesDeleted", "numComments"]

curs = conn.cursor()
curs.execute(f"""
select sum(numLinesAdded) AS linesAdded,
       sum(numLinesDeleted) AS linesDeleted,
       sum(numFilesChanged) AS filesChanged,
       sum(numCommits) AS commits
from pullRequestMergedEvents 
WHERE organization = '{org}'
order by count DESC
limit 50
""")

df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

st.dataframe(df.assign(hack='').set_index('hack'))
