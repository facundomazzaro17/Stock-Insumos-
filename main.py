import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión de Insumos", layout="wide")

# --- CONFIGURACIÓN DE LINKS ---
URL_SALDOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMypw6QM6exXIVOGtCdfJEUTMw9vQ7PrAsX1um9zGMTv88i7obR-4EerL7n86BfwxZkZ_1Wa0MB9l1/pub?gid=10065180&single=true&output=csv"
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMypw6QM6exXIVOGtCdfJEUTMw9vQ7PrAsX1um9zGMTv88i7obR-4EerL7n86BfwxZkZ_1Wa0MB9l1/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def cargar_datos(url):
    return pd.read_csv(url)

# --- MENÚ LATERAL ---
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["📦 Stock Actual", "🕒 Historial de Movimientos"])

# --- VISTA 1: STOCK ACTUAL ---
if opcion == "📦 Stock Actual":
    st.title("📊 Estado de Inventario por Plaza")
    try:
        df_saldos = cargar_datos(URL_SALDOS)
        # Limpieza rápida de columnas
        df_saldos.columns = [c.strip() for c in df_saldos.columns]
        
        # Filtro de Plaza
        plaza_col = 'PLAZA' # Cambiá esto si tu columna se llama "Sucursal" o "Ubicación"
        if plaza_col in df_saldos.columns:
            lista_plazas = ["Todas"] + list(df_saldos[plaza_col].unique())
            sel_plaza = st.selectbox("Filtrar por Plaza:", lista_plazas)
            
            if sel_plaza != "Todas":
                df_saldos = df_saldos[df_saldos[plaza_col] == sel_plaza]
        
        st.dataframe(df_saldos, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error("Error cargando los saldos. Revisá el Link A.")

# --- VISTA 2: HISTORIAL ---
elif opcion == "🕒 Historial de Movimientos":
    st.title("📝 Registro Detallado de Movimientos")
    try:
        df_movs = cargar_datos(URL_MOVIMIENTOS)
        
        # Buscador de texto
        busqueda = st.text_input("🔍 Buscar por producto, comentario o plaza:")
        if busqueda:
            # Filtra en todo el documento si el texto aparece en cualquier celda
            df_movs = df_movs[df_movs.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]
        
        st.write(f"Mostrando {len(df_movs)} registros encontrados:")
        st.dataframe(df_movs, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error("Error cargando los movimientos. Revisá el Link B.")
