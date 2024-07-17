# Importando bibliotecas
import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title='Visão Empresa', page_icon='🏙️', layout='wide')

# ---------------------------------------------------------
# Funções
# ---------------------------------------------------------

def country_maps(df1):
	df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
		.groupby(['City', 'Road_traffic_density'])
		.median()
		.reset_index())
	map = folium.Map()

	for index, location_info in df_aux.iterrows():
		folium.Marker([location_info['Delivery_location_latitude'],
			location_info['Delivery_location_longitude']],
			popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

	folium_static(map, width=1024, height=600)	

def order_share_on_week(df1):
	# criar a coluna da semana e conta e cria um index das semanas
	df_aux01 = (df1.loc[:, ['ID', 'week_of_year']]
			 .groupby('week_of_year')
			 .count()
			 .reset_index())
	df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
			 .groupby('week_of_year')
			 .nunique()
			 .reset_index())
	
	df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
	df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
	# cria o gráfico de linha	

	fig = px.line(df_aux, x='week_of_year', y='Order_by_delivery')
		
	return fig

def order_by_week(df1):
	# criar a coluna da semana e conta e cria um index das semanas
	df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
	# define e cruza os dados ID com semanas do ano e agrupa com semanas do ano
	df_aux = (df1.loc[:, ['ID', 'week_of_year']]
		   .groupby('week_of_year')
		   .count()
		   .reset_index())
	# cria o gráfico de linha
	fig =px.line(df_aux, x='week_of_year', y='ID')

	return fig

def traffic_order_city(df1):
	# seleção de linhas
	df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
		   .groupby(['City', 'Road_traffic_density'])
		   .count()
		   .reset_index())
	# limpeza de dados
	df_aux = df_aux.loc[df_aux['City']!= 'NaN', :]
			
	# gera gráfico
	fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
	
	return fig

def traffic_order_share(df1):
	# seleção de linhas
	df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
		   .groupby('Road_traffic_density')
		   .count()
		   .reset_index())
	# limpeza de dados
	df_aux = df_aux.loc[df_aux['Road_traffic_density']!= "NaN", :]
	# calculo de porcentagem
	df_aux['entregas_perc'] = df_aux["ID"] / df_aux['ID'].sum()

	fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

	return fig

def order_metric(df1):
	st.header('Visão Gerencial')
	st.markdown('---')
			
	#seleção de colunas
	cols = ['ID', 'Order_Date']

	#seleção de linhas
	df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

	#desenhar o gráfico de barras
	st.markdown('### Quantidade de pedidos por dia')
	fig = px.bar(df_aux, x='Order_Date', y='ID')

	return fig

def clean_code(df1):
	# limpar linhas
	linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
	df1 = df1.loc[linhas_selecionadas, :]
	# converter tipo de coluna
	df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

	# converter object para float
	# obs: não precisou limpar as linhas
	df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
	# df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(float)

	# converter object para datetime
	df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y' )

	# limpar linhas
	linhas_selecionadas2 = df1['multiple_deliveries'] != 'NaN '
	df1 = df1.loc[linhas_selecionadas2, :]
	# converter object para int
	df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

	# limpar espaços em object

	df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
	df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
	df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
	df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
	df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

	# limpar coluna de time taken
	df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('[^\d.]', '', regex=True).astype(float)

	# limpar linhas
	#linhas_selecionadas3 = df1['City'] != 'NaN '
	#df1 = df1.loc[linhas_selecionadas3, :]

	# limpar linhas
	linhas_selecionadas4 = df1['Festival'] != 'NaN '
	df1 = df1.loc[linhas_selecionadas4, :]

	return df1



# ------------------------------------------------Início da Estrutura lógica do código ------------------------------

#--------------------------------------------
# import dataset
#--------------------------------------------

caminho_arquivo = 'https://github.com/Ivan-Bertaci/curry_company/blob/master/dataset/train.csv'
df = pd.read_csv(caminho_arquivo)

#--------------------------------------------
#limpar os dados
#--------------------------------------------

df1 = clean_code(df)


#============================================
# Barra lateral
#============================================
st.header('Marketplace - Visão Empresa')

#image_path = '/home/IvanBertaci/Documentos/CIENCIAS_DADOS/COMUNIDADEDS/REPOS/logo.jpeg'
image = Image.open( 'logo.jpeg' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', 
                  value=pd.to_datetime('2022-04-13').date(), 
                  min_value=pd.to_datetime('2022-02-11').date(), 
                  max_value=pd.to_datetime('2022-04-06').date(),
                  format='DD-MM-YYYY')


st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
						 ['Low', 'Medium', 'High', 'Jam'], 
						 default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Cury Company')

# filtro de data
date_slider = pd.to_datetime(date_slider)
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#============================================
# Layout do Streamlit
#============================================

# Criação de tab's
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão de Entregadores'] )

with tab1:
	with st.container():
		fig = order_metric(df1)
		st.plotly_chart(fig, use_container_width=True)
		
	with st.container():
		col1, col2 = st.columns( 2 )

		with col1:
			fig = traffic_order_share(df1)
			st.header("Traffic Order Share")
			st.plotly_chart(fig, use_container_width=True)
		
		with col2:
			fig = traffic_order_city(df1)
			st.header("Traffic Order City")
			st.plotly_chart(fig, use_container_width=True)
	
with tab2:
	with st.container():
		fig = order_by_week(df1)
		st.markdown("# Visão Tática")
		st.plotly_chart(fig, use_container_width=True)

	with st.container():
		fig = order_share_on_week(df1)
		st.markdown("# Traffic Order on Weekdays")
		st.plotly_chart(fig, use_container_width=True)

with tab3:
	st.markdown("# Visão Geográfica")
	country_maps(df1)
	




#st.dataframe(df1)

#print('Deu certo!')"""
