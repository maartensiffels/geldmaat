import pandas as pd
import requests
import csv
import os
import time
import random
import pytz
from datetime import datetime

# Lees het CSV-bestand in
df = pd.read_csv('Geldmaat_Locatie_IDs.csv') # PRODUCTIE
# df = pd.read_csv('Sample_Geldmaat_Locatie_IDs.csv') # TEST

# Haal de huidige tijd op en converteer deze naar CEST
nu = datetime.now()
cest_tijd = nu.astimezone(pytz.timezone('Europe/Amsterdam'))
huidige_tijd = cest_tijd.strftime('%Y%m%d_%H%M')

# Maak de map 'scrapes_hourly' als deze nog niet bestaat
os.makedirs('scrapes_hourly', exist_ok=True)

# Voeg de huidige tijd toe aan de bestandsnaam
bestandsnaam = os.path.join(os.getcwd(), 'scrapes_hourly', f'uitvoer_{huidige_tijd}.csv')

# Open een nieuw CSV-bestand om de gegevens weg te schrijven
with open(bestandsnaam, 'w', newline='') as csvfile:
    veldnamen = ['locatie_id', 'volgnummer', 'apparaat_id', 'type', 'status', 'statusReason', 'timestamp']
    schrijver = csv.DictWriter(csvfile, fieldnames=veldnamen)

    schrijver.writeheader()

    # Een dict om het aantal apparaten per data.id bij te houden
    volgnummers = {}

    # Ga door elke rij in het DataFrame
    for index, rij in df.iterrows():
        # Haal de data.id op
        data_id = rij['data.id']

        # Genereer een willekeurig aantal seconden tussen 0.1 en 0.2 seconden
        vertraging = random.uniform(0.1, 0.2)

        # Pauzeer de uitvoering van het script voor het gespecificeerde aantal seconden om detectie te voorkomen
        time.sleep(vertraging)  
        
        # Vraag de huidige tijd op
        nu = datetime.now()

        # Converteer de UTC tijd naar CEST
        cest_tijd = nu.astimezone(pytz.timezone('Europe/Amsterdam'))
        geformatteerde_tijd = cest_tijd.strftime('%Y-%m-%d %H:%M:%S')
        
        # Initialiseer de teller voor dit data_id als dit de eerste keer is dat we het zien
        if data_id not in volgnummers:
            volgnummers[data_id] = 0

        # Stel de URL samen
        url = f"https://api.prod.locator-backend.geldmaat.nl/locations/{data_id}"

        # Verstuur een GET-verzoek naar de URL
        respons = requests.get(url)

        # Controleer of het verzoek succesvol was
        if respons.status_code == 200:
            # Converteer de respons naar JSON
            data = respons.json()

            # Controleer of 'data' en 'devices' in de data zijn
            if 'data' in data and 'devices' in data['data']:
                # Ga door elk apparaat in de lijst van apparaten
                for apparaat in data['data']['devices']:
                    # Verhoog de teller voor dit data_id
                    volgnummers[data_id] += 1

                    # Schrijf de gegevens van het apparaat weg naar het CSV-bestand
                    schrijver.writerow({'locatie_id': data_id, 'volgnummer': f"{volgnummers[data_id]:02d}",
                                        'apparaat_id': apparaat['id'], 'type': apparaat['functionality'], 
                                        'status': apparaat['deviceState'], 'statusReason': apparaat['depositStatus'],
                                        'timestamp': geformatteerde_tijd})
            else:
                print(f"Geen 'devices' gevonden in de data voor id {data_id}")
