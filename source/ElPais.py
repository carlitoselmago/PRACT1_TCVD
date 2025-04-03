# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 09:18:35 2025

@author: mahp4
"""

import time
import csv
import random
import os
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==================== CONFIGURACIONES INICIALES ====================
base_url = "https://elpais.com/noticias/violencia-machista/"  # URL base de inicio
csv_filename = "noticias.csv"  # Nombre del archivo CSV de salida
write_header = not os.path.exists(csv_filename)  # Escribir encabezado solo si el archivo no existe
filtrar_por_anio = True  # Cambia a False para desactivar el filtro por año
anio_filtrado = 2024

# ==================== CONFIGURACIÓN DE CHROME ====================
options = Options()
# options.add_argument("--headless=new")  # Descomenta para ejecución en segundo plano
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Inicializar el navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(base_url)
pagina = 0
total_noticias = 0
cookies_aceptadas = False

# ==================== ABRIR CSV ====================
with open(csv_filename, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow([
            "Título", "Enlace", "Categoría", "Enlace Categoría",
            "Autor", "Enlace Autor", "Fecha", "Ciudad", "Resumen", "Imagen", "URL Página"
        ])

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
        articulos = driver.find_elements(By.CSS_SELECTOR, "article.c")
        print(f"{len(articulos)} artículos encontrados en la página {pagina}")
        ultimo_titulo = ""

        # ==================== PROCESAR ARTÍCULOS ====================
        for articulo in articulos:
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
                ultimo_titulo = titulo
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

            # Guardar según filtro de año (si aplica)
            if not filtrar_por_anio or año == anio_filtrado:
                writer.writerow([
                    titulo, enlace, categoria, categoria_link, autor, autor_link,
                    fecha, ciudad, resumen, imagen_url, current_url
                ])
                total_noticias += 1

        print(f"Total acumulado: {total_noticias} noticias. Último título: {ultimo_titulo[:70]}")

        # ==================== NAVEGACIÓN A SIGUIENTE PÁGINA ====================
        try:
            contenedor = driver.find_element(By.CSS_SELECTOR, "div.b-au_f")
            siguiente = contenedor.find_element(By.XPATH, ".//a[contains(text(), 'Siguiente')]")
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(1)
            driver.execute_script("arguments[0].click();", siguiente)
            pagina += 1
        except NoSuchElementException:
            print("Botón 'Siguiente' no encontrado dentro del contenedor. Fin del scraping.")
            break

# ==================== FINALIZAR ====================
driver.quit()
print(f"\nProceso finalizado. Total de noticias: {total_noticias}")
print(f"Archivo guardado como: {csv_filename}")
