import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA - Inteligencia Competitiva", layout="wide")
st.title("📊 Análisis Exploratorio de Datos (EDA) - Precios Supermercados")

# 1. Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("df_limpio.csv")
    
    # Acortamos los nombres legales largos a nombres comerciales directos
    nombres_cortos = {
        "INC S.A.": "Carrefour (INC S.A.)",
        "COTO CENTRO INTEGRAL DE COMERCIALIZACION S.A.": "Coto S.A.",
        "Cooperativa Obrera Limitada de Consumo y Vivienda": "Cooperativa Obrera",
        "Cencosud S.A.": "Cencosud (Jumbo/Disco/Vea)",
        "DIA Argentina S.A.": "DIA Argentina S.A."
    }
    df['supermercado'] = df['supermercado'].replace(nombres_cortos)
    
    # Compatibilidad mínima por si df_limpio.csv aún no tiene las columnas de ratios
    if 'productos_precio_lista' in df.columns and 'precio_lista' not in df.columns:
        df = df.rename(columns={
            'productos_precio_lista': 'precio_lista',
            'precio_promo_limpio': 'precio_promo'
        })
    if 'precio_promo' not in df.columns:
        df['precio_promo'] = df['precio_lista']
    if 'ratio_vs_mercado' not in df.columns:
        df_med = df.groupby(['fecha', 'id_producto'], as_index=False).agg(
            precio_lista_medio=('precio_lista', 'median'),
            cant_cadenas=('supermercado', 'nunique')
        )
        df = df.merge(df_med, on=['fecha', 'id_producto'])
        df['ratio_vs_mercado'] = df['precio_lista'] / df['precio_lista_medio']
        df['descuento_anunciado'] = (df['precio_lista'] - df['precio_promo']) / df['precio_lista']
        df['ratio_promo_vs_mercado'] = df['precio_promo'] / df['precio_lista_medio']
        
    return df

df = cargar_datos()

# --- SECCIÓN 1: FRECUENCIAS (MÁS GRANDE, LETRAS MAYORES Y A LA IZQUIERDA) ---
st.header("1. Diagrama de Frecuencia por Cadena")
freq_super = df['supermercado'].value_counts().reset_index()
freq_super.columns = ['Supermercado', 'Cantidad de Registros']
fig_bar = px.bar(
    freq_super, x='Supermercado', y='Cantidad de Registros',
    color='Supermercado', title="Frecuencia de Productos Analizados por Cadena",
    text_auto='.2s', width=1050, height=650
)
fig_bar.update_traces(textposition='outside', textfont_size=15)
fig_bar.update_xaxes(tickangle=45, tickfont=dict(size=14), title_font=dict(size=16))
fig_bar.update_yaxes(tickfont=dict(size=14), title_font=dict(size=16))
fig_bar.update_layout(
    title_font=dict(size=20),
    legend=dict(font=dict(size=14), title_font=dict(size=15))
)
st.plotly_chart(fig_bar, use_container_width=False)

# --- SECCIÓN 2: DISTRIBUCIONES ---
st.header("2. Distribuciones de Precios y Ratios")
col1, col2 = st.columns(2)

with col1:
    df_sin_extremos = df[df['precio_lista'] < df['precio_lista'].quantile(0.95)]
    fig_hist1 = px.histogram(
        df_sin_extremos, x='precio_lista', nbins=50,
        title="Distribución del Precio de Lista (Asimetría Positiva)"
    )
    st.plotly_chart(fig_hist1, use_container_width=True)

with col2:
    df_ratio_acotado = df[(df['ratio_vs_mercado'] >= 0.5) & (df['ratio_vs_mercado'] <= 1.5)]
    fig_hist2 = px.histogram(
        df_ratio_acotado, x='ratio_vs_mercado', color='supermercado',
        nbins=50, barmode='overlay',
        title="Distribución de Competitividad (Ratio vs. Media del Mercado)"
    )
    st.plotly_chart(fig_hist2, use_container_width=True)

# --- SECCIÓN 3: MATRIZ DE CORRELACIÓN (LETRAS MÁS GRANDES Y A LA IZQUIERDA) ---
st.header("3. Matriz de Correlación entre Variables Numéricas")
features_numericas = [
    'precio_lista', 'precio_promo', 'precio_lista_medio',
    'ratio_vs_mercado', 'descuento_anunciado', 'ratio_promo_vs_mercado', 'cant_cadenas'
]
corr = df[features_numericas].corr()

fig_corr = px.imshow(
    corr, text_auto=".2f", color_continuous_scale="RdBu_r",
    title="Mapa de Calor de Correlaciones (Pearson)",
    width=760, height=760
)
fig_corr.update_traces(textfont_size=15)
fig_corr.update_xaxes(tickfont=dict(size=14))
fig_corr.update_yaxes(scaleanchor="x", scaleratio=1, tickfont=dict(size=14))
fig_corr.update_layout(title_font=dict(size=20))
st.plotly_chart(fig_corr, use_container_width=False)

# --- SECCIÓN 4: SELECCIÓN DE FEATURES ---
st.header("4. Selección Final de Features (7 Variables)")
col_lin, col_nolin = st.columns(2)

with col_lin:
    with st.container(border=True, height=260):
        st.subheader("📈 Variables Lineales (3)")
        st.markdown("""
        * **`precio_lista`**: Es el precio común de góndola, sin aplicar ningún descuento ni oferta.
        * **`precio_promo`**: Es el precio final que paga el cliente cuando el producto está en oferta.
        * **`precio_lista_medio`**: Es el precio promedio de ese mismo producto sumando todos los supermercados, usado como referencia.
        """)

with col_nolin:
    with st.container(border=True, height=260):
        st.subheader("⚙️ Variables No Lineales / Ratios (4)")
        st.markdown("""
        * **`ratio_vs_mercado`**: Indica si el precio común del súper está más barato (menor a 1) o más caro (mayor a 1) que el promedio.
        * **`descuento_anunciado`**: Muestra qué porcentaje real de rebaja tiene la oferta respecto a su propio precio de lista.
        * **`ratio_promo_vs_mercado`**: Comprueba si el precio en oferta realmente le gana al promedio de la competencia.
        * **`cant_cadenas`**: Cuenta en cuántos supermercados distintos se vende ese producto para asegurar que sea comparable.
        """)
