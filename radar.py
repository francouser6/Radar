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
        
        # Definir las rutas XPath para los datos
        norma_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[2]'
        definicion_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[4]'
        tipo_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[5]'
        fecha_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[8]'
        sistema_xpath_template = '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00__{}"]/td[7]'

        normas = []
        definiciones = []
        tipos = []
        fechas = []
        sistemas = []

        # Obtener el número de filas dinámicamente
        rows = soup.select('table.rgMasterTable tbody tr')
        num_rows = len(rows)

        # Iterar sobre las filas
        for i in range(num_rows):
            try:
                norma_xpath = norma_xpath_template.format(i)
                definicion_xpath = definicion_xpath_template.format(i)
                tipo_xpath = tipo_xpath_template.format(i)
                fecha_xpath = fecha_xpath_template.format(i)
                sistema_xpath = sistema_xpath_template.format(i)

                # Extraer los datos
                norma_element = soup.select_one(f'xpath:{norma_xpath}')
                definicion_element = soup.select_one(f'xpath:{definicion_xpath}')
                tipo_element = soup.select_one(f'xpath:{tipo_xpath}')
                fecha_element = soup.select_one(f'xpath:{fecha_xpath}')
                sistema_element = soup.select_one(f'xpath:{sistema_xpath}')

                normas.append(norma_element.text.strip() if norma_element else '')
                definiciones.append(definicion_element.text.strip() if definicion_element else '')
                tipos.append(tipo_element.text.strip() if tipo_element else '')
                fechas.append(fecha_element.text.strip() if fecha_element else '')
                sistemas.append(sistema_element.text.strip() if sistema_element else '')
            except Exception as e:
                logging.warning(f"Error al extraer datos en la posición {i}: {e}")
                continue

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
if sbs is not None:
    st.dataframe(sbs)
else:
    st.write("No se pudo extraer los datos.")

