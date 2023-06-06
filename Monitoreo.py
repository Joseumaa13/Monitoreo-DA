import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import datetime


# Configuración de la página.
st.set_page_config(page_title="MONITOREO DIRECCIÓN DE AGUA",
                   layout="wide", 
                   initial_sidebar_state= "auto")

# Logos
# insertar imagen
image = Image.open('images/Imagen1.png')
image1 = Image.open('images/Imagen2.png')
st.image([image, image1],width=300)


# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
st.title('Sistema De Monitoreo De Aguas Subterráneas En Tiempo Real, SIMASTIR')
st.header('**Esta aplicación presenta visualizaciones gráficas de aprovechamiento y profundidad**')
st.markdown('**El usuario debe seleccionar un archivo CSV**')
st.markdown('**La aplicación muestra un conjunto de tablas y gráficos**')

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

# Renombrar columnas
    sn = sn.rename(columns={"RECORD_DATE": "Fecha", "RECORD_TIME": "Hora", "ID_DEVICE_LOG": "ID", "SITE": "Sitio", "ACUIFERO": "Acuifero", "LEVEL_DEPTH_M" : "Profundidad del nivel de agua (m)", "ACTUAL_CONDUCT_US_CM": "Conductividad electrica específica (µS/cm)"})

# Concatenar las columnas de Fecha y Hora. Creación de una columna única.
    sn['Fecha_Hora'] = pd.to_datetime(sn['Fecha'].astype(str) + ' ' + sn['Hora'].astype(str))
    sn.set_index('Fecha_Hora', inplace=True)
    sn.drop(['Fecha', 'Hora'], axis=1, inplace=True)

# Se obtiene valores de SITE, uno sólo para el nombre
    sitios = ", ".join(sn['Sitio'].unique())
# Se obtiene valores de ACUIFERO, uno sólo para el nombre
    acuiferos = ", ".join(sn['Acuifero'].unique())
# Obtener la fecha actual
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")
# SALIDAS
# Creación del gráfico dinámico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sn.index, y=sn['Profundidad del nivel de agua (m)'],
                     mode='lines', name='Profundidad del nivel de agua (m)',
                     visible=True, line=dict(color='#6fa8dc'),
                     hovertemplate="Fecha: %{x|%d-%m}<br>Hora: %{x|%H:%M}<br>Valor: %{y} m"))

# Verificar si hay valores en la columna 'Conductividad electrica específica (µS/cm)'
    if 'Conductividad electrica específica (µS/cm)' in sn.columns and not sn['Conductividad electrica específica (µS/cm)'].isnull().all():
    # Agregar la línea de conductividad eléctrica
        fig.add_trace(go.Scatter(x=sn.index, y=sn['Conductividad electrica específica (µS/cm)'],
                     mode='lines', name='Conductividad eléctrica (µS/cm)',
                     visible=True, yaxis='y2', line=dict(color='#FF6100'),
                     hovertemplate="Fecha: %{x|%d-%m}<br>Hora: %{x|%H:%M}<br>Valor: %{y} µS/cm"))


 # Configuración adicional del gráfico
    fig.update_layout(
        title=f'COMPORTAMIENTO HISTÓRICO DE LAS VARIACIONES DE NIVEL Y CONDUCTIVIDAD ESPECÍFICA, POZO: {sitios}, ACUÍFERO: {acuiferos}',
        font_size=(12.5),
        xaxis=dict(title='Registro Histórico', tickformat='%B-%Y', dtick='M1', tickmode='auto'),
        yaxis=dict(title='Profundidad nivel de agua (m)', side='left',  title_font=dict(color='#6fa8dc')),
        yaxis2=dict(title='Conductividad eléctrica (µS/cm)', side='right', overlaying='y', title_font=dict(color='#FF6100')),
        xaxis_tickangle=-90,
        showlegend=True,
        legend=dict(
        yanchor="top",
        y=0.715,
        xanchor="right",
        x=1.25),
        hovermode='x',
        height=900,
        width=1350
    )

    fig.add_layout_image(
        source=image,
        xref="paper",
        yref="paper",
        x=1.13,  # Ajusta la posición horizontal de la imagen
        y=0.95,  # Ajusta la posición vertical de la imagen
        sizex=0.13,  # Ajusta el tamaño horizontal de la imagen
        sizey=0.13,  # Ajusta el tamaño vertical de la imagen
        xanchor="right",  # Ancla horizontalmente la imagen a la derecha
        yanchor="middle"  # Ancla verticalmente la imagen al centro
)  
    fig.add_layout_image(
        source=image1,
        xref="paper",
        yref="paper",
        x=1.26,  # Ajusta la posición horizontal de la imagen
        y=0.95,  # Ajusta la posición vertical de la imagen
        sizex=0.13,  # Ajusta el tamaño horizontal de la imagen
        sizey=0.13,  # Ajusta el tamaño vertical de la imagen
        xanchor="right",  # Ancla horizontalmente la imagen a la derecha
        yanchor="middle"  # Ancla verticalmente la imagen al centro
)  
# Agregar texto independiente al lado del gráfico
    fig.add_annotation(
        text='<b style="font-size:12.5px">SISTEMA DE MONITOREO DE AGUAS<br>SUBTERRÁNEAS EN TIEMPO REAL, SIMASTIR</b>',
        xref='paper', yref='paper', x=1.26, y=0.88, showarrow=False,
        align='center',
        bordercolor='black', borderwidth=1,
        bgcolor='white')

    fig.add_annotation(
        text='<b style="font-size:12.5px">COMPORTAMIENTO HISTÓRICO DE LAS<br>VARIACIONES DE NIVEL Y<br> CONDUCTIVIDAD ESPECÍFICA</b>',
        xref='paper', yref='paper', x=1.245, y=0.80, showarrow=False,
        align='center',
        bordercolor='black', borderwidth=1,
        bgcolor='white')
