import streamlit as st
import paho.mqtt.client as mqtt
import json
import os
import pathlib

# -------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -------------------------------
st.set_page_config(page_title="BAE - Monitor del Bebé", page_icon="👶", layout="centered")

# Directorio base (para imágenes locales)
BASE_DIR = pathlib.Path(__file__).parent.resolve()

# -------------------------------
# ESTILO VISUAL PASTEL BAE
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #FFF7E6, #FFEED9, #FFF9F1);
    font-family: 'Poppins', sans-serif;
}
h1 {
    color: #5C4438;
    text-align: center;
    font-size: 2.6rem;
    margin-bottom: 0.3rem;
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
    padding: 2.5rem;
    text-align: center;
    box-shadow: 0px 6px 20px rgba(180,150,120,0.25);
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
.footer {
    text-align: center;
    color: #8B6B4E;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>👶 BAE - Monitor del Bebé</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Supervisión ambiental inteligente y visual</p>", unsafe_allow_html=True)

# -------------------------------
# VARIABLES DE ESTADO
# -------------------------------
BROKER = "broker.hivemq.com"
PORT = 8000  # puerto WebSocket
TOPIC = "sensor/temperatura"

if 'temp' not in st.session_state:
    st.session_state.temp = 0.0
if 'hum' not in st.session_state:
    st.session_state.hum = 0.0
if 'estado' not in st.session_state:
    st.session_state.estado = "Esperando datos..."
if 'conectado' not in st.session_state:
    st.session_state.conectado = False

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
        st.session_state.temp = data.get("t", 0.0)
        st.session_state.hum = data.get("h", 0.0)
    except Exception as e:
        print("Error al procesar mensaje:", e)

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

# Selección de color e imagen según temperatura
if temp < 18:
    estado = "🥶 El cuarto está demasiado frío"
    color = "#D4ECFF"
    img_name = "bebeFrio.png"
elif temp > 28:
    estado = "🥵 El cuarto está demasiado caliente"
    color = "#FFE0B3"
    img_name = "bebeCalor.png"
else:
    estado = "😊 Temperatura estable"
    color = "#E6FFD9"
    img_name = "bebeFeliz.png"

# Ruta de imagen local
img_path = BASE_DIR / img_name
if os.path.exists(img_path):
    img_display = str(img_path)
else:
    st.warning(f"⚠️ No se encontró la imagen: {img_name}")
    img_display = None

# -------------------------------
# TARJETA PRINCIPAL
# -------------------------------
st.markdown(f"<div class='card' style='background:{color};'>", unsafe_allow_html=True)
if img_display:
    st.image(img_display, width=230)
st.markdown(f"""
<h2 style="color:#5C4438;">{temp:.1f} °C</h2>
<p style="font-size:1.2rem; color:#5C4438;">Humedad: {hum:.1f}%</p>
<p style="font-weight:600; color:#5C4438;">{estado}</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# PIE DE PÁGINA
# -------------------------------
st.markdown("<p class='footer'>💛 Proyecto BAE - Interfaces Multimodales 2025</p>", unsafe_allow_html=True)

