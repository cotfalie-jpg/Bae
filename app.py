# app.py
import io
import os
import tempfile
import time
import base64
import random
import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from PIL import Image

# Colores BAE (user provided)
COLOR_ORANGE = "#DD8E6B"
COLOR_CREAM = "#FFF8EA"
COLOR_YELLOW = "#FFF2C3"
COLOR_BLUE = "#C6E2E3"
TEXT_COLOR = "#3C3C3C"

st.set_page_config(page_title="BAE - Voz + Dashboard", page_icon="👶", layout="wide")

# CSS estilo BAE
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
    .stApp {{
        background: linear-gradient(180deg, {COLOR_CREAM} 0%, #FFFFFF 100%);
        color: {TEXT_COLOR};
        font-family: Poppins, sans-serif;
        padding: 1.2rem;
    }}
    header .decoration {{
        display:none;
    }}
    .title h1 {{
        color: {COLOR_ORANGE};
        font-weight:700;
        margin-bottom:0.1rem;
    }}
    .subtitle {{
        color: #6b6b6b;
        margin-top:0;
        margin-bottom:1rem;
    }}
    .card {{
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03);
        border-left: 8px solid {COLOR_ORANGE}22;
    }}
    .small-card {{
        background: {COLOR_CREAM};
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.03);
    }}
    .btn-main > button {{
        background: {COLOR_BLUE};
        color: {TEXT_COLOR};
        border-radius:10px;
        padding: 8px 16px;
        font-weight:600;
    }}
    .response-box {{
        background: linear-gradient(90deg, {COLOR_YELLOW}, #FFFEEE);
        padding:12px;border-radius:12px;margin-top:8px;
    }}
    </style>
""", unsafe_allow_html=True)

# Header
col_h1, col_h2 = st.columns([4,1])
with col_h1:
    st.markdown('<div class="title"><h1>BAE</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interfaz por voz para cuidar al bebé — pregunta, pide música o cuenta un cuento</div>', unsafe_allow_html=True)
with col_h2:
    # placeholder logo: si tienes logo local, carga aquí
    try:
        logo = Image.open("logo_bae.png")
        st.image(logo, width=72)
    except:
        st.write("")

st.markdown("")  # spacing

# Left: dashboard
left, right = st.columns([2.2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Panel de Bienestar")
    # Simulación de sensores
    temp = round(36 + random.uniform(-0.8, 1.4), 1)
    hum = int(45 + random.uniform(-10, 10))
    st.markdown(f"**Temperatura corporal — {temp} °C**")
    st.progress(min(max((temp-35)/4, 0), 1))  # visual simple
    st.markdown(f"**Humedad ambiental — {hum}%**")
    st.progress(hum/100)
    # alerts
    alerts = []
    if temp < 36.0:
        alerts.append("Temperatura baja — revisar abrigo del bebé.")
    if temp > 37.6:
        alerts.append("Temperatura alta — posible fiebre.")
    if hum < 30:
        alerts.append("Humedad baja — resequedad ambiental.")
    if not alerts:
        st.success("Condiciones estables")
    else:
        for a in alerts:
            st.warning(a)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")  # spacing

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interacciones por voz")
    st.write("Graba tu pregunta con el botón (o sube un archivo de audio).")
    # Try to import recorder component, else fallback to uploader
    use_recorder = False
    try:
        from streamlit_audio_recorder import audio_recorder
        use_recorder = True
    except Exception:
        use_recorder = False

    audio_bytes = None
    if use_recorder:
        st.markdown("Pulse **Start** para grabar y después **Stop**. (fallback: subir archivo)")
        audio_data = audio_recorder()
        # audio_data is bytes (wav) if recorded, else None
        if audio_data:
            audio_bytes = audio_data
    else:
        st.info("Componente de grabación no instalado. Usa el uploader (graba en tu teléfono y sube el archivo).")
        uploaded = st.file_uploader("Sube tu grabación (wav/mp3/m4a)", type=["wav","mp3","m4a","ogg"])
        if uploaded:
            audio_bytes = uploaded.read()

    st.markdown("---")
    st.markdown("Comandos de ejemplo: *¿Cómo está mi bebé?*, *Pon música*, *Cuéntame un cuento*")
    st.markdown("</div>", unsafe_allow_html=True)

    # Process button
    if st.button("Procesar audio y responder", key="process"):
        if not audio_bytes:
            st.error("No hay audio para procesar. Graba o sube un archivo.")
        else:
            with st.spinner("Transcribiendo y generando respuesta..."):
                # --- Convert audio to WAV if needed using pydub ---
                try:
                    # try to detect format by loading
                    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
                except Exception as e:
                    st.error(f"No se pudo leer el audio: {e}")
                    audio = None

                if audio:
                    wav_io = io.BytesIO()
                    audio.export(wav_io, format="wav")
                    wav_io.seek(0)

                    # Speech recognition
                    r = sr.Recognizer()
                    with sr.AudioFile(wav_io) as source:
                        audio_data = r.record(source)
                        try:
                            text = r.recognize_google(audio_data, language="es-ES")
                        except sr.UnknownValueError:
                            text = ""
                        except Exception as e:
                            st.error(f"Error en reconocimiento: {e}")
                            text = ""

                    if not text:
                        st.error("No se entendió el audio. Intenta hablar más claro o probar otro archivo.")
                    else:
                        st.markdown("**Transcripción:**")
                        st.info(text)

                        # Simple intent classification (rule-based)
                        t = text.lower()
                        response_text = "Lo siento, no entendí la solicitud."

                        if any(w in t for w in ["temperatura","caliente","frío","fiebre","temperatura del bebé","cómo está"]):
                            response_text = f"La temperatura actual aproximada es {temp} °C y la humedad {hum}%. {'Atención: '+alerts[0] if alerts else ''}"
                        elif any(w in t for w in ["música","poner música","suena","reproduce música","canción","relajante"]):
                            response_text = "Listo — reproduzco música suave para el bebé."
                        elif any(w in t for w in ["cuento","cuéntame","dime un cuento","narrar"]):
                            # small example story
                            response_text = (
                                "Había una vez un osito curioso llamado Luno que vivía en una nube. "
                                "Cada noche, Luno bajaba a la tierra a abrazar a los niños con su luz cálida. "
                                "Y así, todos dormían tranquilos."
                            )
                        else:
                            response_text = "Puedo consultar la temperatura, reproducir música o contar un cuento. ¿Qué quieres que haga?"

                        # Generate audio response with gTTS
                        try:
                            tts = gTTS(response_text, lang="es")
                            tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                            tts.save(tmpfile.name)
                            tmpfile.close()
                            # play audio
                            st.audio(tmpfile.name)
                            # show text
                            st.markdown('<div class="response-box"><strong>BAE dice:</strong> ' + response_text + '</div>', unsafe_allow_html=True)
                            # cleanup later
                            time.sleep(0.5)
                            os.unlink(tmpfile.name)
                        except Exception as e:
                            st.error(f"No se pudo generar audio TTS: {e}")
    # Quick demo buttons (no audio)
    st.markdown("---")
    st.write("Pruebas rápidas:")
    if st.button("¿Cómo está mi bebé? (demo)"):
        st.info(f"Temperatura ~ {temp} °C — Humedad {hum}%")
    if st.button("Cuéntame un cuento (demo)"):
        demo_story = "Había una vez un osito llamado Luno que cuidaba de las estrellas..."
        tts = gTTS(demo_story, lang="es")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name); tmp.close()
        st.audio(tmp.name); os.unlink(tmp.name)


with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Controles rápidos")
    st.write("Usa los botones para acciones comunes.")
    if st.button("Reproducir música de cuna"):
        # simple TTS for demo (replace with file streaming in prod)
        tts = gTTS("Suena ahora una canción suave para el bebé.", lang="es")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name); tmp.close()
        st.audio(tmp.name); os.unlink(tmp.name)
    if st.button("Pedir estado rápido"):
        st.success(f"Temperatura: {temp} °C — Humedad: {hum}%")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("BAE — Interacciones por voz para cuidado infantil (demo). Requiere internet para reconocimiento de voz y gTTS.")

