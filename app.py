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

org = st.selectbox('Select an organization', get_orgs())

metrics = ["numLinesAdded", "numFilesChanged", "numLinesDeleted", "numComments"]

curs = conn.cursor()
curs.execute("""
select sum(numLinesAdded) AS linesAdded,
       sum(numLinesDeleted) AS linesDeleted,
       sum(numFilesChanged) AS filesChanged,
       sum(numCommits) AS commits
from pullRequestMergedEvents 
WHERE organization = %(org)s
order by count DESC
limit 50
""", {"org": org})

df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

st.markdown(f"## Activity in the [{org}](https://github.com/{org}) organization")

st.markdown(f"""
| Metric      | Count |
| :-----        |              -----: |
| Lines Added      | {df['linesAdded'].astype('int32').values[0]:,}       |
| Lines Deleted      | {df['linesDeleted'].astype('int32').values[0]:,}       |
| Files Changed      | {df['filesChanged'].astype('int32').values[0]:,}       |
| Commits      | {df['commits'].astype('int32').values[0]:,}       |
""")

left, right = st.beta_columns(2)

with left:
    st.subheader("PRs")
    curs.execute("""
    select repo, count(*) as prs
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by prs DESC
    limit 10
    """, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
        y=alt.Y('repo', sort=["index"], axis=alt.Axis(labels=True, ticks=False), title=None),
        x=alt.X('prs'),        
        tooltip=["repo", alt.Tooltip('prs', format=',')] 
    ).properties(title="PRs")

    st.altair_chart(chart, use_container_width=True)  

    st.subheader("Files changed")
    curs.execute("""
    select repo, sum(numFilesChanged) as filesChanged
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by filesChanged DESC
    limit 10
    """, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
        y=alt.Y('repo', sort=["index"], axis=alt.Axis(labels=True, ticks=False), title=None),
        x=alt.X('filesChanged'),        
        tooltip=["repo", alt.Tooltip('filesChanged', format=',')] 
    ).properties(title="Files changed")

    st.altair_chart(chart, use_container_width=True)  

    st.subheader("Lines added")
    curs.execute("""
    select repo, sum(numLinesAdded) as linesAdded
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by linesAdded DESC
    limit 10
    """, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
        y=alt.Y('repo', sort=["index"], axis=alt.Axis(labels=True, ticks=False), title=None),
        x=alt.X('linesAdded'),        
        tooltip=["repo", alt.Tooltip('linesAdded', format=',')] 
    ).properties(title="Lines added")

    st.altair_chart(chart, use_container_width=True)      

with right:
    st.subheader("Commits")
    curs.execute(f"""
    select repo, sum(numCommits) as commits
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by commits DESC
    limit 10
    """, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
        y=alt.Y('repo', sort=["index"], axis=alt.Axis(labels=True, ticks=False), title=None),
        x=alt.X('commits'),        
        tooltip=["repo", alt.Tooltip('commits', format=',')] 
    ).properties(title="Commits")

    st.altair_chart(chart, use_container_width=True)  

    st.subheader("Lines deleted")
    curs.execute(f"""
    select repo, sum(numLinesDeleted) as linesDeleted
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by linesDeleted DESC
    limit 10
    """, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar().encode(
        y=alt.Y('repo', sort=["index"], axis=alt.Axis(labels=True, ticks=False), title=None),
        x=alt.X('linesDeleted'),        
        tooltip=["repo", alt.Tooltip('linesDeleted', format=',')] 
    ).properties(title="Lines deleted")

    st.altair_chart(chart, use_container_width=True)     

@st.cache
def get_repos(org):
    repo_query = """
    select repo, count(*) AS count
    from pullRequestMergedEvents 
    WHERE organization = %(org)s
    group by repo
    order by count DESC
    limit 50
    """

    curs = conn.cursor()
    curs.execute(repo_query, {"org": org})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    return df['repo'].values

repo = st.selectbox('Select a repository', get_repos(org))    

st.markdown(f"## Activity in the [{org}/{repo}](https://github.com/{org}/{repo}) repository")

left, right = st.beta_columns(2)

with left:
    curs.execute(f"""
    select userId, count(*) AS count
        from pullRequestMergedEvents 
        WHERE organization = %(org)s
        AND repo = %(repo)s
        GROUP BY userId
        ORDER BY count DESC
        limit 10
    """, {"org": org, "repo": repo})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar(color='#9B59B6').encode(
    x=alt.X('userId', sort=["index"], axis=alt.Axis(labels=True, ticks=False, labelAngle=0), title=None),
    y=alt.Y('count'),        
    tooltip=["userId", alt.Tooltip('count', format=',')] 
    ).properties(title="Who creates PRs?")

    st.subheader("Who creates PRs?")
    st.altair_chart(chart, use_container_width=True)  

    curs.execute("""
    select reviewers, COUNTMV(reviewers) AS count
    from pullRequestMergedEvents 
    WHERE reviewers != ''
    AND organization = %(org)s
    AND repo = %(repo)s
    GROUP BY reviewers
    ORDER BY count DESC
    limit 10
    """, {"org": org, "repo": repo})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar(color='#9B59B6').encode(
    x=alt.X('reviewers', sort=["index"], axis=alt.Axis(labels=True, ticks=False, labelAngle=0), title=None),
    y=alt.Y('count'),        
    tooltip=["reviewers", alt.Tooltip('count', format=',')] 
    ).properties(title="Who reviews PRs?")

    st.subheader("Who reviews PRs?")
    if df.shape[0] > 0:
        st.altair_chart(chart, use_container_width=True)  
    else:
        st.write("No PRs")

with right:  
    curs.execute("""
    select mergedBy, count(*) AS count
        from pullRequestMergedEvents 
        WHERE organization = %(org)s
        AND repo = %(repo)s
        GROUP BY mergedBy
        ORDER BY count DESC
        limit 10
    """, {"org": org, "repo": repo})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    chart = alt.Chart(df, padding={"left": 10, "top": 10, "right": 10, "bottom": 10}).mark_bar(color='#9B59B6').encode(
    x=alt.X('mergedBy', sort=["index"], axis=alt.Axis(labels=True, ticks=False, labelAngle=0), title=None),
    y=alt.Y('count'),        
    tooltip=["mergedBy", alt.Tooltip('count', format=',')] 
    ).properties(title="Who merges PRs?")

    st.subheader("Who merges PRs?")
    if df.shape[0] > 0:
        st.altair_chart(chart, use_container_width=True)    