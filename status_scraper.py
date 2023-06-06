import pandas as pd
import requests
import csv
from datetime import datetime

# Lees het CSV-bestand in
df = pd.read_csv('Sample_Geldmaat_Locatie_IDs.csv')

# Krijg de huidige tijd en formatteer het als een string
nu = datetime.now()
tijdstring = nu.strftime("%Y%m%d_%H%M%S")

# Open een nieuw CSV-bestand om de gegevens weg te schrijven, met de huidige tijd in de bestandsnaam
with open(f'uitvoer_{tijdstring}.csv', 'w', newline='') as csvfile:
    veldnamen = ['locatie_id', 'volgnummer', 'apparaat_id', 'type', 'status', 'statusReason', 'timestamp']
    schrijver = csv.DictWriter(csvfile, fieldnames=veldnamen)

    schrijver.writeheader()

    # Een dict om het aantal apparaten per data.id bij te houden
    volgnummers = {}

    # Ga door elke rij in het DataFrame
    for index, rij in df.iterrows():
        # Haal de data.id op
        data_id = rij['data.id']

        # Initialiseer de teller voor dit data_id als dit de eerste keer is dat we het zien
        if data_id not in volgnummers:
            volgnummers[data_id] = 0

        # Stel de URL samen
        url = f"https://ii0d2f1pfc.execute-api.eu-west-1.amazonaws.com/prod/locations/{data_id}"

        # Verstuur een GET-verzoek naar de URL
        respons = requests.get(url)

        # Vang de huidige tijd op
        nu = datetime.now()

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
                                        'timestamp': nu})
            else:
                print(f"Geen 'devices' gevonden in de data voor id {data_id}")
