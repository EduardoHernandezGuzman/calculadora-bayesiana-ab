import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np  # Añade esta línea
import io
from contextlib import redirect_stdout
from calculadora_bayesiana import CalculadoraClicksBayesiana

# Configuración de la página
st.set_page_config(
page_title="Calculadora Bayesiana A/B",
page_icon="📊",
layout="wide",
initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E88E5;
}
.sub-header {
    font-size: 1.5rem;
    color: #424242;
}
.success-box {
    background-color: #E8F5E9;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 0.5rem solid #4CAF50;
}
.info-box {
    background-color: #E3F2FD;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 0.5rem solid #2196F3;
}
</style>
""", unsafe_allow_html=True)

# Título y descripción
st.markdown('<p class="main-header">Calculadora Bayesiana para Tests A/B</p>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
Esta herramienta te permite analizar los resultados de tus pruebas A/B utilizando estadística bayesiana.
Sube un archivo CSV con tus datos o ingresa la información manualmente.
</div>
""", unsafe_allow_html=True)

# Inicializar la calculadora en el estado de la sesión
if 'calculadora' not in st.session_state:
    st.session_state.calculadora = CalculadoraClicksBayesiana()
    st.session_state.datos_procesados = False

# Sidebar con información y opciones
with st.sidebar:
    st.markdown('<p class="sub-header">Información</p>', unsafe_allow_html=True)
    st.info("""
    **¿Cómo funciona?**

    Esta calculadora utiliza estadística bayesiana para determinar cuál de las dos versiones (A o B) tiene mejor rendimiento.

    A diferencia de los tests A/B tradicionales, el enfoque bayesiano:
    - Proporciona probabilidades directas
    - Actualiza continuamente las estimaciones
    - Permite tomar decisiones con menos datos
    """)

    st.markdown('<p class="sub-header">Configuración</p>', unsafe_allow_html=True)

    # Opciones de configuración
    umbral_prob = st.slider(
        "Umbral de probabilidad para decisión", 
        min_value=0.8, 
        max_value=0.99, 
        value=0.95, 
        step=0.01,
        format="%.2f"
    )

    umbral_mejora = st.slider(
        "Umbral de mejora mínima", 
        min_value=0.01, 
        max_value=0.20, 
        value=0.01, 
        step=0.01,
        format="%.2f"
    )

    # Botón para reiniciar
    if st.button("Reiniciar calculadora"):
        st.session_state.calculadora = CalculadoraClicksBayesiana()
        st.session_state.datos_procesados = False
        st.success("Calculadora reiniciada correctamente")

# Pestañas para diferentes métodos de entrada
tab1, tab2, tab3 = st.tabs(["📊 Cargar CSV", "✏️ Entrada manual", "📋 Formato CSV"])

