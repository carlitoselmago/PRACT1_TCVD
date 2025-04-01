from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from helpers import *
import sys

"""
Scrapper para X.com
"""

# Definimos las variables de búsqueda
termino = 'Winsconsin'
ubicacion = 'Spain'

# Obtenemos las credenciales para x.com
user, pwd = get_config()

# Iniciamos el navegador
browser = webdriver.Firefox()
browser.maximize_window()
wait = WebDriverWait(browser, 30)
browser.get('https://x.com/login')

# Hacemos  login
username_input = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
username_input.send_keys(user)

# Pulsamos el botón "Next"
nextbtn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Next')]")))
nextbtn.click()
sleep(3)

# Introducir contraseña y hacer login
password_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
password_input.send_keys(pwd)
password_input.send_keys(Keys.ENTER)
sleep(3)

# Realizar la búsqueda por parámetros
query = f'{termino} place:{ubicacion} since:2006-01-01 min_faves:5 min_retweets:0 '
url = f'https://x.com/search?q={query}'

browser.get(url)

# Creamos una lista para guardar los datos extraídos
data = []

# Esperamos a que aparezcan los primeros posts
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')))
post_counter = 0
intentos_sin_nuevos_posts = 0
max_intentos = 5

# Empezamos el scraping
while True:
    # Buscamos posts
    posts = browser.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]')

    # Procesamos los nuevos posts
    nuevos_posts = 0
    for p in posts[post_counter:]:
        try:
            # Obtenemos la hora del post
            timeelem = p.find_element(By.CSS_SELECTOR, 'time[datetime]')
            parent = timeelem.find_element(By.XPATH, '..')

            # Inicializamos lista de elementos multimedia
            media = []

            # Buscamos imágenes asociadas
            img_elements = p.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                imgsrc = img.get_attribute("src")
                if "/media/" in imgsrc:
                    try:
                        # Utilizamos una función de helpers
                        filename = downloadmedia(imgsrc, browser, '../media/')
                        if filename:
                            media.append(filename)
                    except Exception as e:
                        print("No se pudo descargar la imagen:", e)

            # Buscamos los elementos numéricos del post
            statsdom = p.find_elements(By.CSS_SELECTOR, ".css-175oi2r.r-18u37iz.r-1h0z5md.r-13awgt0")

            stats={
                'replies':processstats(statsdom[0]),
                'reposts':processstats(statsdom[1]),
                'likes':processstats(statsdom[2]),
                'visitas':processstats(statsdom[3])
            }


            # Creamos un diccionario para el post
            post = {
                'time': timeelem.get_attribute("datetime"),
                'posturl': parent.get_attribute("href"),
                'username': p.find_element(By.CSS_SELECTOR, '.css-1jxf684.r-dnmrzs.r-1udh08x.r-1udbk01.r-3s2u2q.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3').text,
                'text': p.find_element(By.CSS_SELECTOR, '.css-146c3p1.r-8akbws.r-krxsd3.r-dnmrzs.r-1udh08x.r-1udbk01.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-bnwqim').get_attribute('innerHTML'),
                'media': media,
                'stats': stats
            }

            if post not in data:
                data.append(post)
                nuevos_posts += 1
                #print(post)
                print(post["time"],post["username"],"::::")

        except Exception as e:
            # Si no se puede procesar el post mostramos el error y su origen
            print("Hubo un error al procesar el post:", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    post_counter = len(posts)

    # Comprobamos si hay nuevos posts
    if nuevos_posts == 0:
        intentos_sin_nuevos_posts += 1
        print(f"No se detectaron nuevos posts ({intentos_sin_nuevos_posts}/{max_intentos})")
        if intentos_sin_nuevos_posts >= max_intentos:
            print("No se encontraron más posts. Finalizando scraping.")
            print(f"Se han procesado {len(data)} posts.")
            break
    else:
        intentos_sin_nuevos_posts = 0

    # Hacemos scroll para que aparezcan nuevos posts
    # Intentamos ralentizar el proceso para no limitar el ratio de posts recibidos
    print("Haciendo scroll...")
    for i in range(5):
        browser.execute_script("window.scrollBy(0, 500);")
        sleep(0.8)  

    # Pausa
    sleep(3)
