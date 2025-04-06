# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:18:35 2025

@author: mahp4
"""

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==================== CONFIGURACIONES INICIALES ====================
base_url = "https://elpais.com/noticias/violencia-machista/"  # URL de inicio
excel_filename = "noticias_excel.xlsx"  # Archivo de salida
filtrar_por_anio = True  # Activar filtro por años
anios_filtrados = list(range(2015, 2025))  # Años a conservar

# ==================== CONFIGURACIÓN DE CHROME ====================
options = Options()
options.add_argument("--headless=new")  
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(base_url)

pagina = 0
total_noticias = 0
cookies_aceptadas = False
datos = []

# ==================== BUCLE PRINCIPAL ====================
while True:
    wait_time = random.uniform(2.5, 5.0)
    print(f"\nPágina {pagina} | Esperando {wait_time:.2f} segundos...")
    time.sleep(wait_time)

    # Aceptar cookies si no se ha hecho aún
    if not cookies_aceptadas:
        try:
            aceptar_btn = driver.find_element(By.CSS_SELECTOR, "button#didomi-notice-agree-button")
            aceptar_btn.click()
            print("Cookies aceptadas")
            cookies_aceptadas = True
            time.sleep(1.5)
        except:
            print("No se encontró el botón de cookies o ya está aceptado")

    current_url = driver.current_url

    # 1) Localizar TODOS los nodos article.c
    todos_los_articulos = driver.find_elements(By.CSS_SELECTOR, "article.c")
    
    # 2) Crear lista de artículos válidos
    valid_articulos = []
    for ar in todos_los_articulos:
        try:
            # Verificamos si contienen header.c_h h2 a (título) y div.c_a time (fecha)
            ar.find_element(By.CSS_SELECTOR, "header.c_h h2 a")
            ar.find_element(By.CSS_SELECTOR, "div.c_a time")
            valid_articulos.append(ar)
        except NoSuchElementException:
            # Si no tiene esos elementos, lo consideramos no válido (ej. publicidad o contenedor vacío)
            pass

    print(f"{len(valid_articulos)} artículos encontrados en esta página.")

    # Contador de cuántos artículos guardamos realmente en esta página
    articulos_en_esta_pagina = 0

    # ==================== PROCESAR SOLO LOS ARTÍCULOS VÁLIDOS ====================
    for articulo in valid_articulos:
        try:
            categoria_tag = articulo.find_element(By.CSS_SELECTOR, "header.c_h a.c_k")
            categoria = categoria_tag.text
            categoria_link = categoria_tag.get_attribute("href")
        except:
            categoria, categoria_link = "", ""

        try:
            titulo_tag = articulo.find_element(By.CSS_SELECTOR, "header.c_h h2 a")
            titulo = titulo_tag.text
            enlace = titulo_tag.get_attribute("href")
        except:
            titulo, enlace = "", ""

        try:
            imagen_tag = articulo.find_element(By.CSS_SELECTOR, "figure.c_m a")
            imagen_url = imagen_tag.get_attribute("href")
        except:
            imagen_url = ""

        try:
            resumen = articulo.find_element(By.CSS_SELECTOR, "p.c_d").text
        except:
            resumen = ""

        try:
            autor_tag = articulo.find_element(By.CSS_SELECTOR, "div.c_a a")
            autor = autor_tag.text
            autor_link = autor_tag.get_attribute("href")
        except:
            autor, autor_link = "", ""

        try:
            fecha = articulo.find_element(By.CSS_SELECTOR, "div.c_a time").get_attribute("datetime")
            año = int(fecha[:4]) if fecha else 0
        except:
            fecha, año = "", 0

        try:
            ciudad = articulo.find_element(By.CSS_SELECTOR, "span.c_a_l").text
        except:
            ciudad = ""

        # Guardar sólo si pasa el filtro de año (si está activado)
        if not filtrar_por_anio or (año in anios_filtrados):
            datos.append([
                titulo, enlace, categoria, categoria_link, autor, autor_link,
                fecha, ciudad, resumen, imagen_url, current_url
            ])
            total_noticias += 1
            articulos_en_esta_pagina += 1

    # Resumen de la página
    print(f"En la página {pagina}, se han GUARDADO {articulos_en_esta_pagina} artículos (acumulado total: {total_noticias}).")

    # ==================== NAVEGAR A SIGUIENTE PÁGINA ====================
    try:
        contenedor = driver.find_element(By.CSS_SELECTOR, "div.b-au_f")
        siguiente = contenedor.find_element(By.XPATH, ".//a[contains(text(), 'Siguiente')]")
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(1)
        driver.execute_script("arguments[0].click();", siguiente)
        pagina += 1
    except NoSuchElementException:
        print("Botón 'Siguiente' no encontrado. Fin del scraping.")
        break

# ==================== GUARDAR ARCHIVO EXCEL ====================
columnas = [
    "Título", "Enlace", "Categoría", "Enlace Categoría",
    "Autor", "Enlace Autor", "Fecha", "Ciudad", "Resumen", "Imagen", "URL Página"
]

df = pd.DataFrame(datos, columns=columnas)
df.to_excel(excel_filename, index=False)
print(f"\nProceso finalizado. Total de noticias: {total_noticias}")
print(f"Archivo guardado como: {excel_filename}")
