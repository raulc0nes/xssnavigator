from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Ruta al ejecutable de ChromeDriver
chromedriver_path = '/usr/bin/chromedriver'

# Inicializa el servicio de ChromeDriver
service = Service(chromedriver_path)
service.start()

# Opciones de Chrome
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # Inicia el navegador maximizado

# Inicializa el navegador
driver = webdriver.Chrome(service=service, options=options)

# URL con marcador (*) para la inyección
target_url = 'http://testphp.vulnweb.com/search.php?test*=query'

# Lee los payloads desde el archivo
with open('/home/usuario/Descargas/xssnavigator/payloads.txt', 'r') as file:
    payloads = file.readlines()

try:
    for payload in payloads:
        # Elimina espacios en blanco al inicio y final de la línea
        payload = payload.strip()
        if payload:
            # Reemplaza el asterisco (*) con el payload
            url_with_payload = target_url.replace('*', payload)
            print(f"Probando URL: {url_with_payload}")  # Registro para debug

            # Navega a la URL con el payload inyectado
            driver.get(url_with_payload)

            # Espera hasta que el cuerpo de la página esté presente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # Espera un segundo para observar la página
            time.sleep(1)

finally:
    # Cierra el navegador y detiene el servicio
    driver.quit()
    service.stop()
