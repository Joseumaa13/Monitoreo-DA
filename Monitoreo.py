import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import datetime
from dateutil import parser

# Configuración de la página.
st.set_page_config(page_title="MONITOREO DIRECCIÓN DE AGUA",
                   layout="wide", 
                   initial_sidebar_state= "auto")
# Insertar imagenes para la página inicial y gráficos.
image = Image.open('images/Imagen1.png')
image1 = Image.open('images/Imagen2.png')
st.image([image, image1],width=300)

# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
st.title('Automatización del procesamiento de datos recolectados a través del Sistema de Monitoreo de Agua Subterránea en Tiempo Real (SIMASTIR).')
st.header('**Esta aplicación presenta visualizaciones gráficas de profundidad de agua y aprovechamiento.**')
st.markdown('**El usuario debe seleccionar un archivo CSV según los parámetros establecidos.**')
st.markdown('**La aplicación muestra un conjunto de tablas y gráficos.**')

# Carga de datos
file1 = st.file_uploader('Seleccione un archivo CSV correspondiente al monitoreo de SIMASTIR')
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
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].astype(str)
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].replace(r'^.*\..*$', float('nan'), regex=True)

# Reemplazar las comas por puntos y convertir la columna a números de punto flotante
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].astype(str)
    sn['LEVEL_DEPTH_M'] = sn['LEVEL_DEPTH_M'].str.replace(',', '.').astype(float)
    sn['ACTUAL_CONDUCT_US_CM'] = sn['ACTUAL_CONDUCT_US_CM'].str.replace(',', '.').astype(float)
# Convertir los valores en 'Profundidad m' a negativos
    sn['LEVEL_DEPTH_M'] = -1 * sn['LEVEL_DEPTH_M']

# Crear datos para la tabla del CSV
# Se obtiene valores de SITE y ACUIFERO
    sitios = ", ".join(sn['SITE'].unique())
    acuiferos = ", ".join(sn['ACUIFERO'].unique())

# Nombre de la tabla según el sitio y acuífero.
    st.header(f'Valores correspondientes al sitio: {sitios}, Acuífero: {acuiferos}')
# Creación del dataframe para la tabla.
    st.dataframe(sn[["ID_DEVICE_LOG",
                     "ID_DEVICE_LOG_RECORDS",
                     "SITE","FECHA_DE_LA_MEDICION",
                     "HORA_DE_LA_MEDICION","ACUIFERO",
                     "REFERENCIA","PROPIETARIO","TIPO_DE_POZO",
                     "ACTUAL_CONDUCT_US_CM","DENSITY_OF_WATER_G_CM3",
                     "LEVEL_DEPTH_M","PRESSURE_MBAR","PRESSURE_MBAR_2","RESISTIVITY_OHM_CM",
                     "SALINITY_PSU","SENSOR_N","SENSOR_N_2","SPECIFIC_CONDUCT_US_CM","TEMPERATURE",
                     "TOT_DISS_SOLID_PPM","FECHA_INSERT_EN_BD","RECORD_DATE","RECORD_TIME"]])
# Crear el dataframe unicamente con estas columna
    sn = sn[["ID_DEVICE_LOG", 
             "SITE", "ACUIFERO", 
             "LEVEL_DEPTH_M", "RECORD_DATE", 
             "RECORD_TIME", "ACTUAL_CONDUCT_US_CM"]]

# Renombrar columnas
    sn = sn.rename(columns={
         "RECORD_DATE": "Fecha", "RECORD_TIME": "Hora", 
         "ID_DEVICE_LOG": "ID", "SITE": "Sitio", 
         "ACUIFERO": "Acuifero", 
         "LEVEL_DEPTH_M" : "Profundidad del nivel de agua (m)", 
         "ACTUAL_CONDUCT_US_CM": "Conductividad electrica específica (µS/cm)"})

# Concatenar las columnas de Fecha y Hora. Creación de una columna única.
    sn['Fecha_Hora'] = pd.to_datetime(sn['Fecha'].astype(str) + ' ' + sn['Hora'].astype(str))
    sn.set_index('Fecha_Hora', inplace=True)
    sn.drop(['Fecha', 'Hora'], axis=1, inplace=True)

# Se obtiene valores de SITE, uno sólo para el nombre
    sitios = ", ".join(sn['Sitio'].unique())
    acuiferos = ", ".join(sn['Acuifero'].unique())
# Obtener la fecha actual
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

