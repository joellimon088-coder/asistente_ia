import streamlit as st
import google.generativeai as genai  # Cambio en la importación para compatibilidad estándar
import base64
import os  # Importante para leer la API KEY de forma segura

# --- 1. CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Asistente IA - Joel Muñoz", layout="wide", page_icon="💻")

# --- 2. FUNCIÓN PARA EL FONDO DE ANIME ---
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
        st.warning("Archivo de imagen no encontrado. Verifica el nombre del archivo.")

# Llama a la función con el nombre exacto de tu archivo
add_bg_from_local('fondo_anime.jpg')

# --- 3. CONFIGURACIÓN DE LA API (SEGURA) ---
# Aquí ya no pegamos la clave directamente. La obtenemos del sistema.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("No se encontró la API KEY. Configúrala en los Secrets de Streamlit.")
else:
    try:
        genai.configure(api_key=API_KEY)
        # Usamos el cliente estándar de la librería
        model_main = genai.GenerativeModel('gemini-1.5-flash') # Modelo principal
    except Exception as e:
        st.error(f"Error de inicialización: {e}")

# --- 4. DISEÑO DE CABECERA ---
st.title("🤖 Mi Asistente Limon")
st.caption("Ingeniería en Computación | CUTonalá | Joel Alejandro Muñoz Limón")
st.divider()

with st.sidebar:
    st.header("⚙️ Panel de Control")
    nombre_ia = st.text_input("Nombre de la IA:", value="Cacho ia")
    personalidad = st.text_area("Personalidad:", value="Eres un asistente experto en programación y hardware.")
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. LÓGICA DE MENSAJES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. PETICIÓN A LA IA ---
if prompt := st.chat_input("Escribe tu duda técnica aquí, Joel..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        contexto_completo = f"Tu nombre es {nombre_ia}. Personalidad: {personalidad}. Usuario: {prompt}"
        
        try:
            # Intento con el modelo configurado
            response = model_main.generate_content(contexto_completo)
            respuesta = response.text
        except Exception as e:
            respuesta = f"❌ Error al conectar con Gemini: {e}"

        st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})