# Agregar texto independiente al lado del gráfico
    fig.add_annotation(
        text=f'<b style="font-size:12.5px">POZO:{sitios}, <br>ACUÍFERO: {acuiferos} </b>',
        xref='paper', yref='paper', x=1.20, y=0.50, showarrow=False,
        align='center',
        bordercolor='black', borderwidth=1,
        bgcolor='white')     
# Agregar texto independiente al lado del gráfico 
    fig.add_annotation(
        text='<b style="font-size:12.5px">Equipo de monitoreo financiado con el<br>Canon de Aprovechamiento de<br>Agua',
        xref='paper', yref='paper', x=1.245, y=0.25, showarrow=False,
        align='center',
        bordercolor='black', borderwidth=1,
        bgcolor='white') 
# Agregar texto independiente al lado del gráfico 
    fig.add_annotation(
        text=f'<b style="font-size:12.5px">Actualizado al: {fecha_actual}',
        xref='paper', yref='paper', x=1.22, y=0.20, showarrow=False,
        align='center',
        bordercolor='black', borderwidth=1,
        bgcolor='white')

# Mostrar el gráfico dinámico
    st.plotly_chart(fig)

file2 = st.file_uploader('Seleccione un archivo CSV correspondiente estación meteorológica')
if file2 is not None:
# Carga de datos en un dataframe
        sn = pd.read_csv(file2, sep = ";")
# Dar formatos de fecha y hora a las columnas RECORD_DATE y RECORD_TIME
        sn['mes-año'] = pd.to_datetime(sn['mes-año'],format="%d/%m/%Y")
# Depuración de los datos
        sn['Acum_mensual'] = pd.to_numeric(sn['Acum_mensual'].str.replace(',', '.'), errors='coerce')
        sn['Prom_mensual'] = pd.to_numeric(sn['Prom_mensual'].str.replace(',', '.'), errors='coerce')

# Eliminar filas con NaN en las columnas
        sn['Acum_mensual'] = sn['Acum_mensual'].fillna(0)
        sn['Prom_mensual'] = sn['Prom_mensual'].fillna(0)

# Tabla de archivos csv
        st.header('Precipitación mensual y acumulada')
        sn_table = sn[["mes-año", "Acum_mensual", "Prom_mensual"]].copy()
        sn_table['mes-año'] = sn_table['mes-año'].dt.strftime('%Y-%m-%d')
        st.dataframe(sn_table)

# SALIDAS
# Crear el dataframe unicamente con estas columna y renombrar
        sn = sn.rename(columns={"mes-año": "Mes y Año", "Acum_mensual": "Precipitación acumulada mensual (mm)", "Prom_mensual": "Precipitación promedio mensual (mm)"})
        sn['Mes y Año'] = sn['Mes y Año'].dt.strftime('%b/%Y')
# SALIDAS
# Creación del gráfico dinámico
        fig = go.Figure()

        traces = ['Precipitación acumulada mensual (mm)', 'Precipitación promedio mensual (mm)']

        for trace in traces:
            fig.add_trace(go.Scatter(x=sn['Mes y Año'], y=sn[trace], 
                                 mode='lines', name=trace, 
                                 visible=True, line=dict(color='#6fa8dc') if trace == 'Precipitación acumulada mensual (mm)' else dict(color='#FF6100'),
                                 hovertemplate="Fecha: %{x}<br>Valor: %{y} mm"))

# Configuración adicional del gráfico
        fig.update_layout(
                    title='Precipitacion',
                    xaxis=dict(title='Año', tickformat='%B-%Y', tickmode='auto', nticks=20, rangeslider=dict(visible=False)),
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