import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', page_icon='🏙️')

#image_path = '/home/IvanBertaci/Documentos/CIENCIAS_DADOS/COMUNIDADEDS/REPOS/logo.jpeg'
image = Image.open( 'logo.jpeg' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company - Growth Analytics")

texto = """
Growth Analystic foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
### Como utilizar esse Growth Analystic?
- Visão Empresa
  - Visão Gerencial: Métricas gerais de comportamento
  - Visão Tática: Indicadores semanais de crescimento
  - Visão Geográfica: Insights de geolocalização
- Visão Entregadores:
  - Acompanhamento dos indicadores semanais de crescimento
- Visão Restaurantes:
  - Indicadores semanais de crescimento dos restaurantes

### Ask for Help
- Time de Data Science no Discord
- Canal de Comunidade DS no Discord
- Canal de Comunidade DS no Twitter
"""

st.markdown(texto)