# Keba-P40-REST-API-for-HA
Keba P40 Integration für Homeassistant, wenn Modbus und OCPP bereits anderweitig belegt ist. z.B. Abrechnungsdienstleister und Energiemanagementsystem 

Folgende Funktionen sind für die P40 vorhanden:
  - Phasenumschaltung
  - Anpassung des Stromes der Phase/Phasen
  - Anzeige von den Wichtigsten werten

Installation:
  1. Die Files in Homeassistant unter "/homeassistant/custom_components/keba_p40/" anlegen
  2. Homeassistant neu starten
  3. Unter Einstellungen  -> Geräte und Dienste eine neue Integration adden Namens keba_p40 hinzufügen
  
  <img width="729" height="332" alt="grafik" src="https://github.com/user-attachments/assets/f947258a-33d4-4758-a4fa-1ac105ad4d66" />
  
  4. Hostname IP eintragen, username ist admin und password euer User Passwort 
  
  <img width="729" height="546" alt="grafik" src="https://github.com/user-attachments/assets/b1bd30ea-f3a9-495b-8536-e806aa547afd" />
  
  5 Folgendes Gerät und Entitäten werden dann angelegt:

  <img width="405" height="309" alt="grafik" src="https://github.com/user-attachments/assets/4104e977-907e-455d-99a5-3f89ecc0af61" />

 <img width="335" height="726" alt="grafik" src="https://github.com/user-attachments/assets/147904a7-37ff-4c0b-89a0-a67b97cdfed8" />





Hier noch die Basic Infos was passiert, falls jemand mehr Infos benötigt.....

Die Beschreibung der REST API ist auf jeder Wallbox selbst über folgenden Link zu erreichen:
  - https://192.168.XXX.XXX:8443/docs#/V2_WALLBOX/post_v2_wallboxes


Befehl zur Abfrage des Tokens. Er ist immer nur 15minuten Gültig!
  - curl -X POST "https://192.168.XXX.XXX:8443/v2/jwt/login" -k -H "Content-Type: application/json" -d "{\"username\":\"admin\", \"password\":\"PASSWORT\"}"

Hier der genutzte GET Befehl zur Abfrag der Werte von der Wallbox:
  - curl -X GET "https://192.168.XXX.XXX/v2/wallboxes" -k -H "Authorization: Bearer <TOKEN_AUS_VORNGEGANGENER_ABFRAGE>
