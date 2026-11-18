import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA - Inteligencia Competitiva", layout="wide")
st.title("📊 Análisis Exploratorio de Datos (EDA) - Precios Supermercados")

# 1. Carga de datos (Podés leer el CSV exportado desde Colab)
@st.cache_data
def cargar_datos():
    # Reemplazá por la ruta de tu archivo limpio o muestra de 50.000 filas
    return pd.read_csv("df_features_muestra.csv")

df = cargar_datos()

# --- SECCIÓN 1: FRECUENCIAS ---
st.header("1. Diagramas de Frecuencia por Cadena")
col1, col2 = st.columns(2)

with col1:
    freq_super = df['supermercado'].value_counts().reset_index()
    freq_super.columns = ['Supermercado', 'Cantidad de Registros']
    fig_bar = px.bar(
        freq_super, x='Supermercado', y='Cantidad de Registros',
        color='Supermercado', title="Frecuencia de Productos Analizados por Cadena"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    freq_cadenas = df['cant_cadenas'].value_counts().reset_index()
    freq_cadenas.columns = ['Cadenas en Simultáneo', 'Cantidad de Productos']
    fig_freq2 = px.bar(
        freq_cadenas, x='Cadenas en Simultáneo', y='Cantidad de Productos',
        title="Frecuencia de Coincidencia de Productos entre Supermercados"
    )
    st.plotly_chart(fig_freq2, use_container_width=True)

# --- SECCIÓN 2: DISTRIBUCIONES ---
st.header("2. Distribuciones de Precios y Ratios")
col3, col4 = st.columns(2)

with col3:
    # Filtramos outliers extremos solo para que el histograma se lea bien
    df_sin_extremos = df[df['precio_lista'] < df['precio_lista'].quantile(0.95)]
    fig_hist1 = px.histogram(
        df_sin_extremos, x='precio_lista', nbins=50,
        title="Distribución del Precio de Lista (Asimetría Positiva)"
    )
    st.plotly_chart(fig_hist1, use_container_width=True)

with col4:
    df_ratio_acotado = df[(df['ratio_vs_mercado'] >= 0.5) & (df['ratio_vs_mercado'] <= 1.5)]
    fig_hist2 = px.histogram(
        df_ratio_acotado, x='ratio_vs_mercado', color='supermercado',
        nbins=50, barmode='overlay',
        title="Distribución de Competitividad (Ratio vs. Media del Mercado)"
    )
    st.plotly_chart(fig_hist2, use_container_width=True)

# --- SECCIÓN 3: MATRIZ DE CORRELACIÓN ---
st.header("3. Matriz de Correlación entre Variables Numéricas")
features_numericas = [
    'precio_lista', 'precio_promo', 'precio_lista_medio',
    'ratio_vs_mercado', 'descuento_anunciado', 'ratio_promo_vs_mercado', 'cant_cadenas'
]
corr = df[features_numericas].corr()

fig_corr = px.imshow(
    corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
    title="Mapa de Calor de Correlaciones (Pearson)"
)
st.plotly_chart(fig_corr, use_container_width=True)

# --- SECCIÓN 4: SELECCIÓN DE FEATURES ---
st.header("4. Selección Final de Features (7 Variables)")
st.markdown("""
* **Features Lineales (3):** `precio_lista`, `precio_promo`, `precio_lista_medio`
* **Features No Lineales / Ratios (4):** `ratio_vs_mercado`, `descuento_anunciado`, `ratio_promo_vs_mercado`, `cant_cadenas`
""")