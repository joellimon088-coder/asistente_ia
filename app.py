import streamlit as st
from google import genai
import base64
import os

# --- 1. CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Asistente IA - Joel Muñoz", layout="wide", page_icon="💻")

# --- 2. FUNCIÓN PARA EL FONDO DE ANIME (SIN FRANJAS BLANCAS) ---
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stHeader"] {{ display: none !important; }}
            .main .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
                background-color: rgba(0, 0, 0, 0.75); 
                border-radius: 25px;
                margin-top: 50px;
                margin-bottom: 50px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            h1, h2, h3, p, span, .stMarkdown, [data-testid="stCaption"] p {{
                color: white !important;
                text-shadow: 1px 1px 2px black;
            }}
            [data-testid="stChatMessage"] {{
                background-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 15px;
            }}
            [data-testid="stSidebar"] {{ background-color: rgba(15, 15, 15, 0.95) !important; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Archivo 'fondo_anime.jpg' no encontrado.")

add_bg_from_local('fondo_anime.jpg')

# --- 3. CONFIGURACIÓN DE LA API (PRIVADA) ---
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("⚠️ No se encontró la API KEY. Configúrala en las variables de entorno.")
    st.stop()

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Error de inicialización: {e}")
    st.stop()

# --- 4. DISEÑO DE CABECERA ---
st.title("🤖 Mi Asistente Limon")
st.caption("Ingeniería en Computación | CUTonalá | Joel Alejandro Muñoz Limón")
st.divider()

with st.sidebar:
    st.header("⚙️ Panel de Control")
    nombre_ia = st.text_input("Nombre de la IA:", value="Cacho ia")
    personalidad = st.text_area("Personalidad:", value="Eres un personaje de anime .")
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. LÓGICA DE MENSAJES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. EL "BRAZO ROBÓTICO" CON CASCADA (FAILOVER) ---
if prompt := st.chat_input("Escribe tu duda técnica aquí, Joel..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instruccion = f"Tu nombre es {nombre_ia}. Actúa como {personalidad}. Usuario dice: "
        
        # Lista de modelos en orden de prioridad
        modelos_disponibles = ["gemini-3-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        respuesta = ""
        exito = False

        for modelo_actual in modelos_disponibles:
            try:
                # Intentamos generar contenido con el modelo actual
                response = client.models.generate_content(
                    model=modelo_actual,
                    contents=instruccion + prompt
                )
                respuesta = response.text
                exito = True
                break  # Si funciona, salimos del ciclo for
            except Exception:
                # Si falla (por cuota agotada o error), avisamos y pasamos al siguiente
                st.warning(f"⚠️ El modelo {modelo_actual} no está disponible. Intentando con el siguiente...")
                continue

        if not exito:
            respuesta = "❌ Lo siento Joel, parece que agotamos las 20 consultas en TODOS los modelos por hoy."

        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
