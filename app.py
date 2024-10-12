import streamlit as st
import pandas as pd
import io
from datetime import datetime
import re
from openpyxl import load_workbook

def get_table_download_link(dfs):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

from datetime import datetime

def is_date(string):
    date_patterns = [
        '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%y', '%y-%m-%d', 
        '%y/%m/%d', '%d-%m-%y', '%m-%d-%Y', '%H:%M:%S', '%H:%M', '%I:%M %p', 
        '%I:%M:%S %p', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %I:%M %p', 
        '%Y-%m-%d %I:%M:%S %p', '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M'
    ]
    
    return any(
        try_parse_date(string, pattern) for pattern in date_patterns
    )

def try_parse_date(string, pattern):
    try:
        datetime.strptime(string, pattern)
        return True
    except ValueError:
        return False

def hide_identity(df):
    name_list = []
    list_of_lists = df.to_dict('split')['data']
    for l in list_of_lists:
        name_list.extend(l)
    name_list = list(set(name_list))
    name_dict = {name: f'estudante_{i}' for i, name in enumerate(name_list)}
    # remove from dict time strings
    for name in name_list:
        if is_date(name):
            name_dict.pop(name)
    df = df.replace(name_dict)
    return df

st.title('Ocultar Identidade')

uploaded_files = st.file_uploader('Insira seus arquivos excel', type=['xlsx', 'xls'], accept_multiple_files=True)

if uploaded_files:
    all_dfs = {}
    for uploaded_file in uploaded_files:
        xls = pd.ExcelFile(uploaded_file)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df = df.astype(str)
            df = df.replace('nan', '')
            df = hide_identity(df)
            all_dfs[f"{uploaded_file.name} - {sheet_name}"] = df

    # Create tabs
    tab1, tab2 = st.tabs(["Dados Ocultos", "Dados Originais"])
    
    # Tab 1: Display the dataframes for editing
    with tab1:
        st.write('Clique nas celulas para editar manualmente')
        edited_dfs = {}
        for sheet_name, df in all_dfs.items():
            st.subheader(sheet_name)
            edited_df = st.data_editor(df, num_rows='dynamic')
            edited_dfs[sheet_name] = edited_df

    # Tab 2: Display the original dataframes
    with tab2:
        st.write('Dados Originais')
        for sheet_name, df in all_dfs.items():
            st.subheader(sheet_name)
            st.dataframe(df)
    
    final_output = get_table_download_link(edited_dfs)
        
    st.download_button(
        label="Baixar o arquivo com os dados ocultos",
        data=final_output,
        file_name="dados_ocultos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )