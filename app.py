import streamlit as st
import pandas as pd
import io

def get_table_download_link(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

st.title('Ocultar Identidade')

uploaded_file = st.file_uploader('Insira seus arquivos excel', type=['xlsx', 'xls'])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df = df.astype(str)
    # Create tabs
    tab1, tab2 = st.tabs(["Dados Ocultos", "Dados Originais"])
    
    # Tab 1: Display the dataframe for editing (can hide sensitive data before this step)
    with tab1:
        st.write('Clique nas celulas para editar manualmente')
        edited_df = st.data_editor(df, num_rows='dynamic')

    # Tab 2: Display the original dataframe
    with tab2:
        st.write('Dados Originais')
        st.dataframe(df)
    
    final_output = get_table_download_link(edited_df)
        
    st.download_button(
        label="Baixar o arquivo com os dados ocultos",
        data=final_output,
        file_name="dados_ocultos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )