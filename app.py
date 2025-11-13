import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import base64

# ====================================================
# CONFIGURACIÓN INICIAL
# ====================================================
st.set_page_config(page_title="BAE - Monitor del Bebé", page_icon="🧸", layout="centered")

# ====================================================
# ESTILOS PASTEL BAE
# ====================================================
st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #FFF9E8 0%, #FFEBD3 100%);
    font-family: 'Poppins', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FFF9E8 0%, #FFEBD3 100%);
}
.block-container {
    background: white;
    border-radius: 25px;
    padding: 2rem 2rem 3rem 2rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
}
h1, h2, h3 {
    color: #604A3F;
    text-align: center;
}
.stButton>button {
    background: linear-gradient(90deg, #FFD5A5, #FBC4AB);
    color: #604A3F;
    border: none;
    border-radius: 50px;
    padding: 0.8rem 2rem;
    font-weight: 600;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(255, 213, 165, 0.6);
}
.status-box {
    border-radius: 15px;
    padding: 1.2rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 500;
    margin-top: 1rem;
    animation: fadeIn 1s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
.cold {
    background-color: #D6EAF8;
    color: #1B4F72;
}
.hot {
    background-color: #FADBD8;
    color: #641E16;
}
.good {
    background-color: #FCF3CF;
    color: #7D6608;
}
.metric-card {
    background: #FFF7ED;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    color: #604A3F;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ====================================================
# TÍTULO PRINCIPAL
# ====================================================
st.markdown("<h1>🧸 BAE - Monitor del Bebé</h1>", unsafe_allow_html=True)
st.markdown("<h3>Vigila el ambiente del bebé con ternura y tecnología pastel 💛</h3>", unsafe_allow_html=True)
st.divider()

# ====================================================
# VARIABLES DE SESIÓN
# ====================================================
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# ====================================================
# FUNCIÓN DE CONEXIÓN MQTT (HiveMQ WebSocket)
# ====================================================
def get_mqtt_message(broker, port, topic, client_id):
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
        client = mqtt.Client(client_id=client_id, transport="websockets")
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

# ====================================================
# CONFIGURACIÓN MQTT
# ====================================================
broker = "broker.hivemq.com"
port = 8000  # WebSocket port
topic = "sensor/temperatura"
client_id = "BAE_Monitor"

# ====================================================
# BOTÓN PARA OBTENER DATOS
# ====================================================
if st.button("🔄 Actualizar temperatura del bebé"):
    with st.spinner("Conectando al cuarto del bebé... 🍼"):
        sensor_data = get_mqtt_message(broker, port, topic, client_id)
        st.session_state.sensor_data = sensor_data

# ====================================================
# MOSTRAR RESULTADOS
# ====================================================
if st.session_state.sensor_data:
    st.divider()
    data = st.session_state.sensor_data

    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ No se pudo conectar al broker MQTT (WebSocket): {data['error']}")
    else:
        st.markdown("## 🌡️ Estado del Cuarto del Bebé")
        try:
            t = float(data.get("t", 0))
            h = float(data.get("h", 0))
        except:
            st.error("Error en el formato de datos recibidos.")
            st.stop()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-card">🌡️ Temperatura<br><span style="font-size:1.8rem;">{t:.1f} °C</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">💧 Humedad<br><span style="font-size:1.8rem;">{h:.1f} %</span></div>', unsafe_allow_html=True)

        # Estado térmico
        if t < 18:
            st.markdown('<div class="status-box cold">❄️ El bebé tiene frío. Asegúrate de abrigarlo bien 💙</div>', unsafe_allow_html=True)
        elif t > 28:
            st.markdown('<div class="status-box hot">☀️ El bebé tiene calor. Refresca el ambiente 💛</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box good">😊 El bebé está cómodo y feliz 🌼</div>', unsafe_allow_html=True)
else:
    st.info("Haz clic en el botón para obtener la temperatura actual del cuarto del bebé 🍼")

# ====================================================
# PIE DE PÁGINA
# ====================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #604A3F;'>
    <b>BAE Monitor</b> 🧸 | Cuidando con amor pastel 💛<br>
    Conectado a <i>HiveMQ MQTT WebSocket</i>
</div>
""", unsafe_allow_html=True)