# Pestaña de carga de CSV (simplificada)
with tab1:
   st.markdown('<p class="sub-header">Cargar datos desde CSV</p>', unsafe_allow_html=True)
   
   st.info("💡 Si no sabes cómo preparar tu archivo CSV, revisa la pestaña **'Formato CSV'** para ver los requisitos.")
   
   # Subida del archivo
   uploaded_file = st.file_uploader(
       "Selecciona tu archivo CSV", 
       type=["csv"],
       help="El archivo debe seguir el formato especificado en la pestaña 'Formato CSV'"
   )
   
   if uploaded_file is not None:
       try:
           df = pd.read_csv(uploaded_file)
           
           # Validar las columnas requeridas
           columnas_requeridas = ['Día', 'Conversiones A', 'Visitas A', 'Conversiones B', 'Visitas B']
           columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
           
           if columnas_faltantes:
               st.error(f"❌ Faltan las siguientes columnas en tu CSV: {', '.join(columnas_faltantes)}")
               st.info("Por favor, revisa los requisitos en la pestaña **'Formato CSV'** y ajusta tu archivo.")
           else:
               st.success("✅ ¡Archivo cargado correctamente!")
               
               # Mostrar vista previa de los datos
               st.subheader("Vista previa de tus datos:")
               st.dataframe(df, use_container_width=True)
               
               # Mostrar estadísticas rápidas
               col1, col2, col3 = st.columns(3)
               with col1:
                   st.metric("Días de datos", len(df))
               with col2:
                   total_visitas_a = df['Visitas A'].sum()
                   total_conversiones_a = df['Conversiones A'].sum()
                   tasa_promedio_a = total_conversiones_a / total_visitas_a if total_visitas_a > 0 else 0
                   st.metric("Tasa promedio A", f"{tasa_promedio_a:.2%}")
               with col3:
                   total_visitas_b = df['Visitas B'].sum()
                   total_conversiones_b = df['Conversiones B'].sum()
                   tasa_promedio_b = total_conversiones_b / total_visitas_b if total_visitas_b > 0 else 0
                   st.metric("Tasa promedio B", f"{tasa_promedio_b:.2%}")
               
               # Botón para procesar
               if st.button("🚀 Procesar datos del CSV", type="primary"):
                   calculadora = st.session_state.calculadora

                   with st.spinner("Por favor ten paciencia mientras se cargan los datos..."):
                       # Barra de progreso mejorada
                       progress_text = "Procesando datos del test A/B..."
                       progress_bar = st.progress(0, text=progress_text)
                       total_rows = len(df)
                       
                       # Procesar cada fila del CSV
                       for i, row in df.iterrows():
                           dia = f"Día {int(row['Día'])}"
                           clicks_a = int(row['Conversiones A'])
                           visitas_a = int(row['Visitas A'])
                           clicks_b = int(row['Conversiones B'])
                           visitas_b = int(row['Visitas B'])
                           calculadora.actualizar_con_datos(clicks_a, visitas_a, clicks_b, visitas_b, dia=dia)
                           
                           # Actualizar barra de progreso
                           current_progress = (i + 1) / total_rows
                           progress_bar.progress(current_progress, text=f"Procesando día {i+1} de {total_rows}... ({int(current_progress*100)}%)")
                       
                       st.session_state.datos_procesados = True
                       st.markdown('<div class="success-box">¡Datos procesados correctamente! Ve a la sección de resultados para ver el análisis.</div>', unsafe_allow_html=True)
       
       except Exception as e:
           st.error(f"❌ Error al procesar el archivo: {e}")
           st.info("Verifica que tu archivo siga el formato CSV correcto (pestaña 'Formato CSV') y que todos los datos sean números válidos.")

# Pestaña de entrada manual
with tab2:
   st.markdown('<p class="sub-header">Entrada manual de datos</p>', unsafe_allow_html=True)
   
   with st.form("entrada_manual"):
       col1, col2 = st.columns(2)
       
       with col1:
           st.subheader("Grupo A")
           clicks_a = st.number_input("Conversiones A", min_value=0, value=0)
           visitas_a = st.number_input("Visitas A", min_value=1, value=100)
           tasa_a = clicks_a / visitas_a if visitas_a > 0 else 0
           st.metric("Tasa de conversión A", f"{tasa_a:.2%}")
       
       with col2:
           st.subheader("Grupo B")
           clicks_b = st.number_input("Conversiones B", min_value=0, value=0)
           visitas_b = st.number_input("Visitas B", min_value=1, value=100)
           tasa_b = clicks_b / visitas_b if visitas_b > 0 else 0
           st.metric("Tasa de conversión B", f"{tasa_b:.2%}")
       
       dia = st.text_input("Etiqueta del día (opcional)", value="Día 1")
       
       submitted = st.form_submit_button("Añadir datos")
       
       if submitted:
          with st.spinner("Por favor ten paciencia mientras se procesan los datos..."):
              calculadora = st.session_state.calculadora
              calculadora.actualizar_con_datos(clicks_a, visitas_a, clicks_b, visitas_b, dia=dia)
              st.session_state.datos_procesados = True
              st.markdown(f'<div class="success-box">Datos del {dia} añadidos correctamente</div>', unsafe_allow_html=True)

