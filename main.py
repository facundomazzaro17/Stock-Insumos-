import streamlit as st
import pandas as pd

st.set_page_config(page_title="Control de Insumos", layout="wide")

# --- CONFIGURACIÓN ---
# PEGA ACÁ EL LINK QUE COPIASTE EN EL PASO 1 (EL DEL CSV)
URL_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtpcWfHUopX22hA6rg-Q2MdmO1ryrp3ZL0JX__XSvFcZX2MBoOvjDaWVxBxnC5r5ArQ_ZVkbsb3yiR/pub?output=csv"

@st.cache_data(ttl=60) # Se actualiza cada 1 minuto
def cargar_datos():
    df = pd.read_csv(URL_SHEETS)
    return df

st.title("📦 Panel de Control de Insumos")

try:
    df = cargar_datos()
    
    # --- LÓGICA PARA PROCESAR TUS COLUMNAS REPETIDAS ---
    # Esto busca todas las columnas que digan "Producto" y "Cantidad"
    prod_cols = [c for c in df.columns if 'Producto' in c]
    cant_cols = [c for c in df.columns if 'Cantidad' in c]
    
    movimientos = []
    
    for _, fila in df.iterrows():
        for p_col, c_col in zip(prod_cols, cant_cols):
            producto = fila[p_col]
            cantidad = fila[c_col]
            
            if pd.notna(producto) and pd.notna(cantidad):
                # Si salió de una plaza, es resta
                if pd.notna(fila['SALIDA']):
                    movimientos.append({'Plaza': fila['SALIDA'], 'Producto': producto, 'Cantidad': -cantidad})
                # Si entró a una plaza, es suma
                if pd.notna(fila['ENTRADA']):
                    movimientos.append({'Plaza': fila['ENTRADA'], 'Producto': producto, 'Cantidad': cantidad})

    df_movs = pd.DataFrame(movimientos)
    
    # --- CÁLCULO DE STOCK ACTUAL ---
    stock_total = df_movs.groupby(['Plaza', 'Producto'])['Cantidad'].sum().reset_index()

    # --- INTERFAZ ---
    plaza_sel = st.selectbox("Seleccioná una Plaza:", stock_total['Plaza'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Stock Actual en {plaza_sel}")
        resumen = stock_total[stock_total['Plaza'] == plaza_sel]
        st.dataframe(resumen[['Producto', 'Cantidad']], use_container_width=True)

    with col2:
        st.subheader("Alertas de Stock Bajo")
        bajo = resumen[resumen['Cantidad'] < 5] # Podés cambiar este número
        if not bajo.empty:
            st.error("¡Atención! Reponer los siguientes insumos:")
            st.table(bajo)
        else:
            st.success("Todo en orden. Stock suficiente.")

except Exception as e:
    st.warning("Configurando conexión... Asegurate de pegar el link del Sheets en el código.")
