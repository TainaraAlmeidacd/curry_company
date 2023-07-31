#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
#bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Entregadores", page_icon="	:articulated_lorry:", layout="wide")
#--------------------------------------------
#funções
#--------------------------------------------
def top_delivers( df1, top_asc ):
    df2 = ( df1.loc[:, ["Delivery_person_ID" , "City" ,  "Time_taken(min)"]]
               .groupby(["City" , "Delivery_person_ID"] )
               .max().sort_values([ "City","Time_taken(min)"],ascending=top_asc )
               .reset_index() )

    df_aux01 = df2.loc[df2["City"] == "Metropolitian" , :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban" , :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban" , :].head(10)
    df3 = pd.concat( [ df_aux01, df_aux02, df_aux03 ] ).reset_index(drop=True )
    return df3
           
def clean_code( df1 ):
    """ Está função tem a resposabilidade de limpar o dataframe 
        Tipos de limpeza:
        1. Remoção  dos dados NaN
        2.Mudança do tipo da coluna de dados
        3.Remoção dos espaços das variaveis de textos 
        4.Formatação da coluna de  datas
        5.Limpeza da coluna de tempo ( Remoção do texto da variavel numerica )

        input: Dataframe
        Output: Dataframe
    
    """

    
    # 1 covertendo a coluna Age de texto para numero
    linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["Road_traffic_density"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    
    linhas_selecionadas = (df1["City"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["Festival"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    
    linhas_selecionadas = (df1["multiple_deliveries"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1["Time_taken(min)"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    
    # 2 convertendo a coluna ratings de texto para numero decimal (float)
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype ( float )
    
    # 3 convertendo a coluna order_date de texto para data
    df1["Order_Date"] = pd.to_datetime( df1["Order_Date"], format="%d-%m-%Y")
    
    #4 convertendo multiple_deliveres de texto para numero interiro ( int )
    
    df1 = df1[df1.loc[:,'multiple_deliveries'].notnull()]
    df1['multiple_deliveries'] =  df1['multiple_deliveries'].astype( int )
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype( int )
    
    
    # 5 removendo os espaços dentro de strings/texto/object
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    df1.loc[:,"Festival"] = df1.loc[:, "Festival"].str.strip()
    
    
    # 6 limpando a coluna de time taken
    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply( lambda x: x.split( "(min)" )[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)" ].astype( int )
    #print("certo")
    #print( df.head() )

    return df1

#import dataset
df = pd.read_csv( "dataset/train.csv" )

df1 = clean_code( df )
#================================================
#Barra lateral
#================================================

#st.header('This is a header')
st.header( "Marketplace - Visão Entregadores" )

image_path = "imagem.jpg"
image = Image.open( "imagem.jpg" )
st.sidebar.image( image, width=120 )
st.sidebar.markdown ( "# Cury Company" )
st.sidebar.markdown ( "## Fastest Delivery in Town" )
st.sidebar.markdown("""---""")

st.sidebar.markdown( "## Selecionar uma data limite" )

date_slider = st.sidebar.slider(
    "Até qual valor?",
#value=pd.datetime( 2022, 4, 13),
#min_value=pd.datetime(2022, 2, 11 ),
#max_value=pd.datetime(2022, 4, 6 ),
    value = datetime.strptime(pd.to_datetime("2022/4/13").strftime("%Y-%m-%d"), "%Y-%m-%d"),
    min_value = datetime.strptime(pd.to_datetime("2022/2/11").strftime("%Y-%m-%d"), "%Y-%m-%d"),
    max_value = datetime.strptime(pd.to_datetime("2022/4/6").strftime("%Y-%m-%d"), "%Y-%m-%d"),
    format = "DD-MM-YYYY" )

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    "Quais as condições do trânsito",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"] )

st.sidebar.markdown("""---""")
st.sidebar.markdown( "### Powered by Comunidade DS" )
#Filtro de datas
linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
#filtro de trânsito
linhas_selecionadas = df1["Road_traffic_density"].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#================================================
#Layout Stramlit 
#================================================

tab1,tab2,tab3 = st.tabs( ["Visão Gerencial", "_", "_"] )
with tab1:
    with st.container():
        st.title( "Overall Metrics" )
        coluna1,coluna2,coluna3,coluna4 = st.columns( 4, gap="large" )
        with coluna1:
            #maior idade dos entregadores 
           
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            coluna1.metric( "Maior de idade",maior_idade )
            
        with coluna2:
            #menor idade  dos entregadores
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            coluna2.metric( "Menor idade", menor_idade )

            
        with coluna3:
            #melhor condição de veiculos 
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            coluna3.metric( "Melhor condicao", melhor_condicao )
            
        with coluna4:
            # pior condição de veiculos 
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            coluna4.metric( " pior condicao", pior_condicao )

            
    with st.container():
        st.markdown( """---""" )
        st.title("Avaliações" )
        coluna1, coluna2 = st.columns( 2 )
        with coluna1:
            st.markdown( "##### Avaliação medias por entregador" )
            df_avaliacao_media = (  df1.loc[: , ["Delivery_person_Ratings" , "Delivery_person_ID"]]
                                     .groupby(["Delivery_person_ID"])
                                     .mean()
                                     .reset_index() )
            st.dataframe( df_avaliacao_media )

        with coluna2:
            st.markdown( "##### Avaliação media por transito" )
            df_media_std =  ( df1.loc[: , ["Delivery_person_Ratings" , "Road_traffic_density"]]
                                 .groupby(["Road_traffic_density"])
                                 .agg({"Delivery_person_Ratings" : ["mean" , "std"]}) )
            df_media_std.columns = [ "delivery_mean" , "delivery_std"]
            df_media_std = df_media_std.reset_index()
            st.dataframe( df_media_std )

            st.markdown( "##### Avaliação media por clima" )
            df_media_Weather_std = (  df1.loc[: , ["Delivery_person_Ratings" , "Weatherconditions"]]
                                 .groupby(["Weatherconditions"])
                                 .agg({"Delivery_person_Ratings" : ["mean" , "std"]}) )
            df_media_Weather_std.columns = [ "delivery_mean" , "delivery_std"]
            df_media_Weather_std = df_media_Weather_std.reset_index()
            st.dataframe( df_media_Weather_std )

    
            
    with st.container():
        st.markdown( """---""" )
        st.title("Velocidade de entrega" )

        coluna1, coluna2 = st.columns( 2 )
        with coluna1:
            st.markdown( "##### Top Entregadores mais rapidos" )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            
        with coluna2:
            st.markdown("##### Top Entregadores mais lentos" )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
            
          




