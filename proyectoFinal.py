import streamlit as st
import google.generativeai as genai
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="J-Architect: Java AI Reviewer", layout="wide", page_icon="☕")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stCodeBlock { border: 1px solid #e0e0e0; border-left: 5px solid #007bff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE VALIDACIÓN (SIMULADA PERO TÉCNICA) ---
def validate_java_rules(code):
    """
    Simula un motor de análisis estático (tipo SonarQube/Checkstyle).
    Valida patrones de código limpio y arquitectura.
    """
    checks = {
        "Constructor Injection": (r"public\s+\w+\s*\([^)]*\w+\s+\w+\s*\)\s*\{", "Uso de inyección por constructor detectado (Buena práctica)."),
        "Custom Exception Handling": (r"catch\s*\(\s*(?!Exception|Throwable|Runtime)\w+\s+\w+\s*\)", "Manejo de excepciones específicas detectado."),
        "Quarkus/Lombok Optimization": (r"@Inject|@Data|@Builder|@ApplicationScoped", "Uso de anotaciones de productividad y scopes correctos."),
        "Avoid Field Injection": (r"@Autowired\s+private", "CRÍTICO: Se detectó inyección por campo (Mala práctica).", True), # True si es negativo
        "Hardcoded Secret Check": (r"[\"'][a-zA-Z0-9+/]{20,}[\"']", "ADVERTENCIA: Posible secreto o token hardcodeado.", True)
    }
    
    results = []
    for name, data in checks.items():
        pattern, message, *is_negative = data
        match = re.search(pattern, code)
        
        if is_negative and is_negative[0]:
            if match:
                results.append(f"❌ **{name}**: {message}")
            else:
                results.append(f"✅ **{name}**: No se detectaron problemas de este tipo.")
        else:
            if match:
                results.append(f"✅ **{name}**: {message}")
            else:
                results.append(f"⚠️ **{name}**: No se pudo verificar este estándar automáticamente.")
    return results

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# En local puedes usar st.sidebar.text_input para la clave, 
# en el deploy usaremos st.secrets
api_key = st.sidebar.text_input("Google API Key", type="password")

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
        )
    )
else:
    st.warning("Por favor, introduce tu Google API Key en la barra lateral para comenzar.")

# --- INTERFAZ DE USUARIO ---
st.title("☕ J-Architect")
st.subheader("Intelligent Code Reviewer for Java Ecosystem")
st.caption("AI-Powered Software Architecture Reviewer for Java Ecosystem")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("### 🔍 Input de Código")
    uploaded_file = st.file_uploader("Subir archivo .java, .yml, .properties", type=["java", "yml", "properties"])
    
    initial_code = ""
    if uploaded_file is not None:
        initial_code = uploaded_file.read().decode("utf-8")
        
    code_input = st.text_area("Código fuente:", value=initial_code, height=450, placeholder="Pega tu código aquí...")
    analyze_button = st.button("🚀 Analizar Arquitectura", type="primary", use_container_width=True)

with col2:
    st.markdown("### 📊 Resultado de Auditoría")
    if analyze_button and code_input:
        if not api_key:
            st.error("Introduce la API Key en la barra lateral.")
        else:
            with st.spinner("Auditando código..."):
                try:
                    response = model.generate_content(code_input).text
                    
                    # Parsing de secciones
                    diag_match = re.search(r"\[DIAGNOSTICO\](.*?)(?=\[REFACTOR\]|$)", response, re.S)
                    ref_match = re.search(r"\[REFACTOR\](.*?)(?=\[DEVOPS\]|$)", response, re.S)
                    dev_match = re.search(r"\[DEVOPS\](.*?)$", response, re.S)
                    
                    tab_diag, tab_refactor, tab_val, tab_dev = st.tabs(["📝 Diagnóstico", "🛠️ Refactor", "✅ Validación", "🚀 DevOps"])
                    
                    with tab_diag:
                        st.markdown(diag_match.group(1).strip() if diag_match else response)
                        
                    with tab_refactor:
                        if ref_match:
                            code_block = re.search(r"```java\s*(.*?)\s*```", ref_match.group(1), re.S)
                            clean_code = code_block.group(1) if code_block else ref_match.group(1).strip()
                            st.code(clean_code, language="java")
                            st.download_button("💾 Descargar Refactor", clean_code, file_name="RefactoredCode.java")
                        else:
                            st.warning("No se detectó bloque de refactorización.")
                            
                    with tab_val:
                        st.subheader("Análisis Estático de la Propuesta")
                        if ref_match and 'clean_code' in locals():
                            results = validate_java_rules(clean_code)
                            for r in results:
                                st.write(r)
                        else:
                            st.info("Esperando código refactorizado para validar.")
                            
                    with tab_dev:
                        st.markdown(dev_match.group(1).strip() if dev_match else "No hay recomendaciones DevOps.")
                        
                except Exception as e:
                    st.error(f"Error en el proceso: {e}")
    else:
        st.info("Carga código y presiona 'Analizar' para ver los resultados.")