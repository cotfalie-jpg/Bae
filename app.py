import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# -------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -------------------------------
st.set_page_config(
    page_title="👶 BAE - Lector de Sensor MQTT",
    page_icon="👶",
    layout="centered"
)

# -------------------------------
# ESTILO VISUAL - BAE
# -------------------------------
st.markdown("""
<style>
/* Fondo general con tonos BAE */
.stApp {
    background: linear-gradient(135deg, #FFF6E9, #FFEBD2, #FFF9E5);
    font-family: 'Poppins', sans-serif;
}

/* Títulos principales */
h1 {
    color: #5C4438;
    text-align: center;
    font-weight: 700;
    font-size: 2.5rem;
}

/* Subtítulos y texto */
h2, h3, h4, p, label, span, div {
    color: #7A5E48 !important;
}

/* Botón principal */
button[kind="primary"] {
    background-color: #F9C784 !important;
    color: #5C4438 !important;
    font-weight: 600;
    border-radius: 15px !important;
    border: none;
}
button[kind="primary"]:hover {
    background-color: #F7B267 !important;
}

/* Tarjetas */
[data-testid="stMetricValue"] {
    color: #5C4438 !important;
    font-weight: bold;
    font-size: 1.6rem !important;
}
[data-testid="stMetricLabel"] {
    color: #9B7050 !important;
    font-weight: 500;
}

/* Expander y cajas */
.streamlit-expanderHeader {
    background-color: #FFF0D9 !important;
    color: #5C4438 !important;
    border-radius: 10px !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# VARIABLES DE ESTADO
# -------------------------------
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# SIDEBAR - CONFIGURACIÓN
# -------------------------------
with st.sidebar:
    st.image("logo_bae.png", width=150)
    st.markdown("### ⚙️ Configuración de Conexión")
    
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com', 
                           help='Dirección del broker MQTT')
    
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535,
                           help='Puerto del broker (generalmente 1883)')
    
    topic = st.text_input('Tópico', value='bae',
                          help='Tópico MQTT a suscribirse')
    
    client_id = st.text_input('ID del Cliente', value='baeapp',
                              help='Identificador único para esta conexión')

# -------------------------------
# TÍTULO PRINCIPAL
# -------------------------------
st.markdown("<h1>👶 BAE - Monitor Ambiental</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#A67856;'>Supervisión de temperatura y humedad en tiempo real</p>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# BOTÓN PARA OBTENER DATOS
# -------------------------------
if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('Conectando al broker y esperando datos...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# -------------------------------
# MOSTRAR RESULTADOS
# -------------------------------
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Datos Recibidos')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente')
        
        if isinstance(data, dict):
            # Mostrar temperatura y humedad con estilo BAE
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key.capitalize(), value=f"{value} {'°C' if key.startswith('t') else '%'}")
            
            with st.expander('📋 Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)

# -------------------------------
# PIE DE PÁGINA
# -------------------------------
st.markdown("<br><p style='text-align:center;color:#8B6B4E;'>💛 Proyecto BAE - Interfaces Multimodales 2025</p>", unsafe_allow_html=True)