# SALIDAS
# Creación del gráfico dinámico
    fig = go.Figure()

    fig.add_trace(go.Scatter(
         x=sn.index,
         y=sn['Profundidad del nivel de agua (m)'],
         mode='lines', name='Profundidad del nivel de agua (m)',
         visible=True, line=dict(color='#6fa8dc'),
         hovertemplate="Fecha: %{x|%d-%m}<br>Hora: %{x|%H:%M}<br>Valor: %{y} m"))

# Verificar si hay valores en la columna 'Conductividad electrica específica (µS/cm)'
    if 'Conductividad electrica específica (µS/cm)' in sn.columns and not sn['Conductividad electrica específica (µS/cm)'].isnull().all():
        fig.add_trace(go.Scatter(
             x=sn.index,
             y=sn['Conductividad electrica específica (µS/cm)'],
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
        legend=dict(yanchor="top",y=0.715,xanchor="right",x=1.25),
        hovermode='x',
        height=900,
        width=1425,
        margin=dict(l=100, r=200, t=100, b=100)
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

file2 = st.file_uploader('Seleccione un archivo CSV correspondiente a la estación meteorológica')
if file2 is not None:
# Carga de datos en un dataframe
        sn = pd.read_csv(file2, sep = ";")
# Dar formatos de fecha y hora a las columnas RECORD_DATE y RECORD_TIME
        sn['mes-año'] = pd.to_datetime(sn['mes-año'],format="%d/%m/%Y")
# Depuración de los datos
        columnas_limpias = ['Acum_mensual', 'Prom_mensual']
        sn[columnas_limpias] = sn[columnas_limpias].apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce'))
# Eliminar filas con NaN en las columnas
        sn[columnas_limpias] = sn[columnas_limpias].fillna(0)

# Tabla de archivos csv
        st.header('Precipitación promedio mensual y acumulada')
        sn_table = sn[["mes-año", "Acum_mensual", "Prom_mensual"]].copy()
        sn_table['mes-año'] = sn_table['mes-año'].dt.strftime('%Y-%m-%d')
        st.dataframe(sn_table)

# SALIDAS
# Crear el dataframe unicamente con estas columna y renombrar
        sn = sn.rename(columns={
             "mes-año": "Mes y Año",
             "Acum_mensual": "Precipitación acumulada mensual (mm)", 
             "Prom_mensual": "Precipitación promedio mensual (mm)"})
        sn['Mes y Año'] = sn['Mes y Año'].dt.strftime('%b/%Y')
# SALIDAS
# Creación del gráfico dinámico
        fig = go.Figure()

        traces = ['Precipitación acumulada mensual (mm)', 'Precipitación promedio mensual (mm)']

        for trace in traces:
            color = '#6fa8dc' if trace == 'Precipitación acumulada mensual (mm)' else '#FF6100'
            fig.add_trace(go.Scatter(x=sn['Mes y Año'], y=sn[trace], 
                                 mode='lines', name=trace, 
                                 visible=True, line=dict(color=color),
                                 hovertemplate="Fecha: %{x}<br>Valor: %{y} mm"))

# Configuración adicional del gráfico
        fig.update_layout(
                    title='PRECIPITACIÓN PROMEDIO Y ACUMULADA MENSUAL',
                    font_size=(12.5),
                    xaxis=dict(title='Año', tickformat='%B-%Y', tickmode='auto', nticks=20, rangeslider=dict(visible=False)),
                    yaxis=dict(title='Precipitación acumulada mensual (mm)', side='left'),
                    yaxis2=dict(title='Precipitación promedio mensual (mm)', side='right', overlaying='y'),
                    xaxis_tickangle=-90,
                    showlegend=True,
                    legend=dict(yanchor="top",y=0.715,xanchor="right",x=1.28),
                    hovermode='x',
                    height=900,  # Ajusta la altura de la figura en píxeles
                    width=1300,
                    margin=dict(l=100, r=100, t=100, b=100)  # Ajusta el ancho de la figura en píxeles
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
            xref='paper', yref='paper', x=1.27, y=0.88, showarrow=False,
            align='center',
            bordercolor='black', borderwidth=1,
            bgcolor='white')

        fig.add_annotation(
            text='<b style="font-size:12.5px">ESTACIÓN CARTAGENA<br>INSTITUTO METEOROLÓGICO NACIONAL',
            xref='paper', yref='paper', x=1.260, y=0.80, showarrow=False,
            align='center',
            bordercolor='black', borderwidth=1,
            bgcolor='white')     
# Mostrar el gráfico dinámico
        st.plotly_chart(fig)


def filtrar_y_formatear_fechas(fechas):
    fechas_validas = []
    for fecha in fechas:
        fecha_sin_set = fecha.replace('set-21', '').strip()
        try:
            fecha_formateada = pd.to_datetime(fecha_sin_set, format="%d/%m/%Y").strftime("%b %Y")
            fechas_validas.append(fecha_formateada)
        except ValueError:
            continue
    return fechas_validas

file3 = st.file_uploader('Seleccione un archivo CSV correspondiente al monitoreo manual con valores dinámicos')
if file3 is not None:
# Carga de registros en un dataframe
            dn = pd.read_csv(file3, sep=";")
            dn
# Reemplazar comas por puntos en las columnas numéricas
            dn.iloc[:, 1:] = dn.iloc[:, 1:].replace(',', '.', regex=True).astype(float)

# Lista de etiquetas para seleccionar el gráfico
            etiquetas = []
            for i in dn.index:
                etiqueta = f"{dn.iloc[i, 0]}"
                etiquetas.append(etiqueta)

# Seleccionar el índice del gráfico mediante las etiquetas
            etiqueta_seleccionada = st.selectbox("Seleccione el gráfico a mostrar", etiquetas)

# Obtener el índice seleccionado
            i = etiquetas.index(etiqueta_seleccionada)
            fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

# Filtrar las fechas válidas y convertirlas al formato deseado
            fechas_validas = filtrar_y_formatear_fechas(dn.columns[1:])

# Se crea una nueva figura para el gráfico seleccionado
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fechas_validas,
                y=-dn.iloc[i, 1:][dn.columns[1:] != 'set-21'],  # Los valores son el resto de las columnas para esta fila
                mode='lines+markers',
                name=dn.iloc[i, 0],  # El nombre del gráfico es el valor de la primera columna
                hovertemplate='Fecha: %{x}<br>Valor: %{y} m',
    ))
            fig.update_layout(title=dn.iloc[i, 0],
                                height=700,
                                width=1400,
                                margin=dict(l=100, r=300, t=100, b=100),
                                xaxis_tickangle=-90,
                                legend=dict(yanchor="top",y=0.695,xanchor="right",x=1.20),
                                showlegend=True,
                                xaxis=dict(title="Registro Histórico",tickmode="auto",  # Ajuste automático de las etiquetas del eje x
                                nticks=10  # Especifica la cantidad deseada de etiquetas del eje x
        ))
            
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
# Se muestra el gráfico seleccionado
            st.plotly_chart(fig)

