import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from PIL import Image

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(page_title="BAE - Baby Monitor", page_icon="👶", layout="centered")

# Paleta de colores BAE (pasteles)
COLOR_FONDO = "#FFF8E7"
COLOR_MENTA = "#C8E4D8"
COLOR_DURAZNO = "#FFD7B5"
COLOR_AZUL = "#CDE5FF"
COLOR_TEXTO = "#4D797A"

# =============================
# ESTILOS CSS
# =============================
st.markdown(f"""
<style>
    body {{
        background-color: {COLOR_FONDO};
        font-family: 'Poppins', sans-serif;
    }}
    .main-title {{
        text-align: center;
        color: {COLOR_TEXTO};
        font-size: 2.5rem;
        font-weight: 700;
        animation: fadeIn 1.5s ease;
    }}
    .status-box {{
        background: linear-gradient(145deg, {COLOR_MENTA}, {COLOR_AZUL});
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.4s ease;
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
        50% {{ transform: translateY(-8px); }}
        100% {{ transform: translateY(0px); }}
    }}
    .footer {{
        text-align: center;
        color: #777;
        margin-top: 20px;
        font-size: 0.9rem;
    }}
</style>
""", unsafe_allow_html=True)

# =============================
# CABECERA
# =============================
st.markdown("<h1 class='main-title'>👶 BAE - Monitor del Bebé</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6A6A6A;'>Supervisión ambiental inteligente y visual</p>", unsafe_allow_html=True)

# =============================
# CONFIGURAR MQTT WEBSOCKET
# =============================
broker = "test.mosquitto.org"
topic = "sensor/temperatura"

if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = {"t": 0, "h": 0}

def on_message(client, userdata, message):
    """Recibir datos del sensor vía MQTT"""
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
        img = "https://i.ibb.co/fXxB4n1/bebe-frio.png"
    elif temp > 28:
        estado = "El cuarto está muy caliente ☀️"
        color = COLOR_DURAZNO
        img = "https://i.ibb.co/nRyYbJn/bebe-calor.png"
    else:
        estado = "El ambiente está perfecto 🌤️"
        color = COLOR_MENTA
        img = "https://i.ibb.co/n7VnLVG/bebe-feliz.png"

    with placeholder.container():
        st.markdown(f"""
        <div class="status-box" style="background:linear-gradient(145deg, {color}, {COLOR_FONDO});">
            <img src="{img}" width="250" style="border-radius:20px; margin-bottom:10px;">
            <div class="temp">{temp:.1f} °C</div>
            <div class="estado">{estado}</div>
            <p style="color:#777; font-size:1rem;">Humedad: {hum:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        # Botón para prender luz por voz (futuro)
        st.markdown("""
        <div style="text-align:center; margin-top:1rem;">
            <button style="
                background-color:#FFD7B5;
                border:none;
                color:#4D797A;
                font-size:1.2rem;
                padding:10px 25px;
                border-radius:15px;
                cursor:pointer;
                box-shadow:0 3px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;"
                onmouseover="this.style.transform='scale(1.05)';"
                onmouseout="this.style.transform='scale(1)';">
                💡 Encender luz del bebé
            </button>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='footer'>💛 BAE - Baby Adaptive Environment</div>", unsafe_allow_html=True)

    time.sleep(5)
