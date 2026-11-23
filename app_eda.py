import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA - Inteligencia Competitiva", layout="wide")
st.title("📊 Análisis Exploratorio de Datos (EDA) - Precios Supermercados")

# Orden oficial de los 10 rubros testigo definidos en el Colab v2
RUBROS_10 = [
    'Leche', 'Yerba', 'Aceite', 'Fideos', 'Arroz',
    'Azucar', 'Queso', 'Gaseosa', 'Detergente', 'Papel Higienico'
]

# 1. Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("df_limpio_v2.csv")
    
    # Acortamos los nombres legales largos a nombres comerciales directos
    nombres_cortos = {
        "INC S.A.": "Carrefour (INC S.A.)",
        "COTO CENTRO INTEGRAL DE COMERCIALIZACION S.A.": "Coto S.A.",
        "Cooperativa Obrera Limitada de Consumo y Vivienda": "Cooperativa Obrera",
        "Cencosud S.A.": "Cencosud (Jumbo/Disco/Vea)",
        "DIA Argentina S.A.": "DIA Argentina S.A."
    }
    df['supermercado'] = df['supermercado'].replace(nombres_cortos)
    return df

df = cargar_datos()

# Paleta fija por cadena para mantener consistencia visual entre todos los gráficos
COLORES_SUPER = {
    "DIA Argentina S.A.": "#636EFA",
    "Carrefour (INC S.A.)": "#EF553B",
    "Coto S.A.": "#00CC96",
    "Cooperativa Obrera": "#AB63FA",
    "Cencosud (Jumbo/Disco/Vea)": "#FFA15A"
}

# CSS puntual para ubicar el desplegable de la Sección 1 justo debajo de la leyenda "Supermercado"
st.markdown("""
<style>
div[data-testid="stVerticalBlock"]:has(> div.element-container div#anchor-sec1) + div[data-testid="stVerticalBlock"] {
    position: relative;
    z-index: 10;
    margin-top: -435px;
    margin-left: 785px;
    width: 260px;
    margin-bottom: 340px;
}
</style>
""", unsafe_allow_html=True)

# --- SECCIÓN 1: PRECIO POR SUPERMERCADO POR RUBRO ---
st.header("1. Comparativa de Precio por Supermercado según Rubro")

# Renderizamos primero el selector para que el gráfico se dibuje al instante con el valor elegido
col_dummy, _ = st.columns([1, 3])
with col_dummy:
    rubro_sec1 = st.selectbox(
        "Seleccione un Producto:",
        options=RUBROS_10,
        index=0,
        key="select_sec1"
    )

df_rubro1 = df[df['tipo_producto'] == rubro_sec1]
precio_super = (
    df_rubro1.groupby('supermercado', as_index=False)
    .agg(Precio=('precio_lista_ref', 'median'))
    .sort_values('Precio', ascending=True)
)
precio_super.columns = ['Supermercado', 'Precio de Referencia ($)']

fig_bar = px.bar(
    precio_super,
    x='Supermercado',
    y='Precio de Referencia ($)',
    color='Supermercado',
    color_discrete_map=COLORES_SUPER,
    title=f"Precio Mediano de Referencia (Kg/L) por Cadena — {rubro_sec1}",
    text_auto='.2f',
    width=1050,
    height=650
)
fig_bar.update_traces(texttemplate='$%{y:,.2f}', textposition='outside', textfont_size=15)
fig_bar.update_xaxes(tickangle=45, tickfont=dict(size=14), title_font=dict(size=16))
fig_bar.update_yaxes(
    tickfont=dict(size=14),
    title_font=dict(size=16),
    range=[0, precio_super['Precio de Referencia ($)'].max() * 1.15]
)
fig_bar.update_layout(
    title_font=dict(size=20),
    legend=dict(font=dict(size=14), title_font=dict(size=15))
)

# Contenedor del gráfico + posicionamiento del desplegable justo debajo de "Supermercado"
with st.container():
    st.plotly_chart(fig_bar, use_container_width=False)
    st.markdown('<div id="anchor-sec1"></div>', unsafe_allow_html=True)

