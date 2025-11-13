import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

# ----------------------------------
# CONFIGURACIÓN VISUAL ESTILO BAE 🌼
# ----------------------------------
st.set_page_config(page_title="👶 BAE - Control MQTT", page_icon="👶", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #FFF6E9, #FFEBD2, #FFF9E5);
    font-family: 'Poppins', sans-serif;
    color: #5C4438;
}
h1 {
    text-align: center;
    color: #5C4438;
    font-weight: 700;
}
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
div[data-testid="stSlider"] > div > div {
    background-color: #F9C784 !important;
}
.css-1offfwp, .stMarkdown {
    color: #7A5E48 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# INFORMACIÓN DEL SISTEMA
# ----------------------------------
st.title("👶 BAE - Control MQTT")
st.caption("Supervisión y control con estilo BAE 💛")

st.write("Versión de Python:", platform.python_version())

# ----------------------------------
# VARIABLES Y CONFIGURACIÓN MQTT
# ----------------------------------
values = 0.0
act1 = "OFF"

def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"   # 🔸 CAMBIO
port = 1883                           # 🔸 CAMBIO
client1 = paho.Client("GIT-HUB")
client1.on_message = on_message

# ----------------------------------
# INTERFAZ PRINCIPAL
# ----------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button('🟢 Encender (ON)'):
        act1 = "ON"
        client1 = paho.Client("GIT-HUB")                           
        client1.on_publish = on_publish                          
        client1.connect(broker, port)  
        message = json.dumps({"Act1": act1})
        ret = client1.publish("bae", message)  # 🔸 CAMBIO
        st.success("Mensaje ON enviado al broker 💛")
    else:
        st.write('')

with col2:
    if st.button('🔴 Apagar (OFF)'):
        act1 = "OFF"
        client1 = paho.Client("GIT-HUB")                           
        client1.on_publish = on_publish                          
        client1.connect(broker, port)  
        message = json.dumps({"Act1": act1})
        ret = client1.publish("bae", message)  # 🔸 CAMBIO
        st.warning("Mensaje OFF enviado al broker 💤")
    else:
        st.write('')

# ----------------------------------
# SLIDER DE VALOR ANALÓGICO
# ----------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🎚️ Control Analógico")

values = st.slider('Selecciona el valor', 0.0, 100.0)
st.write('Valor seleccionado:', values)

if st.button('📤 Enviar valor analógico'):
    client1 = paho.Client("GIT-HUB")                           
    client1.on_publish = on_publish                          
    client1.connect(broker, port)   
    message = json.dumps({"Analog": float(values)})
    ret = client1.publish("bae", message)  # 🔸 CAMBIO
    st.success("Valor analógico enviado correctamente 🌤️")
else:
    st.write('')

# ----------------------------------
# PIE DE PÁGINA
# ----------------------------------
st.markdown("<br><p style='text-align:center;color:#8B6B4E;'>💛 Proyecto BAE - Interfaces Multimodales 2025</p>", unsafe_allow_html=True)

