import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import tempfile
import sounddevice as sd
import wavio
from gtts import gTTS
from openai import OpenAI

# =======================
# CONFIGURACIÓN DE PÁGINA
# =======================
st.set_page_config(
    page_title="BAE - Cuarto del Bebé 💡🐻",
    page_icon="🌼",
    layout="centered"
)

# =======================
# ESTILO VISUAL PASTEL
# =======================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #fff9e6, #fdf3e7, #e8f8f5);
    font-family: "Poppins", sans-serif;
}
h1 {
    text-align: center;
    background: linear-gradient(90deg, #ffd54f, #ffcc80, #ffe082);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
    font-size: 1.2rem;
}
.mic-button {
    background: linear-gradient(145deg, #fff59d, #ffe082);
    color: #444;
    border: none;
    border-radius: 50%;
    width: 120px;
    height: 120px;
    font-size: 3rem;
    margin: 1.5rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
}
.mic-button:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 35px rgba(255, 235, 59, 0.3);
}
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
.card {
    background: #ffffff;
    border: 2px solid #ffe082;
    border-radius: 20px;
    padding: 1.5rem;
    margin-top: 1rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    text-align: center;
    animation: fadeInUp 1s ease;
}
@keyframes fadeInUp {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# =======================
# ENCABEZADO
# =======================
st.markdown("<h1>🌼 BAE - Cuarto del Bebé</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Controla la luz y conoce el clima del bebé con tu voz 💛</div>', unsafe_allow_html=True)

# =======================
# MQTT CONFIG
# =======================
broker = "test.mosquitto.org"
topic_sensor = "sensor/temperatura"
topic_luz = "cuarto/luz"
last_data = {"t": None, "h": None}

def on_message(client, userdata, message):
    global last_data
    try:
        payload = json.loads(message.payload.decode())
        last_data = payload
    except:
        pass

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(broker, 1883, 60)
mqtt_client.subscribe(topic_sensor)
mqtt_client.loop_start()

# =======================
# CONFIGURAR OPENAI
# =======================
api_key = st.text_input("🔑 Clave de OpenAI:", type="password")
if not api_key:
    st.warning("Ingresa tu clave de OpenAI para usar la voz.")
    st.stop()
client = OpenAI(api_key=api_key)

# =======================
# GRABACIÓN DE VOZ
# =======================
duration = 4
fs = 44100
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)

if st.button("🎤 Hablar con BAE"):
    st.info("🎙️ Grabando 4 segundos...")
    rec = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wavio.write(temp_wav.name, rec, fs, sampwidth=2)

    with st.spinner("🎧 Escuchando..."):
        audio_file = open(temp_wav.name, "rb")
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
        user_text = transcript.text.strip()
        st.success(f"🗣️ Dijiste: {user_text}")

        # =======================
        # INTERPRETAR COMANDO
        # =======================
        if "luz" in user_text.lower() and "enciende" in user_text.lower():
            mqtt_client.publish(topic_luz, json.dumps({"estado": "encendida"}))
            answer = "Encendiendo la luz del cuarto del bebé 💡✨"
        elif "luz" in user_text.lower() and "apaga" in user_text.lower():
            mqtt_client.publish(topic_luz, json.dumps({"estado": "apagada"}))
            answer = "Apagando la luz del bebé 🌙"
        elif "temperatura" in user_text.lower() or "clima" in user_text.lower():
            t = last_data.get("t")
            if t is None:
                answer = "No logro leer la temperatura aún, inténtalo de nuevo en un momento 🌼"
            elif t < 18:
                answer = f"La habitación está fría, unos {t:.1f} grados ❄️. Vamos a abrigar al bebé 🧣"
            elif t > 28:
                answer = f"Está calientita la habitación, unos {t:.1f} grados ☀️. Cuidemos que no tenga calor."
            else:
                answer = f"La temperatura es perfecta, unos {t:.1f} grados 🌤️. El bebé está cómodo 💛"
        else:
            answer = "No entendí muy bien, ¿puedes repetirlo con calma, por favor? 💬"

        # Respuesta hablada
        tts = gTTS(answer, lang="es")
        tts.save("respuesta.mp3")

        st.markdown(f'<div class="card">{answer}</div>', unsafe_allow_html=True)
        st.audio("respuesta.mp3")

st.markdown('</div>', unsafe_allow_html=True)

# =======================
# VISUALIZACIÓN SENSOR
# =======================
st.markdown("### 🌡️ Estado del cuarto del bebé")
if last_data["t"] is not None:
    t = last_data["t"]
    h = last_data["h"]

    col1, col2 = st.columns(2)
    col1.metric("Temperatura", f"{t:.1f} °C")
    col2.metric("Humedad", f"{h:.1f} %")

    if t < 18:
        st.image("https://i.imgur.com/YxA4HqL.png", caption="🥶 Bebé con frío")
    elif t > 28:
        st.image("https://i.imgur.com/ZsNw0q2.png", caption="🥵 Bebé con calor")
    else:
        st.image("https://i.imgur.com/8bFkCe3.png", caption="😊 Bebé feliz")
else:
    st.info("Esperando datos del sensor Wokwi...")

# =======================
# PIE
# =======================
st.markdown("""
<hr style="border:1px solid #ffe082;">
<div style="text-align:center; color:#888;">
🌸 BAE - Cuarto del Bebé | Luz, voz y clima inteligente 💛
</div>
""", unsafe_allow_html=True)

