import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def scrape_sbs():
    url = "https://www.sbs.gob.pe/app/pp/INT_CN/Paginas/Busqueda/BusquedaPortal.aspx"
    service = EdgeService(EdgeChromiumDriverManager().install())
    options = Options()
    options.headless = False  # Ejecutar sin modo headless para depuración
    driver = webdriver.Edge(service=service, options=options)

    logging.basicConfig(level=logging.INFO)
    
    try:
        # Abrir la página web
        driver.get(url)
        logging.info("Página web abierta con éxito.")

        # Esperar explícitamente a que el contenido se cargue
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rgMasterTable"))
        )
        logging.info("Contenido cargado con éxito.")

        # Tomar una captura de pantalla para verificar el contenido cargado
        driver.save_screenshot('screenshot.png')
        logging.info("Captura de pantalla tomada.")

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
        rows = driver.find_elements(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_rdgUltimaVersionNormas_ctl00"]/tbody/tr')
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
                norma_element = driver.find_element(By.XPATH, norma_xpath)
                definicion_element = driver.find_element(By.XPATH, definicion_xpath)
                tipo_element = driver.find_element(By.XPATH, tipo_xpath)
                fecha_element = driver.find_element(By.XPATH, fecha_xpath)
                sistema_element = driver.find_element(By.XPATH, sistema_xpath)

                normas.append(norma_element.text.strip())
                definiciones.append(definicion_element.text.strip())
                tipos.append(tipo_element.text.strip())
                fechas.append(fecha_element.text.strip())
                sistemas.append(sistema_element.text.strip())
            except NoSuchElementException:
                logging.warning(f"Elemento no encontrado en la posición {i}.")
                continue

    except TimeoutException:
        logging.error("El contenido no se cargó a tiempo.")
        return None
    except WebDriverException as e:
        logging.error(f"Error del WebDriver: {e}")
        return None
    finally:
        # Cerrar el navegador
        driver.quit()
        logging.info("Navegador cerrado.")

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

# Llamar a la función y mostrar el DataFrame
sbs = scrape_sbs()
if sbs is not None:
    print(sbs)
else:
    print("No se pudo extraer los datos.")
