# Importando bibliotecas
import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title='Visão Entregadores', page_icon='🏙️', layout='wide')

# ---------------------------------------------------------
# Funções
# ---------------------------------------------------------

def top_deliveries( df, top_asc ):	
	df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
			.groupby( ['City', 'Delivery_person_ID'] )
			.mean()
			.sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
	df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
	df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
	df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

	df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

	return df3

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

caminho_arquivo = '../dataset/train.csv'
df = pd.read_csv(caminho_arquivo)


#criando uma cópia para não alterar o original e preservar os dados brutos
df1 = df.copy()


#--------------------------------------------
#limpar os dados
#--------------------------------------------

df1 = clean_code(df)


#============================================
# Barra lateral
#============================================

# Título
st.header('Marketplace - Visão Entregadores')

# imagem
#image_path = '/home/IvanBertaci/Documentos/CIENCIAS_DADOS/COMUNIDADEDS/REPOS/logo.jpeg'
image = Image.open( 'logo.jpeg' )
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

#Filtro de botões por condições climáticas
climate_options = st.sidebar.multiselect('Quais as condições climáticas',
						 ['conditions Cloudy', 'conditions Fog', 'conditions Fog-Rain', 'conditions Rain', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'], 
						 default=['conditions Cloudy', 'conditions Fog', 'conditions Fog-Rain', 'conditions Rain', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

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

# filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(climate_options)
df1 = df1.loc[linhas_selecionadas, :]

#============================================
# Layout do Streamlit
#============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''] )

with tab1:
	with st.container():
		st.title( 'Overall Metrics' )
		col1, col2, col3, col4 = st.columns( 4 )
		with col1:
			maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
			col1.metric( 'Maior de idade', maior_idade )

		with col2:
			menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
			col2.metric( 'Menor idade', menor_idade )

		with col3:
			melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
			col3.metric( 'Melhor condicao', melhor_condicao )

		with col4:
			pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
			col4.metric( 'Pior condicao', pior_condicao)

	with st.container():
		st.markdown( """---""" )
		st.title( 'Avaliacoes' )
		col1, col2 = st.columns( 2 )
		with col1:
			st.markdown('##### Avaliacao media por entregador')
			df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
								 .groupby( 'Delivery_person_ID' ).mean().reset_index() )
			st.dataframe( df_avg_ratings_per_deliver )

		with col2:
			st.markdown('##### Avaliacao media por transito')
			df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
								   .groupby( 'Road_traffic_density' ).agg( {'Delivery_person_Ratings': ['mean', 'std'] } ) )
			#mudar de nome das colunas
			df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

			#resetar o index
			df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

			st.dataframe( df_avg_std_rating_by_traffic )

			st.markdown('##### Avaliacao media por clima')
			df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
								   .groupby( 'Weatherconditions' ).agg( {'Delivery_person_Ratings': ['mean', 'std'] } ) )
			
			#mudar de nome das colunas
			df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

			#resetar o index
			df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()

			st.dataframe( df_avg_std_rating_by_weather )
	
	with st.container():
		st.markdown( """---""" )
		st.title( 'Velocidade de Entrega' )
		col1, col2 = st.columns( 2 )
		with col1:
			st.markdown('##### Entregadores mais rápidos')
			df3 = top_deliveries( df1, top_asc=True )
			st.dataframe( df3 )
			
		with col2:
			st.markdown('##### Entregadores menos rápidos')
			df3 = top_deliveries( df1, top_asc=False )
			st.dataframe(df3)

#st.dataframe(df1)