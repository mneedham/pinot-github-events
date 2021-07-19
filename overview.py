import altair as alt
import pandas as pd
import streamlit as st
from pinotdb import connect
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

def overview():
    st.title("Overview")

    conn = connect(host='localhost', port=8000, path='/query/sql', scheme='http')

    def get_orgs_df(metric, subtract_time):
        orgs_query = f"""
        select organization, 
            {metric}
        from pullRequestMergedEvents 
        where createdTimeMillis > cast((now() - %(subtract_time)d*1000*60) as long)
        group by organization
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(orgs_query, {"subtract_time": subtract_time})
        return pd.DataFrame(curs, columns=[item[0] for item in curs.description])    

    def get_repos_df(metric, subtract_time):
        orgs_query = f"""
        select organization, repo, 
            {metric}
        from pullRequestMergedEvents 
        where createdTimeMillis > cast((now() - %(subtract_time)d*1000*60) as long)
        group by organization, repo
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(orgs_query, {"subtract_time": subtract_time})
        return pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    def get_users_df(metric, subtract_time):
        query = f"""
        select userId, {metric}
        from pullRequestMergedEvents 
        where createdTimeMillis > cast((now() - %(subtract_time)d*1000*60) as long)
        group by userId
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(query, {"subtract_time": subtract_time})
        return pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    def get_mergers_df(metric, subtract_time):
        query = f"""
        select mergedBy, {metric}
        from pullRequestMergedEvents 
        where createdTimeMillis > cast((now() - %(subtract_time)d*1000*60) as long)
        group by mergedBy
        order by {metric} DESC
        limit 1000
        """
        curs = conn.cursor()
        curs.execute(query, {"subtract_time": subtract_time})
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

    time_range = {
        "All events": round(time.time() * 1000),
        "Last week": 7*24*60,
        "Last day": 24*60,
        "Last 12 hours": 12*60,
        "Last hour": 60        
    }


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

    st.markdown("---")

    with st.form(key='searchForm'):
        col1, col2 = st.beta_columns(2)
        with col1:
            metric = st.selectbox('Select a metric:', metrics)
        with col2:
            timestamp = st.selectbox('Select time range:', list(time_range.keys()))
        
        submit_button = st.form_submit_button(label='Refresh')

    col1, col2 = st.beta_columns(2)

    with col1:
        st.subheader("Most active organisations")
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=1000, height=400)        
            df = get_orgs_df(metric, time_range[timestamp])
            wc.generate_from_frequencies({item[0]: item[1] for item in df.values})
            st.image(wc.to_array(), use_column_width=True)

        st.subheader("Most active users")
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=1000, height=400)        
            df = get_users_df(metric, time_range[timestamp])
            wc.generate_from_frequencies({item[0]: item[1] for item in df.values})
            st.image(wc.to_array(), use_column_width=True)            

    with col2:
        st.subheader("Most active repositories")
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=1000, height=400)
            df = get_repos_df(metric, time_range[timestamp])
            wc.generate_from_frequencies({item[1]: item[2] for item in df.values})
            st.image(wc.to_array(), use_column_width=True)

        st.subheader("Most active mergers")
        with st.spinner('Loading word cloud...'):
            wc = WordCloud(background_color="white", max_words=1000, width=1000, height=400)        
            df = get_mergers_df(metric, time_range[timestamp])
            wc.generate_from_frequencies({item[0]: item[1] for item in df.values})
            st.image(wc.to_array(), use_column_width=True)                 


