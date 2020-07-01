# Senado Mexicano
Web scrapping de la página del senado | Limpieza y almacenamiento en MongoDB | Extracción y traducción a pandas | Gráficas descriptivas con Seaborn



## About 

* Este proyecto recaba información de la página del [Senado](https://www.senado.gob.mx/64/) mexicano de cada Senador. Utilizando Scrapy se recaba información detallada de su
semblanza, intervenciones, votaciones, información personal y asistencias. Esta data se guarda en un NoSQL utilizando PyMongo para después extraerse y obtener información 
descriptiva de la data.


## Installation

Este proyecto utiliza Python. También se requiere bajar MongoDB para generar las bases de datos.

Vas a necesitar descargar las siguientes herramientas
1. Python (3.7.8 recommended)
2. MongoDB Community Edition (4.2 recommended)
3. Git (obviously)

Para el Web Scrapping utilizaremos Scrappy. Aquí les dejo la instalación para Windows que es un poco más compleja que en UNIX (que solo es pip install scrapy)
* Vamos a [Python Binaries para Windows](https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted) en #twisted
* Descarga la versión adecuada a tu versión de Python y versión de Windows
* Abre la terminal en donde descargaste el file y dale pip install "nombre del archivo que descargaste"

Las librerias que se deben descargar
* pip install pandas
* pip install numpy
* pip install matplotlib
* pip install seaborn
* pip install pymongo
* pip install scrapy

## Usage
El código comienza en la página de [senadores](https://www.senado.gob.mx/64/senadores) para el start_urls donde se encuentran los senadores hombres divididos por partido político
Se recorre cada perfil y se guardan en una DB de MongoDB. Después se debe repetir el código cambiando start_urls para las [senadoras](https://www.senado.gob.mx/64/senadoras)

##Roadmap
Tengo la idea de después eficientizar este código y, además, agregar información de las interacciones en redes sociales de los senadores utilizando la API de Twitter.
Creo que esto puede ayudar mucho a explicar el comportamiento de los senadores.
