import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from PIL import Image
import base64
from gtts import gTTS
import io

# -----------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------
st.set_page_config(
    page_title="BAE - Monitor del Bebé",
    page_icon="🍼",
    layout="centered"
)

# -----------------------------
# ESTILOS PASTEL BAE
# -----------------------------
st.markdown("""
<style>
    body {
        background: linear-gradient(180deg, #FFF8EA 0%, #FFF2C3 100%);
    }
    .title-bae {
        font-size: 2.8rem;
        font-weight: 800;
        color: #DD8E6B;
        text-align: center;
        margin-bottom: 0.2rem;
        animation: fadeIn 2s ease;
    }
    .subtitle-bae {
        font-size: 1.2rem;
        text-align: center;
        color: #6E5849;
        margin-bottom: 1.5rem;
        opacity: 0.8;
    }
    .card {
        background: #FFF8EA;
        border-radius: 20px;
        box-shadow: 0px 4px 20px rgba(221, 142, 107, 0.2);
        padding: 2rem;
        text-align: center;
        animation: float 6s ease-in-out infinite;
    }
    .metric {
        font-size: 2.5rem;
        color: #6E5849;
        font-weight: 700;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    @keyframes float {
        0%, 100% {transform: translateY(0px);}
        50% {transform: translateY(-8px);}
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# ENCABEZADO
# -----------------------------
st.markdown('<div class="title-bae">🍼 BAE - Monitor del Bebé</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-bae">Supervisión ambiental inteligente y visual</div>', unsafe_allow_html=True)

# -----------------------------
# IMÁGENES DEL BEBÉ
# -----------------------------
bebe_frio = Image.open("bebeFrio.png")
bebe_calor = Image.open("bebeCalor.png")
bebe_feliz = Image.open("bebeFeliz.png")

# -----------------------------
# MQTT CONFIG
# -----------------------------
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

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(broker, 1883, 60)
    mqtt_client.subscribe(topic)
    mqtt_client.loop_start()
except Exception as e:
    st.error("❌ No se pudo conectar al broker MQTT (verifica conexión en Wokwi).")
    st.text(str(e))

# -----------------------------
# OBTENER DATOS DEL SENSOR
# -----------------------------
time.sleep(1)
data = st.session_state.mqtt_data
temp = data.get("t", 0)
hum = data.get("h", 0)

# -----------------------------
# LÓGICA DE ESTADO
# -----------------------------
if temp < 18:
    estado = "Hace frío ❄️"
    color = "#C6E2E3"
    img = bebe_frio
    audio_text = "El cuarto está frío, abriga al bebé."
elif temp > 28:
    estado = "Hace calor ☀️"
    color = "#DD8E6B"
    img = bebe_calor
    audio_text = "El cuarto está muy caliente, abre una ventana."
else:
    estado = "Temperatura estable 😊"
    color = "#A3C9A8"
    img = bebe_feliz
    audio_text = "El cuarto está perfecto, el bebé está cómodo."

# -----------------------------
# TARJETA DE DATOS
# -----------------------------
st.markdown(f"""
    <div class="card" style="border-top: 8px solid {color};">
        <img src="data:image/png;base64,{base64.b64encode(open(img.filename, "rb").read()).decode()}" width="200">
        <p class="metric">{temp:.1f} °C</p>
        <p style="font-size:1.3rem; color:{color}; font-weight:600;">{estado}</p>
        <p style="color:#6E5849;">Humedad: {hum:.1f}%</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------
# AUDIO DE VOZ
# -----------------------------
if st.button("🔊 Escuchar estado"):
    tts = gTTS(audio_text, lang="es")
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/mp3")

# -----------------------------
# INTERACCIÓN POR VOZ (BETA)
# -----------------------------
st.markdown("### 🎤 Prueba de comando de voz")
st.info("Di: *enciende la luz* o *qué temperatura hay* (requiere micrófono local o simulación)")

# Aquí podrías integrar `speech_recognition` o un módulo web JS si lo usas localmente
# En Streamlit Cloud, no se puede acceder directamente al micrófono.

st.markdown("---")
st.caption("👶 Proyecto BAE — Supervisión ambiental inteligente con MQTT y Streamlit 💛")


