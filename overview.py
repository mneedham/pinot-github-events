import altair as alt
import pandas as pd
import streamlit as st
from pinotdb import connect
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def overview():
    st.title("GitHub Events: An Overview")

    conn = connect(host='localhost', port=8000, path='/query/sql', scheme='http')

    def get_orgs_df(metric):
        orgs_query = f"""
        select organization, 
            {metric}
        from pullRequestMergedEvents 
        group by organization
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(orgs_query, {"metric": metric})
        return pd.DataFrame(curs, columns=[item[0] for item in curs.description])    

    def get_repos_df(metric):
        orgs_query = f"""
        select organization, repo, 
            {metric}
        from pullRequestMergedEvents 
        group by organization, repo
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(orgs_query, {"metric": metric})
        return pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    metrics = [
        "count(*)", 
        "sum(numCommits)", 
        "sum(numLinesAdded)", 
        "sum(numLinesDeleted)",
        "sum(numFilesChanged)",
        "sum(numReviewComments)",
        "avg(numReviewers)"
    ]


    query = """
    select count(*) AS prs,
        sum(numCommits) AS commits,
        sum(numFilesChanged) AS filesChanged,
        sum(numLinesAdded) AS linesAdded,
        sum(numLinesDeleted) AS linesDeleted
    from pullRequestMergedEvents 
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    st.markdown(f"""
    | PRs      | Commits | Files Changed | Lines Added | Lines Deleted
    | ----------- | ----------- |
    | {df['prs'].astype('int32').values[0]:,} \
    | {df['commits'].astype('int32').values[0]:,} \
    | {df['filesChanged'].astype('int32').values[0]:,} \
    | {df['linesAdded'].astype('int32').values[0]:,} \
    | {df['linesDeleted'].astype('int32').values[0]:,}
    """)

    st.header("Most active organisations")
    left, right = st.beta_columns([1,4]) 
    with left:
        metric = st.selectbox('Select a metric', metrics) 

    with right:    
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=800, height=500)        
            # st.write(df)
            df = get_orgs_df(metric)
            wc.generate_from_frequencies({item[0]: item[1] for item in df.values})
            st.image(wc.to_array())


    st.header("Most active repositories")
    left, right = st.beta_columns([1,4])    
    with left:
        metric = st.selectbox('Select a metric', metrics, key="repo-metrics") 
    with right:
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=800, height=500)
            df = get_repos_df(metric)
            wc.generate_from_frequencies({item[1]: item[2] for item in df.values})
            st.image(wc.to_array())


