# PRACT1_TCVD
M2.851 - Tipología y ciclo de vida de los datos - PRACT1

## Requerimientos
- Firefox
- Python (probado en Python 3.11.10)

## Instalación
Abre Firefox e identificate manualmente con tus credenciales para que se guarden las cookies de nuestra cuenta en el navegador

ejecuta:
```
pip install -r requirements.txt
python -m seleniumwire extractcert
```
La última línea generará un archivo .crt que deberás instalar

### Windows
Para instalar en Windows, símplemente haz doble click y sigue los pasos
### Linux
Para instalar el Linux copia el archivo a **/usr/share/ca-certificates** (podría variar según distribución Linux)
y ejecuta:
```
update-ca-certificates
```

## Fuentes de datos
- x.com
- elpais.com
- https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/
