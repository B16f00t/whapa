![alt tag](https://github.com/B16f00t/whapa/blob/master/whapa.png)


Whatsapp Parser
==================================
Actualizado: February 2018 - Version 0.2
WhatsApp Messenger Version 2.18.29

Whapa es un analizador de bases de datos whatsapp que automatiza el proceso. El objetivo principal de whapa es presentar los datos manejados por la base de datos Sqlite de una manera comprensible para el analista.
El Script está desarollado en Python 2. x

La herramienta se divide en tres modos:
* **Modo Mensaje: Analiza todos los mensajes de la base de datos, aplicando diferentes filtros. Extrae las miniaturas cuando están disponibles.
* **Modo Descifrado: Descifra bases de datos crypto12 mientras tengamos la clave.
* **Modo Información: Muestra información diferente sobre estados, lista de difusión y grupos.

Tenga en cuenta que este proyecto esta una etapa temprana. Como tal, se pueden encontrar errores. Utilícelo bajo su propio riesgo!

**Bonus**: también incluye una herramienta para descargar copias de seguridad de Google Drive asociada a un smartphone.
"Whapas.py" es la Versión española de Whapa.py


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
	     __      __.__          __________         
	    /  \    /  \  |__ _____ \______   \_____   
	    \   \/\/   /  |  \\__  \ |     ___/\__  \  
	     \        /|   Y  \/ __ \|    |     / __ \_
	      \__/\  / |___|  (____  /____|    (____  /
	           \/       \/     \/               \/ 
	    ---------- Whatsapp Parser v0.2 -----------
    	
	usage: whapa.py [-h] [-k KEY | -i | -m] [-t TEXT] [-u USER] [-g GROUP] [-w]
	                [-s] [-b] [-tS TIME_START] [-tE TIME_END]
	                [-tT | -tI | -tA | -tV | -tC | -tL | -tX | -tP | -tG | -tD | -tR]
	                [DATABASE]
	
	To start choose a database and a mode with options
	
	positional arguments:
  	DATABASE              database file path - './msgstore.db' by default
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -k KEY, --key KEY     *** Decrypt Mode *** - key file path
	  -i, --info            *** Info Mode ***
	  -m, --messages        *** Message Mode ***
	  -t TEXT, --text TEXT  filter messages by text match
	  -u USER, --user USER  filter messages made by a phone number
	  -g GROUP, --group GROUP
	                        filter messages made in a group number
	  -w, --web             filter messages made by Whatsapp Web
	  -s, --starred         filter messages starred by user
	  -b, --broadcast       filter messages send by broadcast
	  -tS TIME_START, --time_start TIME_START
	                        filter messages by start time (dd-mm-yyyy HH:MM)
	  -tE TIME_END, --time_end TIME_END
	                        filter messages by end time (dd-mm-yyyy HH:MM)
	  -tT, --type_text      filter text messages
	  -tI, --type_image     filter image messages
	  -tA, --type_audio     filter audio messages
	  -tV, --type_video     filter video messages
	  -tC, --type_contact   filter contact messages
	  -tL, --type_location  filter location messages
	  -tX, --type_call      filter audio/video call messages
	  -tP, --type_application
	                        filter application messages
	  -tG, --type_gif       filter GIF messages
	  -tD, --type_deleted   filter deleted object messages
	  -tR, --type_share     filter Real time location messages	 

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