# Nueva pestaña para el formato CSV
with tab3:
   st.markdown('<p class="sub-header">Cómo preparar tu archivo CSV</p>', unsafe_allow_html=True)
   
   # Requisitos del CSV
   st.markdown("""
   ### 📋 Formato requerido
   
   Tu archivo CSV debe contener **exactamente** estas 5 columnas con estos nombres:
   """)
   
   # Tabla de requisitos
   requisitos_df = pd.DataFrame({
       'Columna': ['Día', 'Conversiones A', 'Visitas A', 'Conversiones B', 'Visitas B'],
       'Descripción': [
           'Identificador del período (número o texto)',
           'Número de conversiones del grupo A',
           'Número total de visitas del grupo A', 
           'Número de conversiones del grupo B',
           'Número total de visitas del grupo B'
       ],
       'Ejemplo': ['1, 2, 3... o "Lunes", "Martes"...', '13, 29, 28...', '188, 254, 207...', '21, 14, 22...', '181, 176, 173...']
   })
   
   st.dataframe(requisitos_df, use_container_width=True, hide_index=True)
   
   # Ejemplo de archivo CSV
   st.markdown("""
   ### 📄 Ejemplo de archivo CSV válido:
   """)
   
   ejemplo_csv_texto = """Día,Conversiones A,Visitas A,Conversiones B,Visitas B
1,13,188,21,181
2,29,254,14,176
3,28,207,22,173
4,35,312,41,298
5,22,189,28,201"""
   
   st.code(ejemplo_csv_texto, language="csv")
   
   # Consejos
   col1, col2 = st.columns(2)
   
   with col1:
       st.markdown("""
       ### ✅ Consejos importantes:
       - Usa comas (`,`) como separador
       - No incluyas espacios extra en los nombres de las columnas
       - Asegúrate de que los números no contengan puntos de miles
       - Cada fila representa un día/período de tu experimento
       - Guarda el archivo con extensión `.csv`
       """)
   
   with col2:
       st.markdown("""
       ### 🛠️ Cómo crear el archivo:
       
       **En Excel/Google Sheets:**
       1. Crea las columnas como se muestra arriba
       2. Introduce tus datos
       3. Guarda como CSV 
       
       **En un editor de texto:**
       1. Copia el ejemplo de arriba
       2. Reemplaza con tus datos
       3. Guárdalo como `mi_test_ab.csv`
       """)

# Mostrar resultados si hay datos procesados
if st.session_state.datos_procesados:
    st.markdown('<p class="main-header">Resultados del análisis</p>', unsafe_allow_html=True)

    # Pestañas para diferentes visualizaciones
res_tab1, res_tab2, res_tab3 = st.tabs(["📋 Resumen", "📝 Historial detallado", "📈 Gráficos"])

with res_tab1:
    # Mostrar resultado final
    resultado = st.session_state.calculadora.detectar_ganador(
        umbral_probabilidad=umbral_prob,
        umbral_mejora_minima=umbral_mejora
    )
    
    # Mostrar el resultado con formato
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Decisión final")
        if resultado["ganador"] == "A":
            st.success("🏆 El ganador es: Grupo A")
        elif resultado["ganador"] == "B":
            st.success("🏆 El ganador es: Grupo B")
        else:
            st.info("⚖️ No hay ganador claro todavía")
        
        st.write(f"**Recomendación:** {resultado['decision']}")
        st.write(f"**Razón:** {resultado['razon']}")
    
    with col2:
        if "probabilidad" in resultado:
            st.metric("Probabilidad", f"{resultado['probabilidad']:.2%}")
        elif "probabilidad_b_mejor" in resultado:
            st.metric("Probabilidad de que B sea mejor", f"{resultado['probabilidad_b_mejor']:.2%}")
        
        if "mejora_relativa" in resultado:
            st.metric("Mejora relativa", f"{resultado['mejora_relativa']:.2%}")
    
    # Mostrar último estado
    if len(st.session_state.calculadora.historial) > 0:
        ultimo = st.session_state.calculadora.historial[-1]
        
        st.subheader("Estado actual")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Grupo A**")
            mean_a = ultimo['alpha_a'] / ultimo['beta_a']
            st.metric("Tasa de conversión esperada", f"{mean_a:.4f}")
            st.write(f"Parámetros: alpha={ultimo['alpha_a']:.1f}, beta={ultimo['beta_a']:.1f}")
        
        with col2:
            st.write("**Grupo B**")
            mean_b = ultimo['alpha_b'] / ultimo['beta_b']
            st.metric("Tasa de conversión esperada", f"{mean_b:.4f}")
            st.write(f"Parámetros: alpha={ultimo['alpha_b']:.1f}, beta={ultimo['beta_b']:.1f}")

with res_tab2:
    # Capturar la salida de la función mostrar_historial_completo
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        st.session_state.calculadora.mostrar_historial_completo()
    
    # Mostrar la salida en Streamlit
    st.code(buffer.getvalue(), language="text")

