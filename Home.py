import streamlit as st
from PIL import Image
st.set_page_config(
    page_title="Home",
    page_icon= ":game_die:" 

)

#image_path = "/Users/Tamiris Luzia/Documents/repos_juplab/"
image = Image.open( "imagem.jpg" )
st.sidebar.image(image, width=120 )
st.sidebar.markdown ( "# Cury Company" )
st.sidebar.markdown ( "## Fastest Delivery in Town" )
st.sidebar.markdown( """---""" )
st.write( "# Curry Company Growth Dashboard" )
st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como ultilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográficas: Insights de geolocalização.
        - Visão Entregador
        - Acompanhamento dos indicadores semanais de crescimento 
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes 
    ### Ask for Help 
    - Time de Data Science no Discord 
        -@tainara.09
    """ )

#Documents/repos_juplab/imagem.jpg
# se der errrado tente este http://localhost:51341/lab/tree/Documents/repos_juplab/imagem.jpg