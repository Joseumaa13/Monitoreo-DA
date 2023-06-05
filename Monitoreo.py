import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image


# Configuración de la página.
st.set_page_config(page_title="MONITOREO DIRECCIÓN DE AGUA",
                   layout="wide", 
                   initial_sidebar_state= "auto",
                   menu_items={
                    'Get Help': 'https://www.extremelycoolapp.com/help',
                    'Report a bug': "https://www.extremelycoolapp.com/bug",
                    'About': "# This is a header. This is an *extremely* cool app!"})

# Logos
# insertar imagen
image = Image.open('images/Imagen1.png')
image1 = Image.open('images/Imagen2.png')
st.image([image, image1],width=350)


# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
st.title('Monitoreo')
st.markdown('Esta aplicación presenta visualizaciones gráficas de aprovechamiento, calidad y profundidad')
st.markdown('El usuario debe seleccionar un archivo CSV.')
st.markdown('La aplicación muestra un conjunto de tablas y gráficos.')

# Carga de datos
file1 = st.file_uploader('Seleccione un archivo CSV correspondiente al monitoreo')
# Se continúa con el procesamiento solo si hay un archivo de datos cargado
if file1 is not None:
# Carga de registros en un dataframe
    sn = pd.read_csv(file1, sep = ";")
# Dar formatos de fecha y hora a las columnas RECORD_DATE y RECORD_TIME
    sn['RECORD_DATE'] = pd.to_datetime(sn['RECORD_DATE'], dayfirst=True, format='%d/%m/%Y')
    sn['RECORD_TIME'] = pd.to_datetime(sn['RECORD_TIME'], format='%H:%M')
# Depuración de los datos
# Reemplazar valores que contienen punto por NaN
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].replace(r'^.*\..*$', float('nan'), regex=True)
# Convertir los valores restantes en la columna a string
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].astype(str)
# Reemplazar las comas por puntos
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].str.replace(',', '.')
# Convertir la columna a números de punto flotante
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].astype(float)
# Convertir los valores en 'Profundidad m' a negativos
    sn['LEVEL_DEPTH_M'] = -1 * sn['LEVEL_DEPTH_M']
# Reemplazar valores que contienen punto por NaN
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].replace(r'^.*\..*$', float('nan'), regex=True)
# Convertir los valores restantes en la columna a string
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].astype(str)
# Reemplazar las comas por puntos
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].str.replace(',', '.')
# Convertir la columna a números de punto flotante
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].astype(float)

# Eliminar filas con NaN en la columna
    sn = sn.dropna(subset=['LEVEL_DEPTH_M'])
# Crear datos para la tabla del CSV
# Se obtiene valores de SITE, uno sólo para el nombre
    sitios = ", ".join(sn['SITE'].unique())
# Se obtiene valores de ACUIFERO, uno sólo para el nombre
    acuiferos = ", ".join(sn['ACUIFERO'].unique())

# Nombre de la tabla según el sitio y acuífero.
    st.header(f'Valores correspondientes al sitio: {sitios}, Acuífero: {acuiferos}')
# Creación del dataframe para la tabla.
    st.dataframe(sn[["ID_DEVICE_LOG","ID_DEVICE_LOG_RECORDS","SITE","FECHA_DE_LA_MEDICION","HORA_DE_LA_MEDICION","ACUIFERO","REFERENCIA","PROPIETARIO","TIPO_DE_POZO","ACTUAL_CONDUCT_US_CM","DENSITY_OF_WATER_G_CM3","LEVEL_DEPTH_M","PRESSURE_MBAR","PRESSURE_MBAR_2","RESISTIVITY_OHM_CM","SALINITY_PSU","SENSOR_N","SENSOR_N_2","SPECIFIC_CONDUCT_US_CM","TEMPERATURE","TOT_DISS_SOLID_PPM","FECHA_INSERT_EN_BD","RECORD_DATE","RECORD_TIME"]])


# Crear el dataframe unicamente con estas columna
    sn = sn[["ID_DEVICE_LOG", "SITE", "ACUIFERO", "LEVEL_DEPTH_M", "RECORD_DATE", "RECORD_TIME", "ACTUAL_CONDUCT_US_CM"]]
# Eliminar valores nulos
# Verificar si la columna de conductividad tiene valores no nulos
    if 'ACTUAL_CONDUCT_US_CM' in sn.columns and sn['ACTUAL_CONDUCT_US_CM'].notnull().any():
# Eliminar filas con valores faltantes en la columna de conductividad
        sn = sn.dropna(subset=['ACTUAL_CONDUCT_US_CM)'])
# Renombrar columnas
    sn = sn.rename(columns={"RECORD_DATE": "Fecha", "RECORD_TIME": "Hora", "ID_DEVICE_LOG": "ID", "SITE": "Sitio", "ACUIFERO": "Acuifero", "LEVEL_DEPTH_M" : "Profundidad del nivel de agua (m)", "ACTUAL_CONDUCT_US_CM": "Conductividad electrica específica (µS/cm)"})
# Concatenar las columnas de Fecha y Hora. Creación de una columna unica.
    sn['Fecha_Hora'] = pd.to_datetime(sn['Fecha'].astype(str) + ' ' + sn['Hora'].astype(str))
    sn.set_index('Fecha_Hora', inplace=True)
    sn = sn.drop(['Fecha', 'Hora'], axis=1)
# Se obtiene valores de SITE, uno sólo para el nombre
    sitios = ", ".join(sn['Sitio'].unique())
# Se obtiene valores de ACUIFERO, uno sólo para el nombre
    acuiferos = ", ".join(sn['Acuifero'].unique())

# SALIDAS
# Creación del gráfico dinámico
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=sn.index, y=sn['Profundidad del nivel de agua (m)'], # Se selecciona el dato a gráficar.
                         mode='lines', name='Profundidad del nivel de agua (m)', # Tipo de gráfico y su etiqueta
                         visible=True, line=dict(color='#6fa8dc'), # Color de la línea
                         hovertemplate="Fecha: %{x|%d-%m}<br>Hora: %{x|%H:%M}<br>Valor: %{y} m"))# Aparece la etiqueta hover para el punto situado directamente debajo del cursor.


# Agregar la línea de conductividad eléctrica

    fig.add_trace(go.Scatter(x=sn.index, y=sn['Conductividad electrica específica (µS/cm)'], # Se selecciona el dato a gráficar.
                         mode='lines', name='Conductividad eléctrica (µS/cm)', # Tipo de gráfico y su etiqueta
                         visible=True, yaxis='y2', line=dict(color='#FF6100'), # Color de la línea y creación de eje secundario Y
                         hovertemplate="Fecha: %{x|%d-%m}<br>Hora: %{x|%H:%M}<br>Valor: %{y} µS/cm"))# Se selecciona el dato a gráficar.

# Configuración adicional del gráfico
    fig.update_layout(
                title=f'COMPORTAMIENTO HISTÓRICO DE LAS VARIACIONES DE NIVEL Y CONDUCTIVIDAD ESPECÍFICA, SITIO: {sitios}, ACUÍFERO: {acuiferos}', # Titulo del gráfico, con sitio y acuifero
                xaxis=dict(title='Registro Historico', tickformat='%B-%Y', dtick='M1', tickmode='auto', rangeslider=dict(visible=False)), # Etiqueta X, formato MES AÑO, etiqueta por mes, y automaticas, el rango slider desactivado
                yaxis=dict(title='Profundidad nivel de agua (m)', side='left'), # etiqueta y a la derecha
                yaxis2=dict(title='Conductividad eléctrica (µS/cm)', side='right', overlaying='y'), # etiqueta y a la izquierda, y que con superposición
                xaxis_tickangle=-90, # etiquetas del x en angulo de 90°
                showlegend=True, # que se muestra la leyenda, para activar y desactivar.
                hovermode='x', # ventanas emergentes
                height=900,  # Ajusta la altura de la figura en píxeles
                width=1300    # Ajusta el ancho de la figura en píxeles
                )       
