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

st.set_page_config( page_title="Visão Empresa", page_icon=":chart_with_upwards_trend:", layout="wide")

#--------------------------------------------
#funções
#--------------------------------------------
def country_maps( df1 ):
    df_aux = ( df1.loc[:, ["City" , "Road_traffic_density" , "Delivery_location_latitude" , "Delivery_location_longitude"]]
              .groupby( ["City" ,"Road_traffic_density"])
              .median()
              .reset_index() )
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker( [ location_info["Delivery_location_latitude"],
                       location_info["Delivery_location_longitude"]] ).add_to( map )
    folium_static( map, width=1024 , height=600 )



def order_share_by_week( df1 ):
        df_aux01 = df1.loc[:,["ID" ,"week_of_year" ]].groupby( "week_of_year").count().reset_index()
        df_aux02 = ( df1.loc[:, ["Delivery_person_ID" , "week_of_year"]]
                        .groupby("week_of_year")
                        .nunique()
                        .reset_index() )
        #juntar as 2 coisas --- usar comando merge()
        df_aux = pd.merge( df_aux01, df_aux02, how="inner" )
        #criou uma nova coluna e fez a divisão
        df_aux["order_by_deliver"] = df_aux["ID"] / df_aux["Delivery_person_ID" ]
        fig = px.line(df_aux, x="week_of_year" , y="order_by_deliver" )
        return fig


def order_by_week( df1 ):
        df1["week_of_year"] = df1["Order_Date"].dt.strftime( "%U" )
        df_aux = df1.loc[:, ["ID", "week_of_year"]].groupby( "week_of_year" ).count().reset_index()
        fig = px.line( df_aux, x="week_of_year", y="ID" )
        return fig

def traffic_order_city( df1 ): 
            
            df_aux = ( df1.loc[:, ["ID" ,"City" , "Road_traffic_density"]]
                          .groupby(["City" , "Road_traffic_density"] )
                          .count()
                          .reset_index() )

#grafico de bolhas
            fig = px.scatter( df_aux, x="City" , y="Road_traffic_density" , size="ID" , color="City" )
            return fig 


def traffic_order_share( df1 ):
        #Road_traffic_density Delivery_person_ID
        cols = ["ID" , "Road_traffic_density"]
        df_aux = ( df1.loc[: , cols]
                      .groupby("Road_traffic_density")
                      .count()
                      .reset_index() )
        #df_aux
        #Até aqui me deu numeros e eu quero percentual então:criou outra colunas
        df_aux["entregas_perc"] = df_aux["ID"] / df_aux["ID"].sum()

        #tenho que tirar os NaN
        df_aux = df_aux.loc[df_aux["Road_traffic_density"] != "NaN" , :]
        #df_aux

        #gerando o grafico de pizza
        fig = px.pie( df_aux, values="entregas_perc" , names="Road_traffic_density" )
        
        return fig


def order_metric( df1 ):
        #colunas selecionadas
    cols = ["ID" , "Order_Date"]
    df_aux = df1.loc[: , cols].groupby("Order_Date").count().reset_index()
    #desenhar grafico de barras
    fig = px.bar(df_aux, x= "Order_Date" , y="ID")
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

#--------------------------------------------------- Inicio da estrutura logica do codigo-----------------------------------------------------------------
#import dataset
#--------------------
df = pd.read_csv( "dataset/train.csv" )
#print(df.head())
#--------------------
#LIMPANDO DADOS 
#---------------------
df1 = clean_code ( df )


#================================================
#Barra lateral
#================================================

#st.header('This is a header')
st.header( "Marketplace - Visão cliente" )

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
    default=["Low" , "Medium", "High", "Jam"] )

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

tab1,tab2,tab3 = st.tabs( ["Visão Gerencial", "Visão Tática", "Visão Geográfica"] )

with tab1:
    with st.container():
         # Order Metric
        fig = order_metric( df1 )
        st.markdown( "# Orders by Day" )
        st.plotly_chart(fig,use_container_width=True )
        
    with st.container():
            coluna1, coluna2 = st.columns( 2 )
        
            with coluna1:
                fig = traffic_order_share( df1 )
                st.header("Traffic_Order_Share" )
                st.plotly_chart( fig, use_container_width=True )
    
                    
                
            with coluna2:
                st.header("Traffic Order City" )
                fig = traffic_order_city ( df1 )
                

                st.plotly_chart( fig, use_container_widt=True )
               
                   

with tab2:
    with st.container():
        st.markdown( "# Order by Week" )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
     
        
    with st.container():
        st.markdown( "# Order Share by Week" )
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
   
       
        
    
with tab3:
    st.markdown( "# Country Maps" )
    country_maps( df1 )
    
   















