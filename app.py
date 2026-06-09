import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tech Layoffs Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('layoffs.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['total_laid_off'] = df['total_laid_off'].fillna(0).astype(int)
    df['funds_raised'] = df['funds_raised'].fillna(0)
    df['industry'] = df['industry'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['location'] = df['location'].fillna('Unknown')
    df['stage'] = df['stage'].fillna('Unknown')
    df = df[~((df['total_laid_off'] == 0) & (df['percentage_laid_off'].isna()))]
    df = df.drop(columns=['source'])
    return df

df = load_data()

st.title("Global Tech Layoffs Dashboard")
st.markdown("Analysing 3,700+ layoff events from 2020 to 2026")

st.sidebar.header("Filters")
years = sorted(df['year'].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Select years", years, default=years)
industries = sorted(df['industry'].unique())
selected_industries = st.sidebar.multiselect("Select industries", industries, default=industries)

filtered = df[
    (df['year'].isin(selected_years)) &
    (df['industry'].isin(selected_industries))
]

col1, col2, col3 = st.columns(3)
col1.metric("Total laid off", f"{filtered['total_laid_off'].sum():,}")
col2.metric("Companies affected", f"{filtered['company'].nunique():,}")
col3.metric("Countries affected", f"{filtered['country'].nunique():,}")

st.subheader("Layoffs over time")
monthly = filtered.groupby('year_month')['total_laid_off'].sum().reset_index()
monthly = monthly.sort_values('year_month')
fig1 = px.line(monthly, x='year_month', y='total_laid_off',
               labels={'year_month': 'Month', 'total_laid_off': 'Total laid off'})
fig1.update_xaxes(tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.subheader("Top 15 companies")
    top_co = filtered.groupby('company')['total_laid_off'].sum().sort_values(ascending=False).head(15).reset_index()
    fig2 = px.bar(top_co, x='total_laid_off', y='company', orientation='h',
                  labels={'total_laid_off': 'Total laid off', 'company': ''})
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

with col5:
    st.subheader("Layoffs by industry")
    top_ind = filtered.groupby('industry')['total_laid_off'].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(top_ind, x='total_laid_off', y='industry', orientation='h',
                  labels={'total_laid_off': 'Total laid off', 'industry': ''})
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Layoffs by country")
country_data = filtered.groupby('country')['total_laid_off'].sum().reset_index()
fig4 = px.choropleth(country_data, locations='country', locationmode='country names',
                     color='total_laid_off', color_continuous_scale='Blues',
                     labels={'total_laid_off': 'Total laid off'})
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Layoffs by year")
yearly = filtered.groupby('year')['total_laid_off'].sum().reset_index()
fig5 = px.bar(yearly, x='year', y='total_laid_off',
              labels={'year': 'Year', 'total_laid_off': 'Total laid off'})
st.plotly_chart(fig5, use_container_width=True)

st.subheader("Raw data")
st.dataframe(filtered[['company', 'country', 'industry', 'total_laid_off', 'date', 'stage']].sort_values('total_laid_off', ascending=False), use_container_width=True)