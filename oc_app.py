import streamlit as st
import requests
import pandas as pd
import urllib.parse

# Configuración de la página
st.set_page_config(page_title="Visor Auditoría Mercado Público 2026", layout="wide")

st.title("📊 Detalle de Orden de Compra")
st.markdown("Integración API Mercado Público + Respaldo OneDrive")

# --- CONFIGURACIÓN ---

API_TICKET = st.secrets["MP_TICKET"]


OC_LIST = [
    "1866-11-TD26", "1314-4-SE26", "1314-54-CM25", "1314-67-SE25", 
    "1314-62-CM25", "1324-13-AG25", "1314-55-CM25", "1310-7-TD25", 
    "618-481-CM25", "1314-3-CM25", "4293-54-AG25", "618-240-CM25",
    "4293-28-AG25", "1314-32-AG25", "1314-11-AG25", "1368-3-SE26", 
    "1314-3-CM26", "1153-51-AG25", "1324-16-TD25", "1314-47-CM25", 
    "1314-43-CM25", "1314-51-CM25", "1305-6-AG25", "618-469-CM25",
    "618-239-CM25", "4293-34-AG25", "1314-65-CM24", "1314-34-AG25", 
    "618-163-AG25", "1863-2-TD25"
]

# Sidebar
st.sidebar.header("Selección de Auditoría")
seleccion_oc = st.sidebar.selectbox("Seleccione una OC:", OC_LIST)


def consultar_oc(codigo_oc):
    url = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
    params = {"codigo": codigo_oc, "ticket": API_TICKET}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data["Listado"][0] if data.get("Listado") else None
        return None
    except:
        return None


# --- LÓGICA DE NAVEGACIÓN A ONEDRIVE ---
def generar_url_onedrive(nombre_carpeta):
    # Base ID de la carpeta contenedora (Descargas_OC)
    base_id = "/personal/ignacio_davila_corfo_cl/Documents/1- Auditorias/2026/Auditoria TOTAL/MercadoPublico/Descargas_OC"
    # ID de la vista (según tu link)
    view_id = "f25061d4-7cde-427a-8d37-f3ddda2360c6"
    
    # Construimos la ruta hacia la subcarpeta específica
    # Codificamos el nombre de la carpeta para evitar errores con caracteres especiales
    ruta_carpeta_especifica = f"{base_id}/{nombre_carpeta}"
    ruta_encoded = urllib.parse.quote(ruta_carpeta_especifica)
    
    # URL Final estructurada para SharePoint/OneDrive
    url_final = f"https://corfocl-my.sharepoint.com/my?id={ruta_encoded}&viewid={view_id}"
    return url_final

# --- RENDERIZADO ---
if seleccion_oc:
    with st.spinner('Cargando datos de la API...'):
        d = consultar_oc(seleccion_oc)
        
    if d:
        # Encabezado con Botón de OneDrive
        col_tit, col_btn = st.columns([3, 1])
        
        with col_tit:
            st.header(f"OC: {d.get('Codigo')}")
            st.subheader(d.get('Nombre', 'Sin nombre'))
            
        with col_btn:
            st.write("###") # Espaciador
            url_docs = generar_url_onedrive(seleccion_oc)
            st.link_button("📂 Ver datos adjuntos", url_docs, use_container_width=True, type="primary")

        # --- PESTAÑAS ---
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "📄 General", "🏢 Comprador", "🚚 Proveedor", "📦 Ítems", "📅 Fechas", "🛠 JSON"
        ])

        with t1:
            st.markdown("### Información de la Orden")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Descripción:**", d.get("Descripcion"))
                st.write("**Tipo de Despacho:**", d.get("TipoDespacho"))
                st.write("**Forma de Pago:**", d.get("FormaPago"))
            with c2:
                st.write("**Estado:**", d.get("Estado"))
                st.metric("Total Bruto", f"${d.get('Total', 0):,.0f}")

        with t2:
            comp = d.get("Comprador", {})
            st.markdown("### Datos del Organismo Comprador")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Organismo:**", comp.get("NombreOrganismo"))
                st.write("**RUT:**", comp.get("RutUnidad"))
            with col_b:
                st.write("**Contacto:**", comp.get("NombreContacto"))
                st.write("**Dirección:**", f"{comp.get('DireccionUnidad')}, {comp.get('ComunaUnidad')}")

        with t3:
            prov = d.get("Proveedor", {})
            st.markdown("### Datos del Proveedor")
            col_x, col_y = st.columns(2)
            with col_x:
                st.write("**Nombre:**", prov.get("NombreSucursal"))
                st.write("**RUT:**", prov.get("RutSucursal"))
            with col_y:
                st.write("**Ubicación:**", f"{prov.get('Direccion')}, {prov.get('Comuna')}")

        with t4:
            st.markdown("### Listado de Productos/Servicios")
            items = d.get("Items", {}).get("Listado", [])
            if items:
                df_items = pd.DataFrame(items)
                cols = ["CodigoProducto", "Producto", "Cantidad", "UnidadMedida", "PrecioNeto", "TotalLinea"]
                st.dataframe(df_items[[c for c in cols if c in df_items.columns]], use_container_width=True)
            else:
                st.info("No hay ítems registrados.")

        with t5:
            st.json(d.get("Fechas", {}))

        with t6:
            st.json(d)
    else:
        st.error("No se pudo obtener información de la API para esta OC.")