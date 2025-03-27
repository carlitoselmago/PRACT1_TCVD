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
# Variables: TODO: integrar con input()
termino = 'Agresión'
ubicacion = 'Spain'


#obtenemos las credenciales para x.com
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

query = f'{termino} place:{ubicacion}'

url = f'https://x.com/search?q={query}'

browser.get(url)
wait = WebDriverWait(browser, 30)



# Empezamos el scrapping
while True:

    posts=browser.find_elements(By.CSS_SELECTOR,'div[data-testid="cellInnerDiv"]')

    for p in posts:
        #try:
            timeelem=p.find_element(By.CSS_SELECTOR,'time[datetime]')
            parent=timeelem.find_element(By.XPATH, '..')
            post={
                'time':timeelem.get_attribute("datetime"),
                'posturl':parent.get_attribute("href"),
                'username':p.find_element(By.CSS_SELECTOR,'.css-1jxf684.r-dnmrzs.r-1udh08x.r-1udbk01.r-3s2u2q.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3').text
            }
            print(post)
            sys.exit()
        #except Exception as e:
        #    print("Hubo un error al procesar el post:",e)

            
            
            
            