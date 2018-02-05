![alt tag](https://github.com/B16f00t/whapa/blob/master/whapa.png)


Whatsapp Parser
==================================
Actualizado: February 2018 - Version 0.1

WhatsApp Messenger Version 2.18.29

Whapa es un analizador de bases de datos whatsapp que automatiza el proceso. El objetivo principal de whapa es presentar los datos manejados por la base de datos Sqlite de una manera comprensible para el analista.
El Script está desarollado en Python 2. x

La herramienta se divide en tres modos:
* **Modo Mensaje:** Analiza todos los mensajes de la base de datos, aplicando diferentes filtros. Extrae las miniaturas cuando están disponibles.
* **Modo Descifrado:** Descifra bases de datos crypto12 mientras tengamos la clave.
* **Modo Información:** Muestra información diferente sobre estados, lista de difusión y grupos.

Tenga en cuenta que este proyecto esta una etapa temprana. Como tal, se pueden encontrar errores. Utilícelo bajo su propio riesgo!

**Bonus**: también incluye una herramienta para descargar copias de seguridad de Google Drive asociada a un smartphone.
"Whapas.py" es la Versión española de whapa.py


Instalación
=====
 whapa.py (Whatsapp parser)
---------
Puede descargar la última versión de whapa clonando el repositorio de GitHub:

	git clone https://github.com/B16f00t/whapa.git
después:

	pip install -r requirements.txt
	
 whagdext.py (Extrae los datos de la cuenta de Google Drive)
-------------

	sudo apt-get update
	sudo apt-get install -y python3-pip
	sudo pip3 install pyportify
	Para usar:
	config settings.cfg
		[auth]
		gmail = alias@gmail.com
		passw = yourpassword
	python3 whagdext.py "arguments"


Uso
=====
Version inglesa **whapa.py**

Version española **whapas.py**

     __      __.__                                
    /  \    /  \  |__ _____  ___________    ______
    \   \/\/   /  |  \\__  \ \____ \__  \  /  ___/
     \        /|   Y  \/ __ \|  |_> > __ \_\___ \ 
      \__/\  / |___|  (____  /   __(____  /____  >
           \/       \/     \/|__|       \/     \/  
    ---------- Whatsapp Parser Spanish v0.1 -----------

    	
	usage: whapas.py [-h] [-k KEY | -i | -m] [-t TEXT] [-u USER] [-g GROUP] [-w]
	                [-s] [-b] [-tS TIME_START] [-tE TIME_END]
	                [-tT | -tI | -tA | -tV | -tC | -tL | -tX | -tP | -tG | -tD | -tR]
	                [DATABASE]
	
	Para empezar elija una base de dats y un modo con opciones
	
	positional arguments:
  	DATABASE                ruta del la base de datos - './msgstore.db' por defecto
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -k KEY, --key KEY     *** Modo Descifrar*** - ruta del archivo key
	  -i, --info            *** Modo Información ***
	  -m, --messages        *** Modo Mensaje ***
	  -t TEXT, --text TEXT  filtrar mensajes por coincidencias de texto
	  -u USER, --user USER  filtrar mensajes hechos por un número
	  -g GROUP, --group GROUP
	                        filtrar mensajes por grupo
	  -w, --web             filtrar mensajes hechos por Whatsapp Web
	  -s, --starred         filtrar mensajes destacados por el usuario
	  -b, --broadcast       filtrat mensajes por difusión
	  -tS TIME_START, --time_start TIME_START
	                        filtrar mensajes por tiempo de comienzo (dd-mm-yyyy HH:MM)
	  -tE TIME_END, --time_end TIME_END
	                        filtrar mensajes por tiempo de fin (dd-mm-yyyy HH:MM)
	  -tT, --type_text      filtrar mensajes de textos
	  -tI, --type_image     filtrar mensajes de imagenes
	  -tA, --type_audio     filtrar mensajes de audio
	  -tV, --type_video     filtrar mensajes de video
	  -tC, --type_contact   filtrat mensajes de contactos
	  -tL, --type_location  filtrat mensajes de localizaciones
	  -tX, --type_call      filtrar mensajes de audio/video llamada.
	  -tP, --type_application
	                        filtrar mensajes de aplicaciones
	  -tG, --type_gif       filtrar mensajes de GIF
	  -tD, --type_deleted   filtrat mensajes de objetos eliminados
	  -tR, --type_share     filtrar mensajes de localización en tiempo real	 

Ejemplos
=====
("./Media" es el directrorio donde se guardan las miniaturas)

* Modo Mensaje:

		python whapa.py -m 
	Muestra todos los mensajes de la base de datos

		python whapa.py -m -tS "12-12-2017 12:00" -tE "13-12-2017 12:00"
	Muestra todos los mensajes de la fecha 12-12-2017 12:00 a 13-12-2017 12:00.

		python whapa.py -m -w -tI
	Muestra todos los mensajes enviados a través de Whatsapp Web.


* Modo Descifrar:

		python whapa.py msgstore.db.crypt12 -k key
	Descifra msgstore.dbcrypt12, creadno msgstore.db

* Modo Información:

		python whapa.py -i
	Muestra una pantalla con opciones dobre grupos, listas de difusión y estados.


Actualizaciones futuras
=====
Creación de informes de la información mostrada por el script.
  
	
Descargo de responsabilidad
=====
El desarrollador no es responsable, y expresamente renuncia a toda responsabilidad por daños de cualquier tipo que surjan del uso, referencia o confianza en el software. No se garantiza que la información proporcionada por el software sea correcta, completa y actualizada.
