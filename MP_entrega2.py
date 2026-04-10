import streamlit as st
import requests
import pandas as pd
import urllib.parse
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title="Visor Auditoría Mercado Público 2026", layout="wide")

st.title("📊 Detalle de Orden de Compra")
st.markdown("Integración API Mercado Público + Respaldo OneDrive")

# --- CONFIGURACIÓN ---


API_TICKET = st.secrets["MP_TICKET"]

OC_LIST = [
    "1394164-4-TD24","1314-91-TD24","1383017-39-AG24","1394164-2-SE24","1314-66-CM24","1314-68-SE24","618-616-CM24","1377-31-SE24","1314-58-CM24","1308-6-SE24","1368-101-CM24","1863-6-AG24","1153-55-AG24","618-527-SE24","1314-51-SE24","1368-41-SE24","1368-47-SE24","1153-36-AG24","618-340-SE24","1866-10-SE24","1368-32-SE24","1335-4-SE24","1368-34-CC24","1863-1-SE24","618-237-SE24","1864-4-SE24","1308-2-SE24","1314-7-CC24","1377-1-SE24","4293-3-SE24","1377-3-LQ24","1308-1-LQ23","1368-2-LQ24","1368-3-LP24","1866-1-LP24","1368-1-LP24","1335-2-LQ24","1308-2-LQ22","618-6-LR23","618-6-LR23"
]

# Sidebar
st.sidebar.header("Selección de Auditoría")
seleccion_oc = st.sidebar.selectbox("Seleccione una OC:", OC_LIST)

def consultar_oc(codigo_oc):
    url = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
    params = {"codigo": codigo_oc, "ticket": API_TICKET}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["Listado"][0] if data.get("Listado") else None
        return None
    except:
        return None

def generar_url_onedrive(nombre_carpeta):
    base_id = "/personal/ignacio_davila_corfo_cl/Documents/1- Auditorias/2026/Auditoria TOTAL/MercadoPublico/Descargas_OC"
    view_id = "f25061d4-7cde-427a-8d37-f3ddda2360c6"
    ruta_carpeta_especifica = f"{base_id}/{nombre_carpeta}"
    ruta_encoded = urllib.parse.quote(ruta_carpeta_especifica)
    url_final = f"https://corfocl-my.sharepoint.com/my?id={ruta_encoded}&viewid={view_id}"
    return url_final

# --- BOTÓN DE COPIAR CON ALINEACIÓN ABSOLUTA ---
def boton_copiar_perfecto(texto):
    html_code = f"""
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; height: 55px; position: relative; }}
        #copyBtn {{
            position: absolute;
            bottom: 0;
            left: 0;
            background-color: #f0f2f6; 
            color: #31333F; 
            padding: 0 16px; 
            border: 1px solid rgba(49, 51, 63, 0.2); 
            border-radius: 4px; 
            cursor: pointer; 
            width: 100%;
            height: 38px;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Source Sans Pro', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        #copyBtn:hover {{ background-color: #e0e2e6; border-color: #31333F; }}
        #confirmMsg {{
            position: absolute;
            bottom: 40px;
            width: 100%;
            text-align: center;
            visibility: hidden; 
            color: #09ab3b; 
            font-size: 11px; 
            font-weight: bold;
            font-family: sans-serif;
        }}
    </style>
    <div id="confirmMsg">✓ OC copiada</div>
    <button id="copyBtn" onclick="copyToClipboard()">📋 Copiar OC</button>
    
    <script>
    function copyToClipboard() {{
        const text = '{texto}';
        navigator.clipboard.writeText(text).then(() => {{
            const msg = document.getElementById('confirmMsg');
            msg.style.visibility = 'visible';
            setTimeout(() => {{ msg.style.visibility = 'hidden'; }}, 2000);
        }});
    }}
    </script>
    """
    components.html(html_code, height=55)

# --- RENDERIZADO ---
if seleccion_oc:
    with st.spinner('Cargando datos...'):
        d = consultar_oc(seleccion_oc)
        
    if d:
        # Alineación vertical al fondo (bottom) para que todos toquen la misma línea base
        col_tit, col_copy, col_web, col_docs = st.columns([1.6, 0.7, 0.7, 1], vertical_alignment="bottom")
        
        with col_tit:
            st.header(f"OC: {d.get('Codigo')}")
            st.subheader(d.get('Nombre', 'Sin nombre'))
            
        with col_copy:
            boton_copiar_perfecto(seleccion_oc)

        with col_web:
            url_web = f"https://www.mercadopublico.cl/Portal/Modules/Site/Busquedas/BuscadorAvanzado.aspx?qs=2&txtSearch={seleccion_oc}"
            st.link_button("🌐 Ver en web", url_web, use_container_width=True)

        with col_docs:
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

        # ... (Resto de pestañas)
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