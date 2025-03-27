def create_config(config_file_path, user, pwd):
    config = configparser.ConfigParser()
    config.add_section('Credenciales')
    config.set('Credenciales', 'usuario', user)
    config.set('Credenciales', 'contraseña', pwd)
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)

def get_config():
    config_file_path = 'settings.ini'
    config = configparser.ConfigParser()
    if os.path.isfile(config_file_path):
        config.read(config_file_path)
        user = config.get('Credenciales', 'usuario')
        pwd = config.get('Credenciales', 'contraseña')
        print('Configuración cargada: Usuario - {}'.format(user))
    else:
        print("settings.ini no existe, introduce tu usuario y contraseña de Twitter y los datos se guardarán para la próxima vez")
        user = input('Introduce el usuario: ')
        pwd = input('Introduce la contraseña: ')
        create_config(config_file_path, user, pwd)
        print('Configuración guardada en el archivo settings.ini.')
    
    return user, pwd
