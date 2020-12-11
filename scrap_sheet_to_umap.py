# while true; do python scrap_sheet_to_umap.py && git add-co -m 'update layers' && git push origin; sleep 600; done

from __future__ import print_function
import random
import re
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from geopy.geocoders import Nominatim
from time import sleep

REGEX_LAT = r"(?P<lat>\d{2}(\.|\,)\d{4,7})"
REGEX_LON = r"[^\d](?P<lon>-?\d(\.|,)\d{4,7})"


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1xITn4DPQDIlT_qiO51JpM_e7PiHQIZkX0zygcE3AWGY'
SAMPLE_RANGE_NAME = 'Alternatives!A1:AB'
COLUMN_NAMES = ['', 'Région', 'Département', 'alternative', 'Commune', """Adresse postale 
⚠️ + latitude/longitude si PB affichage carte (passer souris pour + d'infos)""", 'Initié par...          (prénom : date)', 'source', 'Contacté par...          (prénom : date)\nRelance le...', 'retour', 'Thèmatique', 'descriptif', 'date de passage', 'Prénom', 'Nom',
                'Mail', 'Téléphone', 'Portable', 'site internet', 'Réseaux sociaux', 'Rédacteur recueil', 'Carto plénière: incontournable ?', 'Carto plénière: punchline 1', 'Carto plénière: punchline 2', 'Carto plénière: punchline 3', 'Carto plénière: hashtag', 'Carto plénière: classification', 'Carto plénière: image']

DAYS_3 = "Essentiels 3 jours"
DAYS_7 = "Essentiels 7 jours"
BONUS = "Bonus à afficher"


def main():
    with open('utility_files/geoloc_adresses.json', 'r') as saved_geoloc_file:
        geoloc = json.load(saved_geoloc_file)

    creds = None
    if os.path.exists('utility_files/token.pickle'):
        with open('utility_files/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'utility_files/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('utility_files/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    for index, col_name in enumerate(values[0]):
        assert col_name == COLUMN_NAMES[index], "Expected 'column %s', got '%s'" % (
            COLUMN_NAMES[index], col_name)
    print("Columns OK")

    days_3_features = {
        "type": "FeatureCollection",
        "features": []
    }
    bonus_features = {
        "type": "FeatureCollection",
        "features": []
    }
    days_7_features = {
        "type": "FeatureCollection",
        "features": []
    }

    for row_nb, row in enumerate(values[1:]):
        if row_nb % 50 == 0:
            print("handling row %d" % row_nb)
        if len(row) >= 22:
            row = row + ["" for i in range(len(COLUMN_NAMES) - len(row))]
            adress = row[5]
            coords = geoloc.get(adress)
            latitude_search = re.search(REGEX_LAT, adress)
            longitude_search = re.search(REGEX_LON, adress)
            if latitude_search and longitude_search:
                coords = [float(longitude_search.group("lon")), float(latitude_search.group("lat"))]
            if not coords:
                geolocator = Nominatim(user_agent="pleniere_at_2020")
                location = geolocator.geocode(adress)
                sleep(1.5)
                if location:
                    coords = [location.longitude, location.latitude]
                    geoloc[adress] = coords
                    with open('utility_files/geoloc_adresses.json', 'w') as saved_geoloc_file:
                        json.dump(geoloc, saved_geoloc_file)
            if not coords:
                coords = [-4.6561 + random.random() * 1.5, 49.1150]
            elif coords[0] < -5.4756155192 or coords[0] > 3.7230954436 or coords[1] > 50.359718657 or coords[1] < 46.6907131609:
                coords = [-4.6561 + random.random() * 1.5, 49.2]
            emoji = row[26].split(" ")[0] if row[26] else ""
            url_image = row[27]
            if row[21] in [DAYS_3, DAYS_7, BONUS]:
                feature_collection = {
                    DAYS_3: days_3_features,
                    DAYS_7: days_7_features,
                    BONUS: bonus_features,
                }[row[21]]
                hashtag = "#" + row[25].replace("#", "") + "\n" if row[25] else ""
                text = """%s%s**Pourquoi il faut absolument y passer ?**
1️⃣ %s
2️⃣ %s
3️⃣ %s

*Site oueb* %s
*Sur les rézos* %s

%s**Description**
%s

**Retours**
%s
                """ % ("{{%s}}\n" % url_image if url_image else "", hashtag, row[22] or "A remplir !", row[23] or "A remplir !", row[24] or "A remplir !", row[18] if row[18] else "A remplir !", row[19] if row[19] else "A remplir !", "**Date de passage:** %s\n\n" % row[12] if row[12] else "", row[11], row[9])

                feature_collection["features"].append({
                    "type": "Feature",
                    "properties": {
                        "description": text,
                        "name": emoji + " " + row[3],
                        "_umap_options": {
                            "iconUrl": emoji
                        }
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                })

    with open('days_3_features.geojson', 'w') as outfile:
        json.dump(days_3_features, outfile)
    with open('days_7_features.geojson', 'w') as outfile:
        json.dump(days_7_features, outfile)
    with open('bonus_features.geojson', 'w') as outfile:
        json.dump(bonus_features, outfile)


# TODOs
# Ajouter département en filter key sur la map. Rentrer "29 - Finistère" par ex.
# Ajouter calque de départements

if __name__ == '__main__':
    main()
