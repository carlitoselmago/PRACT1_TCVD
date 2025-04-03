from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime, timedelta
from helpers import *
import sys
import csv

"""
Scrapper para X.com
"""


# Variables de búsqueda
termino = 'Violencia Machista'
ubicacion = 'Spain'
fecha_inicio = '2015-01-01'  # Fecha inicio (string) en formato YYYY-MM-DD
fecha_fin = '2024-12-31'     # Fecha fin (string) en formato YYYY-MM-DD

# Obtenemos credenciales
user, pwd = get_config()

# Iniciamos el navegador
browser = webdriver.Firefox()
browser.maximize_window()
wait = WebDriverWait(browser, 30)

# Abrimos la página de login
browser.get('https://x.com/login')

# Iniciar sesión
username_input = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
username_input.send_keys(user)

nextbtn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Next')]")))
nextbtn.click()
sleep(3)

password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
password_input.send_keys(pwd)
password_input.send_keys(Keys.ENTER)
sleep(3)

# Parseamos las fechas a objetos datetime
start_date = datetime.strptime(fecha_inicio, "%Y-%m-%d")
end_date   = datetime.strptime(fecha_fin, "%Y-%m-%d")

# Para guardar todos los posts de todos los meses
all_data = []

# Recorremos mes a mes
current_date = start_date
while current_date < end_date:
    # Definimos inicio de mes y comienzo del mes siguiente
    month_start = current_date
    next_month = get_next_month(month_start)  # Asumiendo que helpers.py define get_next_month

    # Ajustamos si el next_month está más allá de fecha_fin
    month_end = min(next_month, end_date)

    # Construimos query para este mes
    query = (f'{termino} place:{ubicacion} '
             f'since:{month_start.strftime("%Y-%m-%d")} '
             f'until:{month_end.strftime("%Y-%m-%d")} '
             #'min_faves:0 min_retweets:0'
             )

    # Armamos la URL de búsqueda
    search_url = f'https://x.com/search?q={query}'
    browser.get(search_url)

    # Esperamos a que aparezcan posts (si existen)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')))
    except:
        print(f"\nNo hay posts para {month_start.strftime('%Y-%m-%d')} - {month_end.strftime('%Y-%m-%d')}")
        current_date = next_month
        continue

    # Lista para los datos de este mes
    data = []
    post_counter = 0
    intentos_sin_nuevos_posts = 0
    max_intentos = 5

    print(f"\n=== SCRAPEANDO {month_start.strftime('%Y-%m-%d')} - {month_end.strftime('%Y-%m-%d')} ===")
    while True:
        # Buscamos todos los posts actualmente cargados
        posts = browser.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')

        nuevos_posts = 0
        # Procesamos desde el último index guardado (post_counter)
        for p in posts[post_counter:]:
            try:
                timeelem = p.find_element(By.CSS_SELECTOR, 'time[datetime]')
                parent = timeelem.find_element(By.XPATH, '..')

                # Buscamos imágenes asociadas
                media = []
                img_elements = p.find_elements(By.TAG_NAME, "img")
                for img in img_elements:
                    imgsrc = img.get_attribute("src")
                    if "/media/" in imgsrc:
                        try:
                            filename = downloadmedia(imgsrc, browser, '../media/')
                            if filename:
                                media.append(filename)
                        except Exception as e:
                            print("No se pudo descargar la imagen:", e)

                # Buscamos estadísticas
                statsdom = p.find_elements(By.CSS_SELECTOR, ".css-175oi2r.r-18u37iz.r-1h0z5md.r-13awgt0")

                # Creamos diccionario para el post
                post = {
                    'Fecha': timeelem.get_attribute("datetime"),
                    'Enlace': parent.get_attribute("href"),
                    'Autor': p.find_element(
                        By.CSS_SELECTOR,
                        '.css-1jxf684.r-dnmrzs.r-1udh08x.r-1udbk01.r-3s2u2q.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3'
                    ).text,
                    'text': p.find_element(
                        By.CSS_SELECTOR,
                        '.css-146c3p1.r-8akbws.r-krxsd3.r-dnmrzs.r-1udh08x.r-1udbk01.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-bnwqim'
                    ).get_attribute('innerHTML'),
                    'Media': ', '.join(media),
                    'Replies': processstats(statsdom[0]),
                    'Reposts': processstats(statsdom[1]),
                    'Likes':   processstats(statsdom[2]),
                    'Visitas': processstats(statsdom[3]),
                    'Lugar':   ubicacion
                }

                # Evitamos duplicados
                if post not in data:
                    data.append(post)
                    nuevos_posts += 1
                    print(post["Fecha"], post["Autor"], "::::")

            except Exception as e:
                print("Hubo un error al procesar el post:", e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        post_counter = len(posts)

        # Verificamos si aparecieron nuevos posts
        if nuevos_posts == 0:
            intentos_sin_nuevos_posts += 1
            print(f"No se detectaron nuevos posts ({intentos_sin_nuevos_posts}/{max_intentos})")

            # Si ya hemos alcanzado el máximo de intentos sin encontrar nada, salimos
            if intentos_sin_nuevos_posts >= max_intentos:
                print("No se encontraron más posts este mes. Pasamos al siguiente mes.")
                break
            else:
                # Hacemos una pausa y volvemos a intentarlo (quizá ya no haya más)
                sleep(2)
        else:
            # Reseteamos el conteo de intentos sin posts
            intentos_sin_nuevos_posts = 0

            # Hacemos scroll para cargar más contenido
            print("Haciendo scroll para cargar más posts...")
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Esperamos un poco para que carguen nuevos tweets
            sleep(5)  

    # Acumulamos los datos de este mes en all_data
    all_data.extend(data)

    # Pasamos al siguiente mes
    current_date = next_month
    pausa_entre_meses=120 # en segundos
    sleep(120)  
    print(f"Pausando durante {pausa_entre_meses/60} minutos...")

# Guardamos todo en un CSV
if all_data:
    keys = all_data[0].keys()
    filename = f'x_scrap_{termino}_{ubicacion}_{fecha_inicio}_{fecha_fin}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)
    print(f"\nScraping terminado. Se han extraído {len(all_data)} posts en total.")
    print(f"Datos guardados en: {filename}")
else:
    print("\nNo se encontraron posts en todo el rango especificado.")