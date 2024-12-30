import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict
import os
import json
from datetime import datetime, timedelta

# File-based caching
CACHE_FILE = "cached_data.txt"
CACHE_EXPIRY_DAYS = 1  # Cache expiry in days

# Save data to cache file
def save_to_cache(data: pd.DataFrame, timestamp: str) -> None:
    """Saves data and timestamp to a cache file."""
    data_reset = data.reset_index().rename(columns={'index': 'Ticker'})
    with open(CACHE_FILE, "w") as file:
        cache = {
            "timestamp": timestamp,
            "data": data_reset.to_dict(orient="list")
        }
        json.dump(cache, file)

# Load data from cache file
def load_from_cache() -> Dict:
    """Loads data and timestamp from the cache file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            cache = json.load(file)
            cache_timestamp = datetime.strptime(cache["timestamp"], "%Y-%m-%d %H:%M:%S")
            is_expired = datetime.now() - cache_timestamp > timedelta(days=CACHE_EXPIRY_DAYS)
            df = pd.DataFrame(cache["data"]).set_index("Ticker")
            return {
                "data": df,
                "timestamp": cache["timestamp"],
                "is_expired": is_expired
            }
    return None



# Configuración de la página
st.set_page_config(
    page_title="CONSENSUS",
    page_icon="📈",
    layout="wide"
)

# Título y descripción
st.title("📊 CONSENSUS")
st.markdown("""
Esta aplicación analiza las posiciones principales de los mejores fondos de inversión para rankear
las acciones en las que más invierten.            
""")

# Valores fijos (eliminamos el sidebar)
MIN_APPEARANCES = 6
SIMILARITY_THRESHOLD = 85


# Check cache
cache = load_from_cache()
if cache and not cache['is_expired']:
    st.session_state.button_disabled = True

# Function to display data
def display_data(df: pd.DataFrame, timestamp: str = None):
    # if timestamp:
    #     st.info(f"Mostrando datos en caché cargados el {timestamp}.")
    # Modificar el layout para dar más espacio a la visualización
    col1, col2 = st.columns([1, 2])  # Proporción 1:2 para las columnas

    with col1:
        st.subheader("📋 Tabla de Resultados")
        # Ajustar el estilo de la tabla
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Appearances": st.column_config.NumberColumn(
                    "Apariciones",
                    width=40,
                    format="%d"
                ),
                "__index__": st.column_config.TextColumn(
                    "Símbolo",
                    width="medium"
                )
            },
            height=400  # Ajustar altura de la tabla
        )

    with col2:
        st.subheader("📊 Visualización")
        fig = px.bar(
            df,
            x=df.index,
            y='Appearances',
            title='Frecuencia de Aparición de Acciones',
            labels={'Appearances': 'Número de Apariciones', 'index': 'Símbolo'},
            color='Appearances',
            color_continuous_scale='blues'
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=500,
            width=1200,  # Hacer el gráfico más ancho
            margin=dict(l=20, r=20, t=40, b=20)  # Ajustar márgenes
        )
        st.plotly_chart(fig, use_container_width=True)

    # Métricas principales
    st.subheader("📈 Métricas Principales")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    with metrics_col1:
        st.metric(
            "Total de Acciones Analizadas",
            len(df)
        )

    with metrics_col2:
        st.metric(
            "Apariciones Máximas",
            df['Appearances'].max()
        )

    with metrics_col3:
        st.metric(
            "Apariciones Promedio",
            round(df['Appearances'].mean(), 2)
        )

    st.download_button(
        label="📥 Descargar Datos",
        data=df.to_csv(index=True),
        file_name="stock_analysis.csv",
        mime="text/csv",
        key=f"download_data_button_{timestamp}"  # Use a dynamic key based on timestamp
    )





# If not loading new data, check if cached data is available and display
if  cache:
    df_stocks = cache['data']
    display_data(df_stocks, cache['timestamp'])

# Agregar información adicional al final
st.markdown("""
---
### 👨‍💻 Autor
**Jaume Antolí Plaza**

[![Twitter](https://img.shields.io/twitter/follow/jantolip?style=social)](https://twitter.com/jantolip)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-blue?style=social&logo=linkedin)](https://linkedin.com/in/jaume-antoli-plaza)

### 📊 Metodología
- Los datos se obtienen de los fondos de inversión de renta variable con mejor rentabilidad a 10 años
- Solo se consideran las 10 principales posiciones de cada fondo
- Se filtran fondos similares para evitar duplicidad
- Solo se muestran acciones estadounidenses

### 🎯 Cómo Interpretar los Resultados
- Un mayor número de apariciones indica que más fondos exitosos confían en esa acción
- Los resultados son una foto fija del momento actual
- La presencia en múltiples fondos puede indicar consenso pero no garantiza rendimiento futuro

### 🔒 Privacidad
Esta aplicación no utiliza cookies ni almacena datos personales. Todos los análisis se realizan en tiempo real.

### ⚠️ Aviso Legal
Esta aplicación es solo para fines informativos y educativos. No constituye asesoramiento financiero, recomendación de inversión ni oferta de compra o venta de valores. Los datos mostrados se obtienen de fuentes públicas y su precisión no está garantizada. Las decisiones de inversión deben tomarse tras realizar un análisis propio o consultar con un asesor financiero profesional. El autor no se hace responsable de las decisiones tomadas basándose en esta información.

### 🔄 Versión
- v1.0.0 (Noviembre 2024)
            
""")