file4 = st.file_uploader('Seleccione un archivo CSV correspondiente al monitoreo manual con valores estáticos')
if file4 is not None:
# Carga de registros en un dataframe
            en = pd.read_csv(file4, sep=";")
            en
# Reemplazar comas por puntos en las columnas numéricas
            en.iloc[:, 1:] = en.iloc[:, 1:].replace(',', '.', regex=True).astype(float)

# Lista de etiquetas para seleccionar el gráfico
            etiquetas = []
            for i in en.index:
                etiqueta = f"{en.iloc[i, 0]}"
                etiquetas.append(etiqueta)

# Seleccionar el índice del gráfico mediante las etiquetas
            etiqueta_seleccionada = st.selectbox("Seleccione el gráfico a mostrar:", etiquetas)

# Obtener el índice seleccionado
            i = etiquetas.index(etiqueta_seleccionada)
            fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

# Filtrar las fechas válidas y convertirlas al formato deseado
            fechas_validas = filtrar_y_formatear_fechas(en.columns[1:])

# Se crea una nueva figura para el gráfico seleccionado
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fechas_validas,
                y=-en.iloc[i, 1:][en.columns[1:] != 'set-21'],  # Los valores son el resto de las columnas para esta fila
                mode='lines+markers',
                name=en.iloc[i, 0],  # El nombre del gráfico es el valor de la primera columna
                hovertemplate='Fecha: %{x}<br>Valor: %{y} m',
    ))
            fig.update_layout(title=en.iloc[i, 0],
                                height=700,
                                width=1400,
                                margin=dict(l=100, r=300, t=100, b=100),
                                xaxis_tickangle=-90,
                                legend=dict(yanchor="top",y=0.695,xanchor="right",x=1.20),
                                showlegend=True,
                                xaxis=dict(title="Registro Histórico",tickmode="auto",  # Ajuste automático de las etiquetas del eje x
                                nticks=10  # Especifica la cantidad deseada de etiquetas del eje x
        ))
            
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
# Se muestra el gráfico seleccionado
            st.plotly_chart(fig)