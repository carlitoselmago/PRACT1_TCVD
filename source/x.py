from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from helpers import *
import sys

#obtenemos las credenciales de x.com
user,pwd=get_config()

browser = webdriver.Firefox()
browser.maximize_window()
wait = WebDriverWait(browser, 30)
browser.get('https://x.com/login')


# realizamos el login
username_input = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
username_input.send_keys(user)


nextbtn=WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Next')]")))
nextbtn.click()

sleep(3)

#password
username_input = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
username_input.send_keys(pwd)
username_input.send_keys(Keys.ENTER)

sleep(3)

# Realizar la búsqueda
termino = 'Agresión'
ubicacion = 'Spain'

query = f'{termino} place:{ubicacion}'

url = f'https://x.com/search?q={query}'

browser.get(url)
wait = WebDriverWait(browser, 30)
