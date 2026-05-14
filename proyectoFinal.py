import streamlit as st
import google.generativeai as genai
import re

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="J-Architect: Full AI Auditor", layout="wide", page_icon="☕")

# --- 2. GESTIÓN DE MEMORIA (SESSION STATE) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = ""
if "last_refactor" not in st.session_state:
    st.session_state.last_refactor = ""

# --- 3. ESTILOS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin-bottom: 10px; font-family: sans-serif; }
    .user-bubble { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
    .ai-bubble { background-color: #f1f8e9; border-left: 5px solid #4caf50; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VALIDACIÓN DE REGLAS (MANTENIDA) ---
def validate_java_rules(code):
    checks = {
        "Constructor Injection": (r"public\s+\w+\s*\([^)]*\w+\s+\w+\s*\)\s*\{", "Uso de inyección por constructor detectado (Buena práctica)."),
        "Custom Exception Handling": (r"catch\s*\(\s*(?!Exception|Throwable|Runtime)\w+\s+\w+\s*\)", "Manejo de excepciones específicas detectado."),
        "Quarkus/Lombok Optimization": (r"@Inject|@Data|@Builder|@ApplicationScoped", "Uso de anotaciones de productividad y scopes correctos."),
        "Avoid Field Injection": (r"@Autowired\s+private", "CRÍTICO: Se detectó inyección por campo (Mala práctica).", True), # True si es negativo
        "Hardcoded Secret Check": (r"[\"'][a-zA-Z0-9+/]{20,}[\"']", "ADVERTENCIA: Posible secreto o token hardcodeado.", True)
    }
    results = []
    for name, data in checks.items():
        pattern, msg, *is_neg = data
        match = re.search(pattern, code)
        if is_neg and is_neg[0]:
            results.append(f"❌ **{name}**: {msg}" if match else f"✅ **{name}**: No detectado.")
        else:
            results.append(f"✅ **{name}**: {msg}" if match else f"⚠️ **{name}**: No verificado.")
    return results

# --- 5. CONFIGURACIÓN DE IA (GEMINI) ---
# 1. Intentar obtener la clave de Secrets o del input
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Google API Key", type="password")
#api_key = st.sidebar.text_input("Google API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "Actúa como un Principal Software Architect experto en Java. "
            "Tu tarea es analizar el código y devuelve SIEMPRE estas secciones marcadas:\n"
            "[DIAGNOSTICO]: Analiza deuda técnica y antipatrones.\n"
            "[REFACTOR]: Devuelve el código COMPLETO y corregido dentro de un bloque de código markdown (```java ... ```).\n"
            "[DEVOPS]: Sugiere configuración de Docker o CI/CD.\n"
            "En el REFACTOR, asegúrate de utilizar lombok, corregir @Autowired por constructores y mejorar el manejo de excepciones."
            "Mantén un tono profesional y técnico. Recuerda el código refactorizado en la conversación del chat."
        )
    )
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
else:
    st.warning("Por favor, introduce tu Google API Key en la barra lateral para comenzar.")

# --- 6. INTERFAZ DE USUARIO ---
st.title("☕ J-Architect: Auditoría & Chat")
st.caption("Solución Integral para Modernización de Aplicaciones Java (SDLC Optimized)")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.markdown("### 🔍 Panel de Análisis")
    uploaded_file = st.file_uploader("Subir .java o pom.xml", type=["java", "xml"])
    
    default_code = ""
    if uploaded_file:
        default_code = uploaded_file.read().decode("utf-8")
    
    code_input = st.text_area("Código a Auditar:", value=default_code, height=350)
    
    if st.button("🚀 Iniciar Auditoría Completa", type="primary", use_container_width=True):
        if not api_key:
            st.error("Introduce la API Key.")
        elif not code_input:
            st.warning("El código está vacío.")
        else:
            with st.spinner("Ejecutando diagnóstico y refactorización..."):
                response = st.session_state.chat_session.send_message(f"Auditoría de código:\n\n{code_input}")
                st.session_state.last_analysis = response.text
                
                # Extraer código para la pestaña de refactor
                ref_match = re.search(r"\[REFACTOR\](.*?)(?=\[DEVOPS\]|$)", response.text, re.S)
                if ref_match:
                    code_block = re.search(r"```java\s*(.*?)\s*```", ref_match.group(1), re.S)
                    st.session_state.last_refactor = code_block.group(1) if code_block else ref_match.group(1).strip()

with col2:
    st.markdown("### 📊 Resultados de la Auditoría")
    if st.session_state.last_analysis:
        res = st.session_state.last_analysis
        diag_m = re.search(r"\[DIAGNOSTICO\](.*?)(?=\[REFACTOR\]|$)", res, re.S)
        dev_m = re.search(r"\[DEVOPS\](.*?)$", res, re.S)
        
        t_diag, t_ref, t_val, t_dev = st.tabs(["📝 Diagnóstico", "🛠️ Refactor", "✅ Validación", "🚀 DevOps"])
        
        with t_diag:
            st.markdown(diag_m.group(1).strip() if diag_m else "Revisa el reporte general.")
            
        with t_ref:
            if st.session_state.last_refactor:
                st.code(st.session_state.last_refactor, language="java")
                st.download_button("💾 Descargar Refactor", st.session_state.last_refactor, file_name="Refactored.java")
            else:
                st.info("Sin código refactorizado.")
                
        with t_val:
            st.subheader("Cumplimiento Estático")
            if st.session_state.last_refactor:
                for rule in validate_java_rules(st.session_state.last_refactor):
                    st.write(rule)
            else:
                st.info("Realiza una auditoría para validar reglas.")
                
        with t_dev:
            st.markdown(dev_m.group(1).strip() if dev_m else "Sin datos DevOps.")
    else:
        st.info("Los resultados aparecerán aquí tras la auditoría.")

# --- 7. CHATBOT INTERACTIVO (PIE DE PÁGINA) ---
st.markdown("---")
st.markdown("### 💬 Chat Interactivo con el Arquitecto")

chat_box = st.container(height=350)
for msg in st.session_state.chat_history:
    style = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    chat_box.markdown(f"<div class='chat-bubble {style}'><b>{msg['role'].upper()}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

if user_query := st.chat_input("Pregunta sobre mejoras adicionales, seguridad o migración..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    with st.spinner("Pensando..."):
        # Enviar mensaje al objeto chat_session de Gemini para mantener memoria
        full_query = f"Sobre el código Java analizado: {user_query}"
        chat_response = st.session_state.chat_session.send_message(full_query)
        st.session_state.chat_history.append({"role": "model", "content": chat_response.text})
    
    st.rerun()