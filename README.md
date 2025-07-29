# Splitly

Splitly és una aplicació web per gestionar despeses compartides entre amics durant viatges o esdeveniments.  
Permet registrar despeses, calcular balanços i compartir l’accés amb els participants d’una manera senzilla i segura.

## Funcionalitats

- Creació de viatges i gestió de participants.
- Afegir i visualitzar despeses de cada participant.
- Càlcul automàtic del balanç de deutes i pagaments.
- Validació de participants via **correu electrònic amb token**.
- Opció d’arxivar i eliminar viatges.
- Enviament d’emails amb **plantilla unificada**.
- Interfície senzilla i adaptada per a dispositius mòbils.

## Tecnologies utilitzades

- **Python 3.x** amb [Flask](https://flask.palletsprojects.com/)
- **MySQL / MariaDB** per a la base de dades
- **Bootstrap 5** per al frontend
- **Flask-Mail** per l’enviament d’emails
- **Jinja2** per al renderitzat de plantilles

## Requisits previs

- Python 3.9+
- MySQL o MariaDB
- `pip` i `virtualenv` recomanats

## Instal·lació

1. Clona el repositori:

   ```bash
   git clone https://github.com/albertfont/splitly.git
   cd splitly
   ```

2. Crea i activa un entorn virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instal·la les dependències:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura la base de dades i les variables d’entorn:

 - Copia config.example.ini a config.ini i edita els valors.
 - Crea la base de dades a MySQL i aplica les migracions si cal.

5. Executa l’aplicació en mode desenvolupament:

   ```bash
   flask run
   ```
Per defecte l’aplicació estarà disponible a http://127.0.0.1:5000

## Desplegament en producció
Per a desplegar en producció es recomana utilitzar:

 - Gunicorn com a servidor WSGI
 - Nginx com a reverse proxy
 - Systemd service per iniciar automàticament l’aplicació

Exemple amb Gunicorn:

   ```bash
   gunicorn -w 4 'app:app'
   ```

## Contribució
Les contribucions són benvingudes.
Pots fer un fork del repositori i enviar un pull request amb les teves millores.

## Llicència
Aquest projecte està sota la llicència MIT.
