# app.py
import streamlit as st
import time
import io
import os
import random
from datetime import datetime, timedelta
from gtts import gTTS
import pandas as pd
import altair as alt
from PIL import Image

# ----------------------------
# CONFIG - COLORES Y ESTILO BAE
# ----------------------------
COLOR_1 = "#DD8E6B"   # melocotón
COLOR_2 = "#FFF8EA"   # crema fondo
COLOR_3 = "#FFF2C3"   # amarillo pálido
COLOR_4 = "#C6E2E3"   # azul pastel

st.set_page_config(page_title="BAE Sense Dashboard", page_icon="👶", layout="wide")

st.markdown(
    f"""
    <style>
        /* Página */
        .stApp {{ background: {COLOR_2}; font-family: 'Poppins', sans-serif; }}

        /* Header */
        .bae-header {{ display:flex; align-items:center; gap:18px; }}
        .bae-logo {{ width:72px; height:72px; border-radius:16px; background:linear-gradient(135deg,{COLOR_4},{COLOR_3}); display:flex; align-items:center; justify-content:center; font-weight:700; color:#ffffff; box-shadow: 0 6px 18px rgba(0,0,0,0.06); }}

        h1 {{ color: #2E2E2E; margin: 0; }}
        .subtitle {{ color: #6b6b6b; margin-top:4px; }}

        /* Cards */
        .card {{
            background: #FFF8EA;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 6px 18px rgba(213,170,150,0.12);
            border-left: 8px solid {COLOR_1};
        }}

        /* small pill */
        .pill {{ background: {COLOR_3}; color:#6b3d2b; padding:6px 10px; border-radius:100px; font-weight:600; }}

        /* animated badge */
        @keyframes floaty {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-6px); }}
            100% {{ transform: translateY(0px); }}
        }}
        .floaty {{ animation: floaty 3s ease-in-out infinite; }}

        /* botones */
        .bae-btn {{
            background: linear-gradient(90deg, {COLOR_4}, {COLOR_1});
            color: #fff; padding:10px 18px; border-radius:12px; border:none; font-weight:700;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helpers: audio generation & sample data
# ----------------------------
def text_to_mp3_bytes(text: str, lang: str = "es") -> bytes:
    """Genera audio mp3 desde text usando gTTS y devuelve bytes."""
    tts = gTTS(text, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()

def generate_sample_history(minutes=120):
    """Genera dataframe de ejemplo para temperatura/humedad."""
    now = datetime.now()
    times = [now - timedelta(minutes=i) for i in range(minutes)][::-1]
    temps = [round(36.0 + random.uniform(-0.6, 1.5), 2) for _ in times]
    hums = [round(45 + random.uniform(-10, 12), 1) for _ in times]
    return pd.DataFrame({"ts": times, "temperature": temps, "humidity": hums})

# Datos iniciales simulados
history = generate_sample_history(240)
current_temp = float(history.temperature.iloc[-1])
current_hum = float(history.humidity.iloc[-1])

# ----------------------------
# LAYOUT: Header
# ----------------------------
logo_present = False
# intenta cargar logo local si existe
if os.path.exists("logo_bae.png"):
    logo_present = True

col1, col2 = st.columns([0.18, 0.82])
with col1:
    if logo_present:
        st.image("logo_bae.png", width=72)
    else:
        st.markdown('<div class="bae-logo">BAE</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="bae-header">', unsafe_allow_html=True)
    st.markdown("<h1>BAE Sense Dashboard</h1>", unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Monitoreo ambiental y asistente multimodal para bebés — voz, texto y visual.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ----------------------------
# Tabs: Panel de Bienestar / Asistente BAE
# ----------------------------
tab1, tab2 = st.tabs(["Panel de Bienestar", "Asistente BAE"])

# ----------------------------
# TAB 1: Panel de Bienestar
# ----------------------------
with tab1:
    # Top row: indicadores
    k1, k2, k3 = st.columns([1,1,1])
    with k1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3>Temperatura corporal</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:36px; font-weight:700'>{current_temp} °C</div>", unsafe_allow_html=True)
        st.markdown("<div>Rango objetivo: 36.0 - 37.5 °C</div>", unsafe_allow_html=True)
        if current_temp < 36.0 or current_temp > 37.5:
            st.markdown("<div style='color:#9b2b2b; margin-top:8px; font-weight:700'>Alerta: temperatura fuera de rango</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with k2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3>Humedad ambiental</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:36px; font-weight:700'>{current_hum} %</div>", unsafe_allow_html=True)
        st.markdown("<div>Ideal: 40% - 60%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with k3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3>Acciones rápidas</h3>", unsafe_allow_html=True)
        st.markdown('<div style="display:flex; gap:8px; margin-top:8px;">', unsafe_allow_html=True)
        if st.button("Actualizar datos", key="refresh"):
            # simula nueva lectura
            new_temp = round(36.0 + random.uniform(-0.8, 1.6), 2)
            new_hum = round(45 + random.uniform(-12, 12), 1)
            now = datetime.now()
            history.loc[len(history)] = [now, new_temp, new_hum]
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px'>Modo sensor:</div>", unsafe_allow_html=True)
        st.radio("Fuente", ("Simulado (local)", "Broker MQTT (Wokwi)"), index=0, horizontal=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")  # espacio

    # Gráficos históricos
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Últimas lecturas</h3>", unsafe_allow_html=True)

    # Chart con Altair
    chart = alt.Chart(history.tail(120)).transform_fold(
        fold=["temperature", "humidity"],
        as_=["measure", "value"]
    ).mark_line(point=False).encode(
        x=alt.X("ts:T", title=""),
        y=alt.Y("value:Q", title=""),
        color=alt.Color("measure:N", scale=alt.Scale(range=[COLOR_1, COLOR_4]))
    ).properties(height=280)
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Panel inferencias (simple)
    st.markdown("<div style='margin-top:14px' class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Recomendaciones</h3>", unsafe_allow_html=True)
    if current_temp > 37.5:
        st.markdown("- Mantener hidratación, revisar ambiente y comunicar a profesional de salud.")
    elif current_temp < 36.0:
        st.markdown("- Abrigar adecuadamente y verificar signos de hipotermia.")
    else:
        st.markdown("- Temperatura dentro del rango esperado. Monitoreo continuo.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# TAB 2: Asistente BAE (voz/texto + cuentos + música)
# ----------------------------
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>Asistente BAE — multimodal</h3>", unsafe_allow_html=True)
    st.markdown("<div>Interacciona por texto (o pega un comando). Dispones de tres acciones rápidas: consultar temperatura, reproducir música relajante o pedir un cuento.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2,1])
    with col_a:
        user_cmd = st.text_input("Escribe aquí tu comando (ej: 'temperatura', 'poner música', 'cuéntame un cuento')", value="")
        if st.button("Enviar comando"):
            cmd = user_cmd.strip().lower()
            if "temp" in cmd or "temper" in cmd:
                st.success(f"La temperatura actual es {current_temp} °C")
                # generar respuesta en audio
                text_resp = f"La temperatura actual del bebé es {current_temp} grados Celsius. Mantén monitoreo."
                audio_bytes = text_to_mp3_bytes(text_resp, lang="es")
                st.audio(audio_bytes, format="audio/mp3")
            elif "música" in cmd or "musica" in cmd or "relax" in cmd or "canción" in cmd:
                st.info("Reproduciendo música relajante (generada)...")
                # cuento corto musicalizado (simulación): reproducir un texto en voz
                music_text = "Inicio de música relajante para bebé. Recomendamos una lista de reproducción con sonido blanco suave."
                audio_bytes = text_to_mp3_bytes(music_text, lang="es")
                st.audio(audio_bytes, format="audio/mp3")
            elif "cuento" in cmd or "cuenta" in cmd or "dormir" in cmd:
                st.info("Narrando cuento corto...")
                # cuento breve
                cuento = ("Había una vez un osito que quería encontrar una estrella. "
                         "Cada noche miraba el cielo y soñaba con tocarla. "
                         "Una noche la estrella bajó un poquito y el osito le cantó una canción. "
                         "La estrella brilló, y el osito se durmió con una sonrisa. Buenas noches.")
                audio_bytes = text_to_mp3_bytes(cuento, lang="es")
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.warning("Comando no reconocido. Prueba: 'temperatura', 'poner música', 'cuéntame un cuento'")

    with col_b:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>Acciones rápidas</h4>", unsafe_allow_html=True)
        if st.button("📈 Consultar temperatura"):
            st.success(f"Temperatura: {current_temp} °C")
            audio_bytes = text_to_mp3_bytes(f"La temperatura es {current_temp} grados", lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        if st.button("🎵 Reproducir música relajante"):
            audio_bytes = text_to_mp3_bytes("Reproduciendo música suave para bebé. Relájate y disfruta.", lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        if st.button("📖 Contar un cuento"):
            cuento = ("Había una vez un conejito que se perdió en un jardín de flores. "
                     "Un amable luciérnaga lo guió hasta su cama y le contó historias de estrellas. "
                     "Al final, el conejito encontró su hogar y soñó con nuevos amigos.")
            audio_bytes = text_to_mp3_bytes(cuento, lang="es")
            st.audio(audio_bytes, format="audio/mp3")
        st.markdown("</div>", unsafe_allow_html=True)

    # Historial simple de interacciones
    st.markdown('<div style="margin-top:12px" class="card">', unsafe_allow_html=True)
    st.markdown("<h4>Historial de interacción</h4>", unsafe_allow_html=True)
    if "history_cmds" not in st.session_state:
        st.session_state.history_cmds = []
    # guardar si hubo entrada manual
    if st.button("Guardar comando actual en historial"):
        if user_cmd.strip():
            st.session_state.history_cmds.append({"cmd": user_cmd, "ts": datetime.now().isoformat()})
            st.success("Comando guardado en historial")
        else:
            st.warning("Escribe un comando primero")
    for e in reversed(st.session_state.history_cmds[-6:]):
        st.markdown(f"- {e['ts'][:19]} → {e['cmd']}")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer / nota
# ----------------------------
st.markdown("---")
st.markdown(
    "<div style='display:flex; justify-content:space-between; align-items:center;'>"
    "<div style='color:#6b6b6b'>BAE • Prototipo educativo — Multimodal & accesible</div>"
    "<div style='color:#6b6b6b'>Colores: pastel • UI inspirada para familias</div>"
    "</div>",
    unsafe_allow_html=True
)

