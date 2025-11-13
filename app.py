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
st.markdown("<h3>Vigila el ambiente del bebé con ternura y tecnología pastel 💛</h3>", unsafe_a_

