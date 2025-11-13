import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import base64
from PIL import Image

# =============================
# CONFIGURACIÓN
# =============================
st.set_page_config(page_title="BAE - Baby Monitor", page_icon="👶", layout="centered")

# Paleta de colores pastel
COLOR_FONDO = "#FFF8E7"
COLOR_DURAZNO = "#FFD7B5"
COLOR_AZUL = "#CDE5FF"
COLOR_VERDE = "#C8E4D8"
COLOR_TEXTO = "#4D797A"

# =============================
# ESTILOS VISUALES
# =============================
st.markdown(f"""
<style>
    body {{
        background-color: {COLOR_FONDO};
        font-family: 'Poppins', sans-serif;
    }}
    .header {{
        text-align: center;
        color: {COLOR_TEXTO};
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        animation: fadeIn 1.5s ease;
    }}
    .status-box {{
        background: linear-gradient(145deg, {COLOR_VERDE}, {COLOR_AZUL});
        border-radius: 25px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        animation: floaty 3s ease-in-out infinite;
    }}
    .temp {{
        font-size: 3rem;
        font-weight: 700;
        color: {COLOR_TEXTO};
    }}
    .estado {{
        font-size: 1.3rem;
        color: {COLOR_TEXTO};
        margin-top: 10px;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes floaty {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-6px); }}
        100% {{ transform: translateY(0px); }}
    }}
</style>
""", unsafe_allow_html=True)

# =============================
# ENCABEZADO
# =============================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo_bae.png", width=70)
with col2:
    st.markdown("<div class='header'>BAE - Monitor del Bebé</div>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#777;'>Supervisión ambiental inteligente con colores pastel 💛</p>", unsafe_allow_html=True)

# =============================
# MQTT CONFIG
# =============================
broker = "test.mosquitto.org"
topic = "sensor/temperatura"

if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = {"t": 0, "h": 0}

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        st.session_state.mqtt_data = payload
    except:
        pass

mqtt_client = mqtt.Client(transport="websockets")
mqtt_client.on_message = on_message

try:
    mqtt_client.ws_set_options(path="/mqtt")
    mqtt_client.connect(broker, 8081, 60)
    mqtt_client.subscribe(topic)
    mqtt_client.loop_start()
except Exception as e:
    st.error("❌ No se pudo conectar al broker MQTT (WebSocket).")
    st.text(str(e))

# =============================
# FUNCIÓN AUDIO BASE64
# =============================
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    base64_audio = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay>
        <source src="data:audio/wav;base64,{base64_audio}" type="audio/wav">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# =============================
# INTERFAZ PRINCIPAL
# =============================
placeholder = st.empty()

while True:
    data = st.session_state.mqtt_data
    temp = data.get("t", 0)
    hum = data.get("h", 0)

    # Determinar estado
    if temp < 18:
        estado = "El cuarto está muy frío ❄️"
        color = COLOR_AZUL
        img = "bebeFrio.png"
        sound = "frio.wav"
    elif temp > 28:
        estado = "El cuarto está muy caliente ☀️"
        color = COLOR_DURAZNO
        img = "bebeCalor.png"
        sound = "calor.wav"
    else:
        estado = "El ambiente está perfecto 🌤️"
        color = COLOR_VERDE
        img = "bebeFeliz.png"
        sound = "estable.wav"

    with placeholder.container():
        st.markdown(f"""
        <div class="status-box" style="background:linear-gradient(145deg, {color}, {COLOR_FONDO});">
            <img src="{img}" width="250" style="border-radius:20px; margin-bottom:10px;">
            <div class="temp">{temp:.1f} °C</div>
            <div class="estado">{estado}</div>
            <p style="color:#777; font-size:1rem;">Humedad: {hum:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        autoplay_audio(sound)
        time.sleep(6)

