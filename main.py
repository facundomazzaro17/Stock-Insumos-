import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión de Insumos", layout="wide")

# --- CONFIGURACIÓN DE LINKS ---
URL_SALDOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMypw6QM6exXIVOGtCdfJEUTMw9vQ7PrAsX1um9zGMTv88i7obR-4EerL7n86BfwxZkZ_1Wa0MB9l1/pub?gid=10065180&single=true&output=csv"
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMypw6QM6exXIVOGtCdfJEUTMw9vQ7PrAsX1um9zGMTv88i7obR-4EerL7n86BfwxZkZ_1Wa0MB9l1/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def cargar_datos(url):
    # Si el link es el de SALDOS (Stock Actual), aplicamos la limpieza de filas
    if url == URL_SALDOS:
        df = pd.read_csv(url, skiprows=2)
        df = df.dropna(axis=1, how='all')
        if 'Unnamed: 1' in df.columns:
            df = df.rename(columns={'Unnamed: 1': 'PRODUCTO'})
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        return df
    else:
        # Si es el de MOVIMIENTOS, lo cargamos normal
        return pd.read_csv(url)
        
# --- MENÚ LATERAL ---
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["📦 Stock Actual", "🕒 Historial de Movimientos"])

# --- VISTA 1: STOCK ACTUAL ---
if opcion == "📦 Stock Actual":
    st.title("📊 Estado de Inventario")
    try:
        df_saldos = cargar_datos(URL_SALDOS)
        df_saldos.columns = [c.strip() for c in df_saldos.columns]

        # --- CREACIÓN DE PESTAÑAS ---
        tab1, tab2, tab3 = st.tabs(["📥 Entradas (C-AB)", "📤 Salidas (AD-BC)", "⚖️ Stock Real (BE-CD)"])

        with tab1:
            st.subheader("Resumen de Entradas por Plaza")
            # Columna 1 (Nombre Producto) + Columnas 2 a 27 (C a AB)
            df_entradas = df_saldos.iloc[:, [1] + list(range(2, 28))]
            st.dataframe(df_entradas, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Resumen de Salidas por Plaza")
            # Columna 1 (Nombre Producto) + Columnas 29 a 54 (AD a BC)
            df_salidas = df_saldos.iloc[:, [1] + list(range(29, 55))]
            st.dataframe(df_salidas, use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("Saldos Actuales Disponibles")
            # Columna 1 (Nombre Producto) + Columnas 56 a 81 (BE a CD)
            df_real = df_saldos.iloc[:, [1] + list(range(56, 82))]
            
            # Formato condicional: Stock 0 o menos en rojo
            def resaltar_negativo(val):
                try:
                    return 'color: red; font-weight: bold' if float(val) <= 0 else ''
                except: return ''
            
            st.dataframe(df_real.style.applymap(resaltar_negativo), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error cargando los saldos: {e}")

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
