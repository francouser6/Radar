import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

def scrape_sbs():
    url = "https://www.sbs.gob.pe/app/pp/INT_CN/Paginas/Busqueda/BusquedaPortal.aspx"
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Verificar que la solicitud fue exitosa
        logging.info("Página web abierta con éxito.")
        
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Contenido cargado con éxito.")
        
        # Definir los selectores CSS para los datos
        rows = soup.select('table.rgMasterTable tbody tr')
        
        normas = []
        definiciones = []
        tipos = []
        fechas = []
        sistemas = []

        # Iterar sobre las filas
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:
                normas.append(cols[1].text.strip())
                definiciones.append(cols[3].text.strip())
                tipos.append(cols[4].text.strip())
                fechas.append(cols[7].text.strip())
                sistemas.append(cols[6].text.strip())

    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la solicitud HTTP: {e}")
        return None

    # Crear un DataFrame con los datos extraídos
    df = pd.DataFrame({
        'Norma': normas,
        'Definición': definiciones,
        'Tipo': tipos,
        'Fecha': fechas,
        'Sistema': sistemas
    })

    # Convertir la columna "Fecha" al formato de fecha
    df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d/%m/%Y", errors='coerce')

    # Rellenar valores en blanco con el valor de la siguiente fila
    df['Fecha'] = df['Fecha'].fillna(method='bfill')

    # Formatear la columna "Fecha" en el formato "dd/mm/yyyy"
    df['Fecha'] = df['Fecha'].dt.strftime("%d/%m/%Y")

    return df

# Crear la aplicación de Streamlit
import streamlit as st

st.title("Scraping SBS Data")
st.write("Esta aplicación extrae datos de la SBS y los muestra en un DataFrame.")

# Llamar a la función y mostrar el DataFrame
sbs = scrape_sbs()
if sbs is not None and not sbs.empty:
    st.dataframe(sbs)
else:
    st.write("No se pudo extraer los datos o el DataFrame está vacío.")


