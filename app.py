import streamlit as st
import json
import paho.mqtt.client as mqtt
from gtts import gTTS
from openai import OpenAI
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import tempfile

# ===============================
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# ===============================
st.set_page_config(page_title="BAE - Cuarto del Bebé 💛", layout="centered", page_icon="🍼")

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #fff7cc, #ffe8d6, #e7f6f2);
    font-family: 'Poppins', sans-serif;
}
h1 {
    text-align: center;
    background: linear-gradient(90deg, #ffd54f, #ffcc80, #ffe082);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    margin-bottom: 0.2rem;
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

# ===============================
# ENCABEZADO
# ===============================
st.markdown("<h1>🍼 BAE - Cuarto del Bebé</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Habla con BAE, controla la luz y conoce el clima del bebé 💛</div>', unsafe_allow_html=True)

# ===============================
# MQTT CONFIGURACIÓN
# ===============================
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

# ===============================
# API KEY
# ===============================
api_key = st.text_input("🔑 Clave de OpenAI:", type="password")
if not api_key:
    st.warning("Por favor ingresa tu clave de OpenAI para usar BAE 🌼")
    st.stop()
client = OpenAI(api_key=api_key)

# ===============================
# BOTÓN DE VOZ (micrófono navegador)
# ===============================
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)

stt_button = Button(label="🎤 Hablar con BAE", width=300, height=60)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'es-ES';
    recognition.onresult = function (e) {
        var text = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=70,
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# PROCESAR COMANDO DE VOZ
# ===============================
if result and "GET_TEXT" in result:
    user_text = result["GET_TEXT"]
    st.markdown(f"### 🗣️ Dijiste: *{user_text}*")

    # Interpretar el comando
    if "enciende" in user_text.lower() and "luz" in user_text.lower():
        mqtt_client.publish(topic_luz, json.dumps({"estado": "encendida"}))
        answer = "Encendiendo la luz del cuarto del bebé 💡✨"
    elif "apaga" in user_text.lower() and "luz" in user_text.lower():
        mqtt_client.publish(topic_luz, json.dumps({"estado": "apagada"}))
        answer = "Apagando la luz del bebé 🌙"
    elif "temperatura" in user_text.lower() or "clima" in user_text.lower():
        t = last_data.get("t")
        if t is None:
            answer = "Aún no recibo datos del sensor, inténtalo otra vez en unos segundos 💛"
        elif t < 18:
            answer = f"El cuarto está fresquito, unos {t:.1f} grados ❄️"
        elif t > 28:
            answer = f"Está calientito, unos {t:.1f} grados ☀️"
        else:
            answer = f"Perfecto, el bebé está cómodo con {t:.1f} grados 🌼"
    else:
        answer = "No entendí muy bien, ¿puedes repetirlo con calma por favor? 💬"

    # Generar respuesta con voz
    tts = gTTS(answer, lang="es")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)

    st.markdown(f'<div class="card">{answer}</div>', unsafe_allow_html=True)
    st.audio(temp_file.name)

# ===============================
# VISUALIZACIÓN DEL SENSOR
# ===============================
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
    st.info("Esperando datos del sensor desde Wokwi...")

st.markdown("""
<hr style="border:1px solid #ffe082;">
<div style="text-align:center; color:#888;">
🌸 BAE - Luz, voz y clima del bebé 🍼💛
</div>
""", unsafe_allow_html=True)
