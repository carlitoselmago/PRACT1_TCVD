# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:47:21 2025

@author: miguel.herrera.p
"""

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Script para iniciar sesión en El País, recorrer enlaces de noticias guardados en un Excel,
extraer el texto de cada noticia y guardar el resultado en un nuevo archivo.
"""

# -*- coding: utf-8 -*-
"""
Script para iniciar sesión en El País, leer enlaces desde un archivo Excel
y guardar el texto completo de cada noticia en una nueva columna.
Optimizado para evitar repetir el cierre del banner de cookies.
"""

import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Configuración del WebDriver ----------
def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ---------- Cargar credenciales desde archivo ----------
def cargar_credenciales(path="credenciales.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- Cierra el banner de cookies si aparece ----------
def cerrar_banner_cookies(driver):
    selectores = [
        'button#didomi-notice-agree-button',
        'button[aria-label="Aceptar"]',
        'button.didomi-accept-button',
        'button[mode="primary"]'
    ]

    for selector in selectores:
        try:
            boton = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            boton.click()
            print("Banner de cookies cerrado")
            return
        except:
            continue

    print("No se pudo cerrar el banner de cookies")

# ---------- Iniciar sesión ----------
def iniciar_sesion_el_pais(driver, credenciales):
    driver.get("https://elpais.com/")
    cerrar_banner_cookies(driver)

    try:
        # Hacer clic en el botón "Iniciar sesión"
        iniciar_sesion_span = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Iniciar sesión")]'))
        )
        iniciar_sesion_span.click()
    except TimeoutException:
        print("No se encontró el botón 'Iniciar sesión'")
        return

    try:
        # Esperar a que aparezcan los campos de email y contraseña
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "subsEmail"))
        )
        driver.find_element(By.ID, "subsEmail").send_keys(credenciales["usuario"])
        driver.find_element(By.ID, "subsPassword").send_keys(credenciales["clave"])
        driver.find_element(By.ID, "subsSignIn").click()
    except Exception as e:
        print(f"Error al intentar iniciar sesión: {e}")
        return

    # Esperar a que desaparezca el botón de "Iniciar sesión" como señal de login exitoso
    try:
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Iniciar sesión")]'))
        )
        print("Sesión iniciada correctamente")
    except TimeoutException:
        print("No se logró verificar el inicio de sesión")

# ---------- Extraer texto de una noticia ----------
def extraer_texto_noticia(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        parrafos = driver.find_elements(By.CSS_SELECTOR, "article p")
        texto = "\n".join([p.text for p in parrafos])
        return texto.strip()
    except Exception:
        return ""

# ---------- Main ----------
def main():
    credenciales = cargar_credenciales("credenciales.json")
    driver = configurar_driver()

    df = pd.read_excel("noticias_excel.xlsx")
    if "Enlace" not in df.columns:
        raise KeyError("La columna 'Enlace' no se encuentra en el archivo Excel")

    # Abrir la página inicial para cerrar el banner de cookies y hacer login
    driver.get("https://elpais.com/")
    cerrar_banner_cookies(driver)
    iniciar_sesion_el_pais(driver, credenciales)

    textos = []

    for i, fila in df.iterrows():
        url = fila["Enlace"]
        print(f"Procesando noticia {i + 1}: {url}")
        try:
            driver.get(url)
            # Ya no se cierra el banner de cookies en cada iteración (optimización)
            texto = extraer_texto_noticia(driver)
            textos.append(texto)
        except Exception as e:
            print(f"Error al procesar {url}: {e}")
            textos.append("")
        time.sleep(2)  # Espera para evitar sobrecarga

    df["Texto"] = textos
    df.to_excel("noticias_con_texto.xlsx", index=False)
    print("Archivo guardado como 'noticias_con_texto.xlsx'")

    driver.quit()

if __name__ == "__main__":
    main()