# Movemos visualmente el selectbox justo debajo de la leyenda derecha del gráfico
st.markdown("""
<script>
const anchor = window.parent.document.getElementById('anchor-sec1');
if (anchor) {
    const selectContainer = anchor.closest('[data-testid="stVerticalBlock"]').previousElementSibling;
    const chartContainer = anchor.closest('[data-testid="stVerticalBlock"]');
    if (selectContainer && chartContainer) {
        selectContainer.style.position = 'absolute';
        selectContainer.style.top = '235px';
        selectContainer.style.left = '785px';
        selectContainer.style.width = '250px';
        selectContainer.style.zIndex = '999';
        chartContainer.style.position = 'relative';
        chartContainer.appendChild(selectContainer);
    }
}
</script>
""", unsafe_allow_html=True)

# --- SECCIÓN 2: DISTRIBUCIONES ---
st.header("2. Distribuciones de Precios y Ratios")
col1, col2 = st.columns(2)

with col1:
    fig_hist1 = px.histogram(
        df,
        x='precio_lista_ref',
        color='tipo_producto',
        nbins=30,
        title="Distribución del Precio de Referencia por Kg/L (10 Rubros)",
        labels={'precio_lista_ref': 'Precio Lista Ref. ($/Kg o L)', 'tipo_producto': 'Rubro'}
    )
    fig_hist1.update_layout(yaxis_title="Frecuencia")
    st.plotly_chart(fig_hist1, use_container_width=True)

with col2:
    df_ratio_acotado = df[(df['ratio_vs_mercado'] >= 0.5) & (df['ratio_vs_mercado'] <= 1.5)]
    fig_hist2 = px.histogram(
        df_ratio_acotado,
        x='ratio_vs_mercado',
        color='supermercado',
        color_discrete_map=COLORES_SUPER,
        nbins=30,
        barmode='overlay',
        title="Distribución de Competitividad (Ratio vs. Mediana del Mercado)",
        labels={'ratio_vs_mercado': 'Ratio vs. Mercado', 'supermercado': 'Supermercado'}
    )
    fig_hist2.update_layout(yaxis_title="Frecuencia")
    st.plotly_chart(fig_hist2, use_container_width=True)

# --- SECCIÓN 3: MATRIZ DE CORRELACIÓN POR RUBRO ---
st.header("3. Matriz de Correlación entre Variables Numéricas por Rubro")

features_numericas = [
    'precio_lista_ref', 'precio_promo_ref', 'precio_mercado_medio',
    'ratio_vs_mercado', 'descuento_anunciado', 'ratio_promo_vs_mercado', 'cantidad_opciones'
]

col_graf3, col_sel3 = st.columns([2.4, 1])

with col_sel3:
    st.markdown("<div style='height: 220px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Seleccione un Rubro:**")
        rubro_sec3 = st.radio(
            "Rubro (Matriz de Correlación)",
            options=RUBROS_10,
            index=0,
            key="radio_sec3",
            label_visibility="collapsed"
        )

with col_graf3:
    df_rubro3 = df[df['tipo_producto'] == rubro_sec3]
    corr = df_rubro3[features_numericas].corr().fillna(0)

    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Mapa de Calor de Correlaciones (Pearson) — {rubro_sec3}",
        width=760,
        height=760
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
    with st.container(border=True, height=330):
        st.subheader("📈 Variables Lineales (3)")
        st.markdown("""
        * **`precio_lista_ref`**: Es la mediana del precio común normalizado por Kg o Litro para cada rubro y cadena.
        * **`precio_promo_ref`**: Es la mediana del precio final normalizado que paga el cliente considerando promociones activas.
        * **`precio_mercado_medio`**: Es la mediana del precio de referencia del rubro sumando todos los supermercados en ese día.
        """)

with col_nolin:
    with st.container(border=True, height=330):
        st.subheader("⚙️ Variables No Lineales / Ratios (4)")
        st.markdown("""
        * **`ratio_vs_mercado`**: Indica si el precio de lista del súper está más barato (menor a 1) o más caro (mayor a 1) que la mediana del mercado.
        * **`descuento_anunciado`**: Muestra qué porcentaje real de rebaja tiene la oferta respecto a su propio precio de lista de referencia.
        * **`ratio_promo_vs_mercado`**: Comprueba si el precio en oferta realmente le gana a la mediana de la competencia.
        * **`cantidad_opciones`**: Cuenta cuántos productos distintos (códigos de barra únicos) ofrece cada cadena dentro de ese rubro.
        """)
