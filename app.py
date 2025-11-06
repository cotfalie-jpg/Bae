import streamlit as st
from gtts import gTTS
import openai
import os
from pydub import AudioSegment
from io import BytesIO
import base64

# 🍼 Configuración de la app
st.set_page_config(page_title="BAE | Bebé Asistente Emocional", page_icon="🍼", layout="centered")

# 🌈 Estilo pastel BAE
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #fff7da, #fef3e2, #e4f6ff, #dff7ec);
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
}
@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
h1 {
    text-align: center;
    color: #2c423f;
    font-weight: 800;
    font-family: 'Poppins', sans-serif;
}
.big-button button {
    background: linear-gradient(135deg, #fddf91, #fbc687);
    border: none;
    color: #2c423f;
    font-size: 1.2rem;
    font-weight: 600;
    padding: 0.8rem 2rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    box-shadow: 0 6px 15px rgba(250,180,100,0.3);
}
.big-button button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #ffe5a3, #ffd4a2);
}
.response-box {
    background-color: rgba(255,255,255,0.6);
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1rem;
    color: #2c423f;
    font-size: 1.1rem;
    text-align: center;
    font-family: 'Nunito', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# 🧸 Encabezado
st.markdown("<h1>🍼 BAE — Bebé Asistente Emocional</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#2c423f;'>Habla con BAE: puede contarte cuentos, poner música o ayudarte a cuidar al bebé 💛</p>", unsafe_allow_html=True)

# 🔑 Clave de API
api_key = st.text_input("🔑 Ingresa tu clave de OpenAI", type="password", placeholder="sk-...")
if api_key:
    openai.api_key = api_key

# 🎙️ Grabación de voz
audio_file = st.audio_input("Habla con BAE (haz tu pregunta o pide algo)", help="Puedes decir: 'cuéntame un cuento', 'qué temperatura tiene el bebé', 'pon música suave'")

# 🔄 Procesamiento
if st.button("💫 Procesar Audio", key="procesar", help="Haz clic para que BAE procese tu voz", use_container_width=True):
    if not api_key:
        st.warning("Por favor ingresa tu API key antes de continuar 🗝️")
    elif not audio_file:
        st.info("🎙️ Graba tu voz para que BAE pueda escucharte.")
    else:
        with st.spinner("🎧 BAE está escuchando..."):
            # Guardar audio temporalmente
            with open("input.wav", "wb") as f:
                f.write(audio_file.getbuffer())

            # 🔊 Aquí puedes integrar tu modelo de reconocimiento de voz o texto
            # Por simplicidad, simulamos texto procesado:
            user_text = "BAE, cuéntame un cuento sobre un osito que tiene sueño"

            # 🤖 Llamar al modelo de OpenAI
            prompt = f"Eres BAE, un asistente tierno, calmado y con voz maternal. Responde como si hablaras a un bebé o a su cuidador. Pregunta: {user_text}"
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content

            # 🍼 Mostrar respuesta
            st.markdown('<div class="response-box">🧸 ' + answer + '</div>', unsafe_allow_html=True)

            # 🎤 Generar respuesta hablada
            tts = gTTS(answer, lang="es")
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.audio(audio_buffer, format="audio/mp3")

            # 💫 Animación de ternura (simple efecto de texto)
            st.markdown("<p style='text-align:center; font-size:1.2rem; color:#2c423f;'>💛 BAE sonríe y te mira con ternura 💛</p>", unsafe_allow_html=True)


