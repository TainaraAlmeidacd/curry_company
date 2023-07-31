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
import numpy as np
from streamlit_folium import folium_static
st.set_page_config( page_title="Visão Restaurantes", page_icon=":knife_fork_plate:", layout="wide")

#--------------------------------------------
#funções
#--------------------------------------------
def avg_std_time_on_traffic( df1 ):
    df_aux = ( df1.loc[:, ["City", "Time_taken(min)", "Road_traffic_density"]]
                  .groupby ( ["City", "Road_traffic_density"] )
                  .agg( {"Time_taken(min)": ["mean", "std"]} ) )
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=["City", "Road_traffic_density"], values="avg_time",
                      color="std_time", color_continuous_scale="RdBu",
                      color_continuous_midpoint=np.average(df_aux["std_time"] ) )
    return fig


def avg_std_time_graph( df1 ):
        
    df_aux = df1.loc[:, ["City", "Time_taken(min)"]].groupby( "City" ).agg( {"Time_taken(min)": ["mean", "std"]} )
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name="Control", x=df_aux["City"], y=df_aux["avg_time"], error_y=dict(type="data", array=df_aux["std_time"])))
    fig.update_layout(barmode="group")
    return fig
def avg_std_time_delivery( df1, Festival, op ):
    """
    Esta função calcula o tempo medio e o desvio padrão do tempo de entrega
    Parâmetros:
        Input:
             - df: Dataframe com os dados necessários para o cálculo 
             op: Tipo de operação que precisa ser calculada 
             "avg_time": Calcula o tempo medio 
             "std_time": calcula o desvio padrão do temppo 
             Output:
                 - df:Dataframe com 2 colunas e uma linha
    """

    
    df_aux = ( df1.loc[:, ["Time_taken(min)" , "Festival"]]
                  .groupby( "Festival" )
                  .agg( {"Time_taken(min)" : ["mean" , "std"]}) )
    df_aux.columns = ["avg_time" , "std_time"]
    df_aux = df_aux.reset_index()
  
    df_aux = np.round( df_aux.loc[df_aux["Festival"] == Festival, op], 2 )
    return df_aux

def distance( df1, fig ):
    if fig == False:
        cols = ["Delivery_location_latitude", "Delivery_location_longitude", "Restaurant_latitude", "Restaurant_longitude"]
        df1["distance"] = df1.loc[:, cols].apply( lambda x:
                                    haversine(  (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                                                (x["Delivery_location_latitude"], x["Delivery_location_longitude"]) ), axis=1 )
        avg_distance = np.round(df1["distance"].mean(), 2)
        return avg_distance
    else:
         cols = ["Delivery_location_latitude", "Delivery_location_longitude", "Restaurant_latitude", "Restaurant_longitude"]
         df1["distance"] = df1.loc[:, cols].apply( lambda x:
                                    haversine(  (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                                                (x["Delivery_location_latitude"], x["Delivery_location_longitude"]) ), axis=1 )
         avg_distance = df1.loc[:, ["City", "distance"]].groupby( "City" ).mean().reset_index()
         fig = go.Figure( data=[go.Pie( labels=avg_distance["City"], values=avg_distance["distance"], pull=[0,0.1,0])])

        
         return fig




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
#----------------------------------------------
#import dataset
#----------------------------------------------
df = pd.read_csv( "dataset/train.csv")
#Cleaning Code
df1 = clean_code( df )


#================================================
#Barra lateral
#================================================

#st.header('This is a header')
st.header( "Marketplace - Visão restaurantes" )

image_path = "imagem.jpg"
image = Image.open( "imagem.jpg" )
st.sidebar.image( image, width=120 )
st.sidebar.markdown ( "# Cury Company" )
st.sidebar.markdown ( "## Fastest Delivery in Town" )
st.sidebar.markdown( """---""" )

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

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect(
    "Quais as condições do trânsito",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"] )

st.sidebar.markdown( """---""" )
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
        #ENTREGADORES UNICOS
        st.markdown( """---""" )
        st.title( "Overal Metrics")
        
        coluna1, coluna2, coluna3, coluna4, coluna5, coluna6 = st.columns( 6 )
        with coluna1:
            delivery_unique = df.loc[:, "Delivery_person_ID"].nunique()
            coluna1.metric( "Entregadores", delivery_unique )


        
        # with coluna1:
        #      st.markdown( "##### Coluna1" )
        #      delivery_unique = df.loc[:, "Delivery_person_ID"].nunique()
        #      coluna1.metric( "Entregadores únicos", delivery_unique )
   
        with coluna2:
            #DISTANCIA MEDIA
            avg_distance = distance( df1, fig=False )
            coluna2.metric( " A distância média", avg_distance )                                                  
             
        with coluna3:
            # df_aux = ( df1.loc[:, ["Time_taken(min)" , "Festival"]]
            #       .groupby( "Festival" )
            #               .agg( {"Time_taken(min)" : ["mean" , "std"]}) )
            # df_aux.columns = ["avg_time" , "std_time"]
            # df_aux = df_aux.reset_index()
          
            # df_aux = np.round( df_aux.loc[df_aux["Festival"] == "Yes", "avg_time"], 2 )
            # print(df_aux)
            
            df_aux = avg_std_time_delivery( df1, "Yes", "avg_time" )
            coluna3.metric( "Tempo médio", df_aux )
            



        
        with coluna4:
           df_aux = avg_std_time_delivery( df1, "Yes", "std_time" ) 
           coluna4.metric( "STD Entrega", df_aux )
            

        with coluna5:
            df_aux = avg_std_time_delivery( df1, "No", "avg_time" ) 
            coluna5.metric( "Tempo médio", df_aux )
          
           

        with coluna6:
            df_aux = avg_std_time_delivery( df1, "No", "std_time" )
            coluna6.metric( "std entrega", df_aux )
            
        
        
        
    with st.container():
        st.markdown( """---""" )
        
        coluna1, coluna2 = st.columns ( spec = 2,gap="large" )
        with coluna1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig, use_container_width=True)
            
            
        with coluna2:
             df_aux = ( df1.loc[:, ["City", "Time_taken(min)", "Type_of_order"]]
                           .groupby( ["City", "Type_of_order"])
                           .agg( {"Time_taken(min)": ["mean", "std"]}))
             df_aux.columns = ["avg_time", "std_time"]
             df_aux = df_aux.reset_index()
             st.dataframe( df_aux )

            
        
           
    with st.container():
        st.markdown( """---""" )
        st.title( "Distribuição do tempo")
        
        coluna1, coluna2 = st.columns ( 2 )
        with coluna1:
           fig = distance( df1, fig=True )
           st.plotly_chart( fig, use_container_width=True)
    
     
        with coluna2:
            fig = avg_std_time_on_traffic( df1 )  
            st.plotly_chart( fig, use_container_width=True)
        