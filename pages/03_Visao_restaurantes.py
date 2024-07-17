# Importando bibliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime

st.set_page_config(page_title='Visão Restaurantes', page_icon='🏙️', layout='wide')

# import dataset
caminho_arquivo = '/dataset/train.csv'
df = pd.read_csv(caminho_arquivo)
#print(df.head())

#criando uma cópia para não alterar o original e preservar os dados brutos
df1 = df.copy()

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
df1 = df1.loc[linhas_selecionadas2, :].copy()
# converter object para int
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# limpar espaços em object

df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
# limpar coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('[^\d.]', '', regex=True).astype(float)

# limpar linhas
#linhas_selecionadas3 = df1['City'] != 'NaN '
#df1 = df1.loc[linhas_selecionadas3, :].copy()

# limpar linhas
linhas_selecionadas4 = df1['Festival'] != 'NaN '
df1 = df1.loc[linhas_selecionadas4, :].copy()

# limpando a coluna de Time_taken
# df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])

  # transformando em numero interiro
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

#============================================
# Barra lateral
#============================================

# Título
st.header('Marketplace - Visão Restaurantes')

# imagem
#image_path = '/home/IvanBertaci/Documentos/CIENCIAS_DADOS/COMUNIDADEDS/REPOS/logo.jpeg'
image = Image.open( 'logo.jpeg')
st.sidebar.image( image, width=120 )

# filtro de linha por data
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', 
                  value=pd.to_datetime('2022-04-13').date(), 
                  min_value=pd.to_datetime('2022-02-11').date(), 
                  max_value=pd.to_datetime('2022-04-06').date(),
                  format='DD-MM-YYYY')

# linha de separação
st.sidebar.markdown("""---""")

# filtro de botões por transito
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
						 ['Low', 'Medium', 'High', 'Jam'], 
						 default=['Low', 'Medium', 'High', 'Jam'])

# linha de separação
st.sidebar.markdown("""---""")
# informações de quem produziu o conjunto de dados
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', ' ', ' '] )

with tab1:
	with st.container():
		st.markdown( """---""" )
		st.markdown('#### Overall Metrics')

		col1, col2, col3, col4, col5, col6 = st.columns( 6 )
		with col1:
			#st.markdown( '##### Entregadores únicos' )
			delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )
			col1.metric( 'Entregadores únicos', delivery_unique )

		with col2:
			#st.markdown( '##### Distância média' )
			cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
			df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Delivery_location_latitude'], x['Delivery_location_longitude']), (x['Restaurant_latitude'], x['Restaurant_longitude']) ), axis=1)
			avg_distance = np.round(df1['distance'].mean(), 2)
			col2.metric('Distância media', avg_distance )
		with col3:
			#st.markdown( '##### Tempo médio de entrega' )
			df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			# Filtrar apenas as linhas com 'Festival' igual a 'Yes'
			df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)
			col3.metric('Desvio padrão das entrega médio com festival', df_aux)
    			
		
		with col4:
			#st.markdown( '##### Desvio padrão das entrega médio com festival' )
			df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			# Filtrar apenas as linhas com 'Festival' igual a 'Yes'
			df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)
			col4.metric('Desvio padrão das entrega médio com festival', df_aux)

		with col5:
			# st.markdown( '##### Tempo de entrega médio sem festival' )
			df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			# Filtrar apenas as linhas com 'Festival' igual a 'Yes'
			df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)
			col5.metric('Desvio padrão das entrega médio com festival', df_aux)
		with col6:
			# st.markdown( '##### Desvio padrão das entrega médio sem festival' )
			df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			# Filtrar apenas as linhas com 'Festival' igual a 'Yes'
			df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)
			col6.metric('Desvio padrão das entrega médio com festival', df_aux)

	with st.container():
		st.markdown( """---""" )
		
		col1, col2 = st.columns( 2 )
		with col1:
			# gráfico de barras com desvio padrão
			st.title('Tempo médio de entrega')
			df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()
			
			fig = go.Figure()
			fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))

			fig.update_layout(barmode='group')
			st.plotly_chart(fig)

		with col2:
			st.title('Distribuição da distância')

			df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			st.dataframe(df_aux)

	with st.container():
		st.markdown( """___""" )
		st.title('Distribuição do tempo')

		col1, col2 = st.columns( 2 )
		with col1:

			colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
			df1['distance'] = df1.loc[:, colunas].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

			avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

			fig = go.Figure(data=[go.Pie(
				labels=avg_distance['City'],
				values=avg_distance['distance'],
				pull=[0, 0.1, 0])])

			st.plotly_chart(fig)

		with col2:
			df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
			df_aux.columns = ['avg_time', 'std_time']
			df_aux = df_aux.reset_index()

			fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))

			st.plotly_chart(fig)