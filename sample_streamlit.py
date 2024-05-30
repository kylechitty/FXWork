import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import datetime as dt
import warnings

def main():
    st.title('Cocoa Data Dashboard')

    # Cocoa Historical Time Series
    st.header('Cocoa Historical Time Series')
    cocoa_df = yf.Ticker("CC=F").history(period="max").loc[:,"Open":"Volume"]

    filter_dict = {}
    n_cols = 5
    col_list = st.columns(n_cols)
    
    with col_list[0]:
        freq_dict = {'Daily':'D', 'Weekly':'W', 'Monthly':'ME', 'Quarterly':'Q', 'Annually':'A'}
        sel_index = list(freq_dict.keys()).index('Monthly')
        sel_freq = st.selectbox('Frequency', freq_dict.keys(), index=sel_index)
        filter_dict['freq'] = sel_freq

    with col_list[1]:
        sel_index = list(cocoa_df.columns).index('Close')
        sel_price_used = st.selectbox('Price Used', cocoa_df.columns, index=sel_index)
        filter_dict['price_used'] = sel_price_used

    with col_list[2]:
        sel_display = st.selectbox('Display Metric', ['Price','Returns'])
        filter_dict['display'] = sel_display

    with col_list[3]:
        start_date = st.date_input('Start Date', value=cocoa_df.index.min(), min_value=cocoa_df.index.min(), 
                                   max_value=cocoa_df.index.max())
        filter_dict['start_date'] = start_date

    with col_list[4]:
        end_date = st.date_input('End Date', value=cocoa_df.index.max(), min_value=cocoa_df.index.min(), 
                                 max_value=cocoa_df.index.max())
        filter_dict['end_date'] = end_date

    freq = freq_dict[filter_dict['freq']]
    price_ser = cocoa_df[filter_dict['price_used']].resample(freq).mean()
    price_ser = price_ser[(price_ser.index >= dt.datetime.combine(filter_dict['start_date'], dt.datetime.min.time())) & 
                          (price_ser.index <= dt.datetime.combine(filter_dict['end_date'], dt.datetime.min.time()))]

    fig = plt.figure(figsize=(10,6))
    if filter_dict['display'] == 'Price':
        plt.plot(price_ser)
    else:
        df_ret = (np.log(price_ser) - np.log(price_ser.shift(1))) * 100
        plt.plot(df_ret)

    st.pyplot(fig)

    # Cocoa Production Dataset
    st.header('Cocoa Production Dataset')

    prod_df = pd.read_csv('production_data.csv', index_col=0)
    col_mapping = {'2022/23 (estimated)':'2022/23', '2023/24 (forecasted)':'2023/24'}
    prod_df = prod_df.rename(columns=col_mapping)

    sel_region = st.multiselect('Regions', list(prod_df.index), default=list(prod_df.index))
    df = prod_df.loc[sel_region]

    st.dataframe(df)

    # Open Interest Volume
    st.header('Open Interest Volume')

    open_int_df = pd.read_csv('open_interest.csv')
    open_int_df['datetime_index'] = pd.to_datetime(open_int_df['datetime_index'])
    open_int_df.index = open_int_df['datetime_index']

    partition_df = open_int_df[['CSCE-COCOA COM. LONG FUT - OPEN INTEREST', 'CSCE-COCOA COM. SHORT FUT - OPEN INTEREST', 
                                'CSCE-COCOA N-COM. LONG FUT - OPEN INTEREST', 'CSCE-COCOA N-COM. SHORT FUT - OPEN INTEREST']]

    partition_df = partition_df.rename(columns={'CSCE-COCOA COM. LONG FUT - OPEN INTEREST' : 'Commercial Long Futures',
                                                'CSCE-COCOA N-COM. LONG FUT - OPEN INTEREST' : 'Non-Commercial Long Futures',
                                                'CSCE-COCOA COM. SHORT FUT - OPEN INTEREST' : 'Commercial Short Futures',
                                                'CSCE-COCOA N-COM. SHORT FUT - OPEN INTEREST' : 'Non-Commercial Short Futures'})
    
    filter_dict = {}
    n_cols = 3
    col_list = st.columns(n_cols)
    
    with col_list[0]:
        sel_fut_type = st.selectbox('Future Type', partition_df.columns, index=sel_index)
        filter_dict['fut_type'] = sel_fut_type

    with col_list[1]:
        start_date = st.date_input('Start Date', value=cocoa_df.index.min(), min_value=cocoa_df.index.min(), 
                                   max_value=cocoa_df.index.max(), key="start_date_1")
        filter_dict['start_date'] = start_date

    with col_list[2]:
        end_date = st.date_input('End Date', value=cocoa_df.index.max(), min_value=cocoa_df.index.min(), 
                                 max_value=cocoa_df.index.max(), key='end_date_1')
        filter_dict['end_date'] = end_date

    fut_ser = partition_df[filter_dict['fut_type']]
    fut_ser = fut_ser[(fut_ser.index >= dt.datetime.combine(filter_dict['start_date'], dt.datetime.min.time())) & 
                        (fut_ser.index <= dt.datetime.combine(filter_dict['end_date'], dt.datetime.min.time()))]
    
    fig = plt.figure(figsize=(10,6))
    plt.plot(fut_ser)

    st.pyplot(fig)

warnings.simplefilter(action='ignore', category=FutureWarning)
main()