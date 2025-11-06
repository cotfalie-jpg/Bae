# app.py
import os
import time
import json
import random
import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image
from gtts import gTTS
import paho.mqtt.client as mqtt
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models.widgets import Button
from bokeh.models import CustomJS

# ---------------------------
# Config y estilos BAE
# ---------------------------
st.set_page_config(page_title="BAE Sense", page_icon="👶", layout="wide")
CSS = f"""
<style>
:root {{
  --bae-peach: #{ 'DD8E6B' };
  --bae-cream: #{ 'FFF8EA' };
  --bae-yellow: #{ 'FFF2C3' };
  --bae-aqua: #{ 'C6E2E3' };
  --bae-dark: #37504F;
}}

body {{ background: linear-gradient(180deg, var(--bae-cream) 0%, #fffaf5 100%); font-family: 'Poppins', sans-serif; }}
.stApp .block-container{{ padding:2rem 3rem 3rem 3rem; }}

.header {{
  display:flex; align-items:center; gap:16px; margin-bottom:18px;
}}
.logo {{
  width:72px; height:72px; border-radius:14px; padding:6px; background: linear-gradient(135deg, var(--bae-cream), var(--bae-yellow));
  box-shadow: 0 6px 18px rgba(221,142,107,0.12);
}}
.h1 {{
  font-size:2.4rem; color:var(--bae-dark); margin:0; font-weight:800;
}}
.h2 {{ color:var(--bae-peach); margin-top:0.2rem; margin-bottom:12px; font-weight:600; }}

.card {{
  background: white;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  border-left: 8px solid var(--bae-peach);
}}

.small-card {{
  background: white;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 6px 14px rgba(0,0,0,0.04);
}}

.btn-bae {{
  background: linear-gradient(90deg, var(--bae-aqua), var(--bae-yellow));
  color: var(--bae-dark);
  border: none;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight:700;
}}

.fade-in {{
  animation: fadeIn 0.6s ease-in-out;
}}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.metric-label {{ color:#7d7d7d; font-size:0.85rem; }}
.metric-value {{ font-size:1.5rem; font-weight:700; color:var(--bae-dark); }}

.sidebar .sidebar-content {{ background: linear-gradient(180deg, var(--bae-yellow), #fff7df) !important; border-radius:12px; padding:16px; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------
# Helpers
# ---------------------------
ASSETS = Path("assets")
ASSETS.mkdir(exist_ok=True)

def play_audio_and_return_bytes(text, lang="es", filename=None):
    if not filename:
        filename = f"temp_audio_{int(time.time())}.mp3"
    tmp_path = ASSETS / filename
    tts = gTTS(text, lang=lang)
    tts.save(str(tmp_path))
    with open(tmp_path, "rb") as f:
        data = f.read()
    return data

def simulate_sensor_reading():
    """Simula datos ambientales y signos del bebé"""
    temp = round(random.uniform(19.0, 30.0), 1)        # °C
    humidity = round(random.uniform(30.0, 70.0), 1)    # %
    motion = random.choice([False, False, False, True]) # movimiento
    cry = random.choice([False, False, True])          # llanto detectado
    ts = int(time.time())
    return {"temp": temp, "humidity": humidity, "motion": motion, "cry": cry, "ts": ts}

# MQTT read with timeout
def read_mqtt_once(broker, port, topic, timeout_s=3):
    result = {"ok": False, "payload": None}
    def on_message(client, userdata, message):
        try:
            result["payload"] = json.loads(message.payload.decode())
        except:
            result["payload"] = message.payload.decode()
        result["ok"] = True

    client = mqtt.Client()
    client.on_message = on_message
    try:
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        start = time.time()
        while time.time() - start < timeout_s and not result["ok"]:
            time.sleep(0.1)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        result["payload"] = {"error": str(e)}
    return result

# ---------------------------
# App header
# ---------------------------
col1, col2 = st.columns([1,6])
with col1:
    logo_path = ASSETS / "logo_bae.png"
    if logo_path.exists():
        img = Image.open(logo_path).convert("RGBA")
        st.markdown(f'<div class="logo"><img src="data:image/png;base64,{img_to_b64(img)}" style="width:100%;height:100%;object-fit:contain;border-radius:10px;"/></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo" ></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="header"><div><h1 class="h1">Portafolio BAE</h1><div class="h2">Aplicaciones para el cuidado y desarrollo de tu bebé</div></div></div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Sidebar: configuración (MQTT, navegación)
# ---------------------------
st.sidebar.markdown("### 🔧 Conexión y configuración")
use_mqtt = st.sidebar.checkbox("Usar MQTT (si no, se simula)", value=False)
broker = st.sidebar.text_input("Broker MQTT", value="broker.hivemq.com")
port = st.sidebar.number_input("Puerto MQTT", value=1883)
topic = st.sidebar.text_input("Tópico MQTT", value="bae/sensors/esp32")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Acciones")
page = st.sidebar.radio("Navegar a", ["Voice & Monitor", "Sensor Panel", "Cuentos / Audio"])

# ---------------------------
# Voice widget JS helper (SpeechRecognition)
# ---------------------------
VOICE_JS = """
var recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'es-ES';
recognition.onresult = function(e) {
    var value = e.results[0][0].transcript;
    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
};
recognition.start();
"""

# small helper to embed image to base64 (for inline logo)
def img_to_b64(img: Image.Image):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ---------------------------
# PAGE: Voice & Monitor
# ---------------------------
if page == "Voice & Monitor":
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("### 🎤 Voice & Monitor")
    st.write("Usa tu voz (botón) o escribe un comando. Comandos de ejemplo: `¿Cuál es la temperatura?`, `Reproducir cuento`, `Estado del bebé`.")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2,3])
    with col1:
        st.markdown('<div class="small-card">', unsafe_allow_html=True)
        st.markdown("**Entrada por texto**")
        text_cmd = st.text_input("Escribe un comando", value="", key="cmd_text")
        if st.button("Enviar comando"):
            cmd = text_cmd.strip().lower()
            st.info(f"Comando: {cmd}")
            st.session_state.last_cmd = cmd
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>')
        st.markdown('<div class="small-card">', unsafe_allow_html=True)
        st.markdown("**Entrada por voz**")
        st.markdown("Pulsa el botón y concede permiso al micrófono del navegador.")
        # Bokeh button that triggers browser Speech API (via CustomJS)
        b = Button(label="🎙️ Hablar", width=220, height=50)
        b.js_on_event("button_click", CustomJS(code=VOICE_JS))
        result = streamlit_bokeh_events(
            b,
            events="GET_TEXT",
            key="listen",
            refresh_on_update=False,
            debounce_time=0
        )
        if result and "GET_TEXT" in result:
            voice_text = result.get("GET_TEXT")
            st.success(f"Reconocido: {voice_text}")
            st.session_state.last_cmd = voice_text

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Estado actual del entorno**")
        # read sensor (mqtt or simulated)
        if use_mqtt:
            r = read_mqtt_once(broker, int(port), topic, timeout_s=2)
            if not r["ok"]:
                st.warning("No se recibió mensaje MQTT en el tiempo dado — usando datos simulados.")
                sensor = simulate_sensor_reading()
            else:
                sensor = r["payload"]
        else:
            sensor = simulate_sensor_reading()

        # Present metrics
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            st.markdown('<div class="metric-label">Temperatura</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{sensor.get("temp", "—")} °C</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-label">Humedad</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{sensor.get("humidity", "—")} %</div>', unsafe_allow_html=True)
        with c3:
            motion = sensor.get("motion", False)
            cry = sensor.get("cry", False)
            status = "Movimiento" if motion else ("Llanto" if cry else "Tranquilo")
            st.markdown('<div class="metric-label">Estado</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{status}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.write("Acciones rápidas")
        cola, colb = st.columns([2,1])
        if cola.button("Reproducir canción de cuna"):
            audio_bytes = play_audio_and_return_bytes("Shh... este es un cuento para arrullar al bebé. Dulces sueños.", lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        if colb.button("Sondear sensor ahora"):
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # handle last command if exists
    if "last_cmd" in st.session_state and st.session_state.last_cmd:
        cmd = st.session_state.last_cmd.lower()
        if "temperatura" in cmd or "temp" in cmd:
            st.success(f"La temperatura actual es {sensor.get('temp')} °C")
        elif "huevo" in cmd or "cuento" in cmd or "cuna" in cmd or "reproducir" in cmd:
            st.info("Reproduciendo cuento...")
            audio_bytes = play_audio_and_return_bytes("Había una vez un osito que aprendió a dormir escuchando el viento...", lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.info("Comando recibido: " + cmd)

# ---------------------------
# PAGE: Sensor Panel (visual)
# ---------------------------
elif page == "Sensor Panel":
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("### 📊 Sensor Panel")
    st.markdown("Panel visual con controles y visualizaciones. Click en los botones para simular acciones.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Read (or simulate) sensor
    if use_mqtt:
        r = read_mqtt_once(broker, int(port), topic, timeout_s=2)
        sensor = r["payload"] if r["ok"] else simulate_sensor_reading()
    else:
        sensor = simulate_sensor_reading()

    left, right = st.columns([2,1])
    with left:
        st.markdown('<div class="small-card">', unsafe_allow_html=True)
        st.markdown("**Indicadores**")
        st.progress(min(max((sensor.get("temp", 20) - 15) / 20, 0), 1), text="Temperatura relativa")
        st.write(f"Temperatura: **{sensor.get('temp')} °C**")
        st.write(f"Humedad: **{sensor.get('humidity')} %**")
        st.write("Movimiento:" , "✅" if sensor.get("motion") else "—")
        st.write("Llanto:", "🔊" if sensor.get("cry") else "—")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>')
        st.markdown('<div class="small-card">', unsafe_allow_html=True)
        if st.button("Encender luz suave"):
            st.success("Luz encendida (simulado)")
        if st.button("Activar modo descanso"):
            st.success("Modo descanso activado (ruidos blancos)")
            audio_bytes = play_audio_and_return_bytes("Sonidos suaves de lluvia para ayudar al descanso.", lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Control rápido**")
        st.button("Refrescar datos", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# PAGE: Cuentos / Audio
# ---------------------------
else:
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("### 📖 Cuentos para bebé")
    st.write("Escribe o selecciona un cuento corto y conviértelo en audio para arrullar.")
    st.markdown("</div>", unsafe_allow_html=True)

    story = st.selectbox("Historias de ejemplo", [
        "El osito y la luna",
        "La nube que quería jugar",
        "La estrella tímida"
    ])
    custom = st.text_area("O escribe tu propio cuento (máx 500 caracteres):", max_chars=500)

    text_to_use = custom.strip() if custom.strip() else {
        "El osito y la luna": "Había una vez un osito que miraba la luna y soñaba con volar.",
        "La nube que quería jugar": "Una nube blanca rodaba por el cielo buscando amistades.",
        "La estrella tímida": "Una pequeña estrella aprendió a brillar cuando alguien la miró con cariño."
    }[story]

    lang = st.selectbox("Idioma", ["es", "en"], index=0)
    if st.button("Generar audio"):
        with st.spinner("Generando audio..."):
            audio_bytes = play_audio_and_return_bytes(text_to_use, lang=lang)
            st.audio(audio_bytes, format="audio/mp3")
