import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração inicial
st.set_page_config(page_title="Meu Controle Financeiro IA", layout="wide")

# Função do "modelo de IA" para sugestões
def analisar_gastos(df, renda_total):
    if df.empty:
        return "Adicione transações para ver as análises."
    
    # Análise básica de gastos por categoria
    gastos_por_categoria = df[df['Tipo'] == 'Saída'].groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    
    # Sugestão de redução
    categoria_maior_gasto = gastos_por_categoria.idxmax() if not gastos_por_categoria.empty else "Nenhum"
    sugestao_reducao = f"Reduza gastos em '{categoria_maior_gasto}'" if categoria_maior_gasto != "Nenhum" else ""
    
    # Sugestão de investimento (regra básica)
    sobra = renda_total - df[df['Tipo'] == 'Saída']['Valor'].sum()
    sugestao_investir = f"Invista até R${sobra * 0.3:.2f} (30% da sobra)" if sobra > 0 else "Ajuste gastos para investir"
    
    return f"{sugestao_reducao} | {sugestao_investir}"

# Dados (persistência via CSV)
try:
    df = pd.read_csv('dados_financeiros.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns=['Data', 'Descrição', 'Valor', 'Categoria', 'Tipo'])

# Sidebar para novos registros
with st.sidebar:
    st.header("➕ Nova Transação")
    data = st.date_input("Data", datetime.today())
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0)
    categoria = st.selectbox("Categoria", ["Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Outros"])
    tipo = st.radio("Tipo", ["Entrada", "Saída"])
    
    if st.button("Salvar"):
        nova_linha = pd.DataFrame([[data, descricao, valor, categoria, tipo]], 
                                columns=df.columns)
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv('dados_financeiros.csv', index=False)
        st.success("Salvo!")

# Layout principal
st.title("💰 Meu Controle Financeiro IA")

# Métricas rápidas
renda_total = df[df['Tipo'] == 'Entrada']['Valor'].sum()
gastos_total = df[df['Tipo'] == 'Saída']['Valor'].sum()
saldo = renda_total - gastos_total

col1, col2, col3 = st.columns(3)
col1.metric("Renda Total", f"R${renda_total:,.2f}")
col2.metric("Gastos Total", f"R${gastos_total:,.2f}")
col3.metric("Saldo Atual", f"R${saldo:,.2f}")

# Gráficos e análises
tab1, tab2, tab3 = st.tabs(["Gastos por Categoria", "Balanço Mensal", "Sugestões IA"])

with tab1:
    st.subheader("📊 Distribuição de Gastos")
    if not df[df['Tipo'] == 'Saída'].empty:
        st.bar_chart(df[df['Tipo'] == 'Saída'].groupby('Categoria')['Valor'].sum())
    else:
        st.write("Sem dados de gastos ainda.")

with tab2:
    st.subheader("📅 Balanço Mensal")
    if not df.empty:
        df['Data'] = pd.to_datetime(df['Data'])
        df['Mês'] = df['Data'].dt.strftime('%Y-%m')
        mensal = df.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack(fill_value=0)
        
        mensal['Entrada'] = mensal.get('Entrada', 0)
        mensal['Saída'] = mensal.get('Saída', 0)
        mensal['Saldo'] = mensal['Entrada'] - mensal['Saída']
        
        st.line_chart(mensal[['Entrada', 'Saída', 'Saldo']])
    else:
        st.write("Adicione transações para ver o balanço mensal.")

with tab3:
    st.subheader("🤖 Recomendações Financeiras")
    sugestao = analisar_gastos(df, renda_total)
    st.write(sugestao)
    st.write("(Modelo básico - personalize com mais dados!)")

# Mostrar dados brutos
if st.checkbox("Ver tabela completa"):
    st.dataframe(df)
