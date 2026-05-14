import streamlit as st
import google.generativeai as genai
import os

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
            "Actúa como un Principal Software Architect experto en Java, Spring Boot y Quarkus. "
            "Tu objetivo es analizar código para identificar deuda técnica, malas prácticas y antipatrones; revisiones profundas de buenas prácticas"
            "IMPORTANTE: Debes separar tu respuesta SIEMPRE con estos delimitadores para que yo pueda procesarlos:\n"
            "##DIAGNOSTICO## para el análisis de deuda y antipatrones.\n"
            "##REFACTOR## para el código sugerido.\n"
            "##DEVOPS## para configuraciones de Docker o CI/CD."
        )
    )
else:
    st.warning("Por favor, introduce tu Google API Key en la barra lateral para comenzar.")

# --- INTERFAZ DE USUARIO ---
st.title("☕ J-Architect")
st.subheader("Intelligent Code Reviewer for Java Ecosystem")

# Barra lateral para carga de archivos
st.sidebar.header("📂 Carga de Proyecto")
uploaded_file = st.sidebar.file_uploader("Sube un archivo .java o pom.xml", type=["java", "xml", "properties"])

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
    st.markdown("### 📊 Resultado del Análisis")
    
    if analyze_button and code_input:
        with st.spinner("Analizando arquitectura..."):
            try:
                prompt = f"Analiza el siguiente código y genera el reporte estructurado:\n\n{code_input}"
                response = model.generate_content(prompt).text
                
                # Creación de Tabs
                tab_diag, tab_refactor, tab_devops = st.tabs([
                    "📝 Diagnóstico de Deuda", 
                    "🛠️ Código Refactorizado", 
                    "🚀 DevOps & Deploy"
                ])

                # Lógica simple para repartir el contenido (si la IA sigue los delimitadores)
                parts = response.split("##")
                
                with tab_diag:
                    st.info("Resumen de hallazgos y antipatrones detectados.")
                    # Si la IA usó los delimitadores, mostramos esa parte, si no, mostramos todo
                    st.markdown(response) 
                
                with tab_refactor:
                    st.success("Propuesta de código limpio y optimizado.")
                    # Aquí podrías usar lógica de búsqueda de strings para separar el código
                    st.code(code_input, language="java") # Placeholder, la IA dará el nuevo
                
                with tab_devops:
                    st.warning("Configuración recomendada para Docker/Kubernetes.")
                    st.markdown("Generando archivo `Dockerfile` optimizado...")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Ingresa código o sube un archivo y presiona 'Iniciar Auditoría'.")

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
st.sidebar.info("J-Architect v1.0 - Proyecto Integrador Máster IA")