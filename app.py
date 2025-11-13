import streamlit as st
import paho.mqtt.client as mqtt
import json

# -------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -------------------------------
st.set_page_config(page_title="BAE - Monitor del Bebé", page_icon="👶", layout="centered")

# -------------------------------
# ESTILO VISUAL PASTEL BAE
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #FFF9E6, #FFEFD5, #FDF5EC);
    font-family: 'Poppins', sans-serif;
}
h1 {
    color: #5C4438;
    text-align: center;
    font-size: 2.5rem;
}
.sub {
    text-align: center;
    color: #A67856;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}
.card {
    background-color: white;
    border-radius: 25px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(180,150,120,0.25);
    transition: all 0.3s ease;
}
.card:hover {
    transform: scale(1.02);
}
.baby {
    border-radius: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0% { transform: translatey(0px); }
    50% { transform: translatey(-8px); }
    100% { transform: translatey(0px); }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>👶 BAE - Monitor del Bebé</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Supervisión ambiental inteligente y visual</p>", unsafe_allow_html=True)

# -------------------------------
# VARIABLES DE ESTADO
# -------------------------------
BROKER = "broker.hivemq.com"
PORT = 8000
TOPIC = "sensor/temperatura"

if 'temp' not in st.session_state:
    st.session_state.temp = 0.0
if 'hum' not in st.session_state:
    st.session_state.hum = 0.0
if 'estado' not in st.session_state:
    st.session_state.estado = "Esperando datos..."

# -------------------------------
# CALLBACKS MQTT
# -------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.conectado = True
    else:
        st.session_state.conectado = False

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        st.session_state.temp = data["t"]
        st.session_state.hum = data["h"]
    except:
        pass

# -------------------------------
# CONEXIÓN MQTT
# -------------------------------
try:
    mqtt_client = mqtt.Client(transport="websockets")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.subscribe(TOPIC)
    mqtt_client.loop_start()
except Exception as e:
    st.error(f"❌ No se pudo conectar al broker MQTT (WebSocket).<br>{e}", unsafe_allow_html=True)

# -------------------------------
# VISUALIZACIÓN
# -------------------------------
temp = st.session_state.temp
hum = st.session_state.hum

if temp < 18:
    estado = "🥶 El cuarto está demasiado frío"
    color = "#D4ECFF"
    img = "bebeFrio.png"
elif temp > 28:
    estado = "🥵 El cuarto está demasiado caliente"
    color = "#FFE0B3"
    img = "bebeCalor.png"
else:
    estado = "😊 Temperatura estable"
    color = "#E6FFD9"
    img = "bebeFeliz.png"

st.markdown(f"""
<div class="card" style="background:{color};">
    <img src="{img}" class="baby" width="230">
    <h2 style="color:#5C4438;">{temp:.1f} °C</h2>
    <p style="font-size:1.2rem;">Humedad: {hum:.1f}%</p>
    <p style="font-weight:600;">{estado}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center;color:#8B6B4E;'>💛 Proyecto BAE - Interfaces Multimodales 2025</p>", unsafe_allow_html=True)
