import configparser
import os
import requests
from furl import furl
import re

"""
Funciones de ayuda para scrapping y procesamiento básico de contenidos
"""

# Creamos un archivo de configuración con usuario y contraseña
def create_config(config_file_path, user, pwd):
    config = configparser.ConfigParser()
    config.add_section('Credenciales')
    config.set('Credenciales', 'usuario', user)
    config.set('Credenciales', 'contraseña', pwd)
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)

# Obtenemos usuario y contraseña desde el archivo settings.ini o los pedimos al usuario si no existe
def get_config():
    config_file_path = 'settings.ini'
    config = configparser.ConfigParser()
    
    # Comprobamos si el archivo ya existe
    if os.path.isfile(config_file_path):
        # Leemos la configuración existente
        config.read(config_file_path)
        user = config.get('Credenciales', 'usuario')
        pwd = config.get('Credenciales', 'contraseña')
        print('Configuración cargada: Usuario - {}'.format(user))
    else:
        # Pedimos las credenciales al usuario y guardarlas
        print("settings.ini no existe, introduce tu usuario y contraseña de X.com")
        user = input('Introduce el usuario: ')
        pwd = input('Introduce la contraseña: ')
        create_config(config_file_path, user, pwd)
        print('Configuración guardada en el archivo settings.ini.')
    
    return user, pwd

# Descargamos archivo multimedia usando las cookies del navegador
def downloadmedia(url, driver, downloadfolder):
    # Creamos carpeta de destino (si no existe)
    destfolder = downloadfolder
    os.makedirs(destfolder, exist_ok=True)

    # Extraemos cookies del navegador 
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])

    # Hacemos la petición usando la sesión con cookies
    response = session.get(url)
    
    if response.status_code == 200:
        # Determinamos el nombre del archivo a partir de la URL
        f = furl(url)
        file_name = str(f.path.segments[-1]) + "." + f.args["format"]
        
        # Solicitamos la versión más grande de la imagen
        f.set({"format": "jpg", "name": "large"})
        url = f.url
        
        # Guardamos el archivo en disco
        full_path = os.path.join(destfolder, file_name)
        with open(full_path, "wb") as f:
            f.write(response.content)
        
        print("Descargado en", full_path)
        return file_name
    else:
        print("Error:", response.status_code)
        return False

def processstats(stat):
    v = str(stat.text)

    # Convertimos a int aunque exista texto no numérico
    digitos = re.findall(r'\d+', v)
    if digitos:
        vp = int(''.join(digitos))
    else:
        vp = 0 

    # Multiplicamos si existen las letras K = 1000 o M = 1000000
    if "K" in v:
        vp*=1000
    if "M" in v:
        vp*=1000000

    return vp