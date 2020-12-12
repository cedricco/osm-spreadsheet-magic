# while true; do python scrap_tracks.py && git add-co -m 'update tracks' && git push origin; sleep 120; done
# curl https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n2_536295 | grep -A 2 "Parcours"


# curl https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n39_536557 | grep -A 2 "Parcours"

# https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n25_536539

# https://docs.google.com/spreadsheets/d/1C-D2wkA4ht4svC6ncN0bVmt88w05G-b-0OtCrHNhA8k/edit#gid=0

import geopandas
from shapely.geometry import Point

# 25e: 1519197

# 39e: 1519265

LAYER_IDS = [
    1518329, 1518350, 1519023, 1519045, 1519051, 1519063, 1519067, 1519074, 1519081, 1519089,
    1519096, 1519129, 1519134, 1519139, 1519144, 1519160, 1519164, 1519168, 1519172, 1519176,
    1519181, 1519185, 1519189, 1519193, 1519976, 1519202, 1519207, 1519211, 1519215, 1519219,
    1519224, 1519228, 1519233, 1519237, 1519247, 1519251, 1519257, 1519261, 1520045, 1519269,
    1519274, 1519279, 1519303, 1519309, 1519313, 1519317, 1519322, 1519326, 1519335, 1519339,
    1519344, 1519348, 1519352, 1519356, 1519360, 1519364, 1519368, 1519373, 1519402, 1519406,
]



TRACK_LAYERS = []

for (index, id) in enumerate(LAYER_IDS):
    try:
        TRACK_LAYERS.append(geopandas.read_file("http://umap.openstreetmap.fr/en/datalayer/%s/" % id))
    except Exception:
        print("PB avec %s" % (index + 1))


geometries = geopandas.GeoDataFrame()

for track_layer in TRACK_LAYERS:
    geometries = geometries.append(geopandas.GeoDataFrame.from_features(track_layer))

if not geometries.empty:
    geometries.to_file("tracks.geojson", driver='GeoJSON')
