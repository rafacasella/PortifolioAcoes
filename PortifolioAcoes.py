#App Portifólio de ações
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime
from dateutil.utils import today
from pandas.conftest import axis
from streamlit import subheader
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

def build_sidebar():
    ticker_list = pd.read_csv('tickers.csv', index_col = 0) #para pegar diretamente o nome, e não o número do índice
    tickers = st.multiselect("Selecione as Empresas", options= ticker_list, placeholder="Códigos")
    tickers = [t+'.SA' for t in tickers] #Adicionando a terminologia utilziada no yahoo finance
    start_date = st.date_input("Data Inicial", format='DD/MM/YYYY', value=datetime(2016, 1, 1)) #Streamlit automaticamene joga 10 anos para mais e pars menos
    end_date = st.date_input("Data Final", format='DD/MM/YYYY', value=datetime.today())

    if tickers:
        prices = yf.download(tickers, start=start_date, end=end_date)['Close'] #baixar a ação selecionada, filtrada pelo fechamento
        prices.columns = prices.columns.str.strip('.SA') #removendo o SA, para facilitar as execuções futuras
        prices['IBOV'] = yf.download('^BVSP', start=start_date, end=end_date)['Close'] #Utilizar também o IBOV como comparativo do portifólio
        return tickers, prices
    return [], pd.DataFrame()


def build_main(tickers, prices):
    if not prices.empty:
        weights = np.ones(len(tickers))/len(tickers) #colcoar todos os pesos iguais, a medida que acrescenta mais ações os pesos são redistribuidos equitativamente
        prices['Portifólio'] = prices.drop('IBOV', axis=1) @ weights #Criando nova coluna com a multiplicação dos preços pelos pesos
        norm_prices = 100 * prices / prices.iloc[0] #normalizando os preços pelo primeiro valor....muito útil na exibição do gráfico
        returns = prices.pct_change()[1:] #Calculando os retornos ja excluindo a primeira linha
        vols = returns.std() *np.sqrt(252) #Calculando a volatilidade utilizando desvio padrão e o número de dias úteis
        rets = ((norm_prices.iloc[-1]/norm_prices.iloc[0]) -1) #retonos: pegando o último retorno, e exibindo em forma decimal

        mygrid = grid(5,5,5,5,5,5, vertical_align='top') #criando um grid vazio alinhado ao topo
        for t in prices.columns: #alimentando o grid
            c = mygrid.container(border=True)
            c.subheader(t, divider='red')
            colA, colB = c.columns(2) #criando as colunas que apresentarão as métricas
            colA.metric(label='Retorno', value=f'{rets[t]:.0%}') #Exibindo o retorno em porcentagem
            colB.metric(label='Volatilidade', value=f'{vols[t]:.0%}') #Exibinfo os retorno também em porcentagem

            col1, col2 = st.columns(2, gap='large') #criando duas colunas para receber os gráficos

        with col1:
            st.subheader('Desempenho Relativo')
            st.line_chart(norm_prices, height=600)

        with col2:
            st.subheader('Risco x Retorno')
            fig = px.scatter(
                x=vols,
                y=rets,
                text=vols.index,
                color=rets/vols,
                color_discrete_sequence=px.colors.sequential.Bluered_r
            )
            fig.update_traces(
                textfont_color="white",
                marker=dict(size=45),
                textfont_size=10,
            )
            fig.layout.yaxis.title = 'Retorno Total'
            fig.layout.xaxis.title = 'Volatilidade (anualizada)'
            fig.layout.height = 600
            fig.layout.yaxis.tickformat = '.0%'
            fig.layout.xaxis.tickformat = '.0%'
            fig.layout.coloraxis.colorbar.title = 'Sharpe'
            st.plotly_chart(fig, use_container_width=True)


        st.dataframe(prices)
    else:
        st.warning('Selecione pelo menos uma empresa para visualizar os preços')

st.set_page_config(layout="wide")

with st.sidebar:
    tickers, prices = build_sidebar()

st.title('Portifolio Ações')
build_main(tickers, prices)
