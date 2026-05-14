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
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# En local puedes usar st.sidebar.text_input para la clave, 
# en el deploy usaremos st.secrets
api_key = st.sidebar.text_input("Google API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "Actúa como un Principal Software Architect experto en Java (Nativo, Spring Boot y Quarkus). "
            "Tu tarea es recibir código y devolver SIEMPRE tres secciones claramente marcadas:\n"
            "1. [DIAGNOSTICO]: Analiza deuda técnica y antipatrones.\n"
            "2. [REFACTOR]: Devuelve el código COMPLETO y corregido dentro de un bloque de código markdown (```java ... ```).\n"
            "3. [DEVOPS]: Sugiere configuración de Docker o CI/CD.\n"
            "Sé crítico con el rendimiento y la seguridad."
        )
    )
else:
    st.warning("Por favor, introduce tu Google API Key en la barra lateral para comenzar.")

# --- INTERFAZ DE USUARIO ---
st.title("☕ J-Architect")
st.subheader("Intelligent Code Reviewer for Java Ecosystem")

# Barra lateral para carga de archivos
st.sidebar.header("📂 Carga de Proyecto")
uploaded_file = st.sidebar.file_uploader("Sube archivo .java o pom.xml, properties", type=["java", "xml", "properties"])

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🔍 Input de Código")
    
    # Si hay un archivo subido, leemos su contenido
    initial_code = ""
    if uploaded_file is not None:
        initial_code = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Archivo cargado correctamente")

    code_input = st.text_area("Pega o edita el código Java:", 
                              value=initial_code, 
                              height=400, 
                              placeholder="public class MyService { ... }")
    
    analyze_button = st.button("🚀 Iniciar Auditoría de Arquitectura", type="primary")

with col2:
    st.markdown("### 📊 Resultado")
    
    if analyze_button and code_input:
        with st.spinner("El Arquitecto está trabajando..."):
            try:
                response = model.generate_content(f"Analiza este código:\n\n{code_input}").text
                
                # --- LÓGICA DE EXTRACCIÓN (PARSING) ---
                # Separamos por las etiquetas definidas en el system_instruction
                diag_part = re.search(r"\[DIAGNOSTICO\](.*?)(?=\[REFACTOR\]|$)", response, re.S)
                refactor_part = re.search(r"\[REFACTOR\](.*?)(?=\[DEVOPS\]|$)", response, re.S)
                devops_part = re.search(r"\[DEVOPS\](.*?)$", response, re.S)

                tab_diag, tab_refactor, tab_devops = st.tabs(["📝 Diagnóstico", "🛠️ Refactor", "🚀 DevOps"])

                with tab_diag:
                    if diag_part:
                        st.markdown(diag_part.group(1).strip())
                    else:
                        st.markdown(response) # Fallback si no detecta etiquetas

                with tab_refactor:
                    if refactor_part:
                        refactor_text = refactor_part.group(1).strip()
                        # Extraemos solo el bloque de código entre ```java ... ```
                        code_match = re.search(r"```java\s*(.*?)\s*```", refactor_text, re.S)
                        if code_match:
                            clean_code = code_match.group(1)
                            st.code(clean_code, language="java")
                            st.download_button("Descargar Código Refactorizado", clean_code, file_name="Refactored.java")
                        else:
                            st.markdown(refactor_text)
                    else:
                        st.warning("No se encontró una propuesta de refactorización específica.")

                with tab_devops:
                    if devops_part:
                        st.markdown(devops_part.group(1).strip())

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Carga código para ver el análisis.")

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
st.sidebar.info("J-Architect v1.0 - Proyecto Integrador Máster IA")