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
        model_name="gemini-1.5-flash",
        system_instruction=(
            "Actúa como un Principal Software Architect experto en Java, Spring Boot y Quarkus. "
            "Tu objetivo es analizar código para identificar deuda técnica, malas prácticas y antipatrones. "
            "Para Spring Boot, verifica inyección de dependencias, scopes y manejo de excepciones. "
            "Para Quarkus, prioriza la eficiencia para compilación nativa y extensiones correctas. "
            "Responde siempre de forma estructurada: 1. Diagnóstico, 2. Sugerencia de Mejora, 3. Código Refactorizado."
        )
    )
else:
    st.warning("Por favor, introduce tu Google API Key en la barra lateral para comenzar.")

# --- INTERFAZ DE USUARIO ---
st.title("☕ J-Architect")
st.subheader("Intelligent Code Reviewer for Java Ecosystem")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🔍 Input de Código o Archivos")
    framework = st.selectbox("Selecciona el Framework (opcional)", ["Autodetectar", "Java Nativo", "Spring Boot", "Quarkus"])
    
    code_input = st.text_area("Pega tu código Java aquí (Controller, Service, Pom.xml...)", height=400, placeholder="public class MyService { ... }")
    
    analyze_button = st.button("Analizar Código", type="primary")

with col2:
    st.markdown("### 📊 Resultado del Análisis")
    if analyze_button:
        if not api_key:
            st.error("Falta la API Key.")
        elif not code_input:
            st.error("El campo de código está vacío.")
        else:
            with st.spinner("El Arquitecto está revisando tu código..."):
                try:
                    # Construcción del prompt dinámico
                    prompt = f"Contexto detectado/seleccionado: {framework}\n\nAnaliza el siguiente código Java:\n\n{code_input}"
                    
                    response = model.generate_content(prompt)
                    
                    st.markdown(response.text)
                    
                    # Botón para descargar el resultado (opcional)
                    st.download_button("Descargar Reporte", response.text, file_name="analisis_jarchitect.md")
                except Exception as e:
                    st.error(f"Hubo un error con la IA: {e}")

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
st.sidebar.info("J-Architect v1.0 - Proyecto Integrador Máster IA")