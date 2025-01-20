import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
     for unidade in ['', 'mil']:
          if valor < 1000:
               return f'{prefixo} {valor:.2f} {unidade}'
          valor /= 1000
     return f'{prefixo} {valor:.2f} milhões'

# Filtro Regiao e Anos 
st.title('DASHBOARD DE VENDAS :shopping_trolley:') 
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
     regiao = ''
     
todos_anos = st.sidebar.checkbox('Dados de todo o peŕiodo', value = True)
if todos_anos:
     ano = ''
else:
     ano = st.sidebar.slider('Ano', 2020, 2023)
     
query_string = {'regiao':regiao.lower(),
                'ano':ano}


url = 'https://labdados.com/produtos'
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
     dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

### Tabelas das receitas

# mapa
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# receita categorias
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabelas de quantidade de vendas

# quantidade vendas dos estados
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# quantidade de vendas mensal
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# vendas categorias
vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending = False)

### Tabelas dos vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))
 
### Gráficos

## ABA 1
# Mapa Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat': False, 'lon': False},
                                   title = 'Receita por Estado'
                                   )

# Linhas de meses e ano
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Barras Top receita estados
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Receita categorias
fig_receita_categorias = px.bar(receita_categorias,
                             text_auto = True,
                             title = 'Receita por Categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita ')

## ABA 2
# Mapa Quantidade de Vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                             lat = 'lat',
                             lon = 'lon',
                             scope = 'south america',
                             size = 'Preço',
                             template = 'seaborn',
                             hover_name = 'Local da compra',
                             hover_data = {'lat': False, 'lon': False},
                             title = 'Quantidade de vendas X Estados'
                             )

# Vendas de mesmes e nao (line plot)
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y = 'Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

# Barras Top vendas estados
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (Vendas)')

fig_vendas_estados.update_layout(yaxis_title = 'Vensas')

# Vendas por categorias
fig_vendas_categorias = px.bar(vendas_categorias,
                              text_auto = True,
                              title = 'Vendas por Categotia')

fig_vendas_categorias.update_layout(yaxis_title = 'Vendas')







## Vizualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantida de vendas', 'Vendedores'])


with aba1:
     col1, col2 = st.columns(2)
     with col1:
          st.metric('Receita ', formata_numero(dados['Preço'].sum(), 'R$'))
          st.plotly_chart(fig_mapa_receita, use_container_width = True)
          st.plotly_chart(fig_receita_estados, use_container_width = True)
          
     with col2:
          st.metric('Total de Vendas ', formata_numero (dados.shape[0 ]))
          st.plotly_chart(fig_receita_mensal, use_container_width = True)
          st.plotly_chart(fig_receita_categorias, use_container_width = True)
          
with aba2:
     col1, col2 = st.columns(2)

     with col1:
          st.metric('Receita ', formata_numero(dados['Preço'].sum(), 'R$'))
          st.plotly_chart(fig_mapa_vendas,use_container_width = True)
          st.plotly_chart(fig_vendas_estados,use_container_width = True)

     with col2:
          st.metric('Total de Vendas ', formata_numero (dados.shape[0 ]))
          st.plotly_chart(fig_vendas_mensal, use_container_width = True)
          st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
     qtd_vendedores = st.number_input('Quantidade de venededores', 2, 10, 5)
     col1, col2 = st.columns(2)
     with col1:
          
          st.metric('Receita ', formata_numero(dados['Preço'].sum(), 'R$'))
          fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                          x = 'sum',
                                          y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                          text_auto = True,
                                          title = f'Top {qtd_vendedores} vendedores (receita)')
          
          st.plotly_chart(fig_receita_vendedores)
          
     with col2:
          st.metric('Total de Vendas ', formata_numero (dados.shape[0 ]))
          fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                          x = 'count',
                                          y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                          text_auto = True,
                                          title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
          
          st.plotly_chart(fig_vendas_vendedores)
          
          
# st.dataframe(dados)