with res_tab3:
 if len(st.session_state.calculadora.historial) > 0:
   st.subheader("Gráficos")
   
   # Crear selector de día
   dias_disponibles = [paso['dia'] for paso in st.session_state.calculadora.historial if 'dia' in paso]
   if len(dias_disponibles) > 1:  # Si hay más de un día (excluyendo "A priori")
       dia_seleccionado = st.selectbox("Selecciona un día para ver sus gráficos:", 
                                      dias_disponibles[1:],  # Excluir "A priori"
                                      index=len(dias_disponibles)-2)  # Seleccionar el último día por defecto
       
       # Encontrar el paso correspondiente al día seleccionado
       paso_seleccionado = None
       for paso in st.session_state.calculadora.historial:
           if 'dia' in paso and paso['dia'] == dia_seleccionado:
               paso_seleccionado = paso
               break
   else:
       paso_seleccionado = st.session_state.calculadora.historial[-1]
   
   # Mostrar gráficos del día seleccionado
   if paso_seleccionado and "trace" in paso_seleccionado:
       # Crear gráfico de distribuciones posteriores
       fig1, ax1 = plt.subplots(figsize=(10, 5))
       tasa_a_samples = paso_seleccionado['trace'].posterior['tasa_clicks_a'].values.flatten()
       tasa_b_samples = paso_seleccionado['trace'].posterior['tasa_clicks_b'].values.flatten()
       
       sns.kdeplot(tasa_a_samples, label="Grupo A", fill=True, ax=ax1)
       sns.kdeplot(tasa_b_samples, label="Grupo B", fill=True, ax=ax1)
       ax1.set_title(f"{paso_seleccionado['dia']} - Distribuciones posteriores")
       ax1.set_xlabel("Tasa de clicks por visita")
       ax1.legend()
       
       st.pyplot(fig1)
       
       # Crear gráfico de diferencia
       fig2, ax2 = plt.subplots(figsize=(10, 4))
       diff = paso_seleccionado['trace'].posterior['diferencia'].values.flatten()
       
       sns.kdeplot(diff, label="Diferencia (B - A)", color="purple", fill=True, ax=ax2)
       ax2.axvline(0, color="black", linestyle="--")
       ax2.set_title(f"{paso_seleccionado['dia']} - Diferencia de tasa de clicks")
       ax2.set_xlabel("Diferencia en clicks por visita")
       ax2.legend()
       
       st.pyplot(fig2)
       
       # Mostrar estadísticas del día seleccionado
       col1, col2 = st.columns(2)
       with col1:
           st.subheader(f"Estadísticas del {paso_seleccionado['dia']}")
           mean_a = paso_seleccionado['alpha_a'] / paso_seleccionado['beta_a']
           mean_b = paso_seleccionado['alpha_b'] / paso_seleccionado['beta_b']
           st.metric("Tasa de conversión A", f"{mean_a:.4f}")
           st.metric("Tasa de conversión B", f"{mean_b:.4f}")
       
       with col2:
           if "uplift" in paso_seleccionado:
               uplift = paso_seleccionado["uplift"]
               st.subheader("Uplift (B vs A)")
               st.metric("Media", f"{uplift['media']:.2%}")
               st.metric("IC 95%", f"[{uplift['ic_95'][0]:.2%}, {uplift['ic_95'][1]:.2%}]")
           
           prob_b_mejor = np.mean(diff > 0)
           st.metric("Probabilidad de que B > A", f"{prob_b_mejor:.2%}")
   
   # Mostrar gráfico de evolución si hay más de un día de datos
   if len(st.session_state.calculadora.historial) > 2:  # Más de 2 porque el primero es "A priori"
       st.subheader("Evolución de tasas de conversión")
       
       # Preparar datos para el gráfico de evolución
       dias = []
       tasas_a = []
       tasas_b = []
       
       for paso in st.session_state.calculadora.historial[1:]:  # Excluir "A priori"
           if 'dia' in paso:
               dias.append(paso['dia'])
               tasas_a.append(paso['alpha_a'] / paso['beta_a'])
               tasas_b.append(paso['alpha_b'] / paso['beta_b'])
       
       # Crear gráfico de evolución
       fig3, ax3 = plt.subplots(figsize=(10, 5))
       ax3.plot(dias, tasas_a, 'o-', label="Grupo A", color="blue")
       ax3.plot(dias, tasas_b, 'o-', label="Grupo B", color="orange")
       ax3.set_title("Evolución de tasas de conversión")
       ax3.set_xlabel("Día")
       ax3.set_ylabel("Tasa de conversión")
       ax3.legend()
       ax3.grid(True)
       plt.xticks(rotation=45)
       plt.tight_layout()
       
       st.pyplot(fig3)

# Pie de página
st.markdown("---")
st.markdown("""
<div style="text-align: center; background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-top: 20px;">
<p style="margin: 0; color: #555;">Idea y concepto: <strong>Claudia de la Cruz</strong> &nbsp;|&nbsp; Desarrollo: <strong>Pablo González</strong> &nbsp;|&nbsp; Desarrollo visual: <strong>Eduardo Hernández</strong></p>
</div>
""", unsafe_allow_html=True)