# Mostrar el gráfico dinámico
    st.plotly_chart(fig)

file2 = st.file_uploader('Seleccione un archivo CSV correspondiente estación meteorológica')
if file2 is not None:
# Carga de datos en un dataframe
    sn = pd.read_csv(file2, sep = ";")
# Dar formatos de fecha y hora a las columnas RECORD_DATE y RECORD_TIME
sn['mes-año'] = pd.to_datetime(sn['mes-año'],format="%d/%m/%Y")
# Depuración de los datos
# Reemplazar valores que contienen punto por NaN
sn['Acum_mensual'] = sn['Acum_mensual'].replace(r'^.*\..*$', float('nan'), regex=True)
# Convertir los valores restantes en la columna a string
sn['Acum_mensual'] = sn['Acum_mensual'].astype(str)
# Reemplazar las comas por puntos
sn['Acum_mensual'] = sn['Acum_mensual'].str.replace(',', '.')
# Convertir la columna a números de punto flotante
sn['Acum_mensual'] = sn['Acum_mensual'].astype(float)
# Reemplazar valores que contienen punto por NaN
sn['Prom_mensual'] = sn['Prom_mensual'].replace(r'^.*\..*$', float('nan'), regex=True)
# Convertir los valores restantes en la columna a string
sn['Prom_mensual'] = sn['Prom_mensual'].astype(str)
# Reemplazar las comas por puntos
sn['Prom_mensual'] = sn['Prom_mensual'].str.replace(',', '.')
# Convertir la columna a números de punto flotante
sn['Prom_mensual'] = sn['Prom_mensual'].astype(float)

# Eliminar filas con NaN en la columna
sn = sn.dropna(subset=['Acum_mensual'])
# Eliminar filas con NaN en la columna
sn = sn.dropna(subset=['Prom_mensual'])

# Tabla de archivos csv
st.header('Valores')
st.dataframe(sn[["mes-año","Acum_mensual","Prom_mensual"]])

# SALIDAS
# Crear el dataframe unicamente con estas columna
sn = sn[["mes-año", "Acum_mensual", "Prom_mensual"]]
# Eliminar valores nulos
sn = sn.dropna()
# Renombrar columnas
sn = sn.rename(columns={"mes-año": "Mes y Año", "Acum_mensual": "Precipitación acumulada mensual (mm)", "Prom_mensual": "Precipitación promedio mensual (mm)"})

# SALIDAS
# Creación del gráfico dinámico
fig = go.Figure()

fig.add_trace(go.Scatter(x=sn["Mes y Año"].dt.strftime('%Y-%m'), y=sn['Precipitación acumulada mensual (mm)'], 
                         mode='lines', name='Precipitación acumulada mensual (mm)', 
                         visible=True, line=dict(color='#6fa8dc'), 
                         hovertemplate="Fecha: %{x|%b/%Y}<br>Valor: %{y} mm"))

fig.add_trace(go.Scatter(x=sn["Mes y Año"].dt.strftime('%Y-%m'), y=sn['Precipitación promedio mensual (mm)'], 
                         mode='lines', name='Precipitación promedio mensual (mm)', 
                         visible=True, yaxis='y2', line=dict(color='#FF6100'), 
                         hovertemplate="Fecha: %{x|%b/%Y}<br>Valor: %{y} mm"))


# Configuración adicional del gráfico
fig.update_layout(
        title='Precipitacion',
        xaxis=dict(title='Año', tickformat='%B-%Y', dtick='M1', tickmode='auto', rangeslider=dict(visible=False)),
        yaxis=dict(title='Precipitación acumulada mensual (mm)', side='left'),
        yaxis2=dict(title='Precipitación promedio mensual (mm)', side='right', overlaying='y'),
        xaxis_tickangle=-90,
        showlegend=True,
        hovermode='x',
        height=900,  # Ajusta la altura de la figura en píxeles
        width=1300    # Ajusta el ancho de la figura en píxeles
        )
# Mostrar el gráfico dinámico
st.plotly_chart(fig)