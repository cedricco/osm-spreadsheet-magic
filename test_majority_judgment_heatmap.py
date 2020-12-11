# curl --output 532470.json http://umap.openstreetmap.fr/en/map/532470/geojson/
# Enregistrer fichier

# Ouvrir le fichier
# Dans le résultat prendre "id" à partir du "name":
# {
# "name": "Layer 1",
# "id": 1506133,
# "displayOnLoad": true
# }

# Commencer avec 2 cartes à merger
# https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n2_536295
# https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n1_536288

import geopandas
import random
from shapely.geometry import Point

LAYER

likes = geopandas.read_file("http://umap.openstreetmap.fr/en/datalayer/1506234/")

random_points_left = []
random_points_right = []
for like in likes.itertuples():
    for i in range(random.randint(0, 70)):
        sign = random.choice((-1, 1))
        xoff = sign * (1/50 + (random.random() / 200))
        yoff = 1/1000
        nu_point = Point(like.geometry.x + xoff, like.geometry.y + yoff)
        if sign == 1:
            random_points_right.append(nu_point)
        random_points_left.append(nu_point)



d_left = {'geometry': random_points_left}
d_right = {'geometry': random_points_right}
gdf_left = geopandas.GeoDataFrame(d_left, crs="EPSG:4326")
gdf_right = geopandas.GeoDataFrame(d_right, crs="EPSG:4326")

nu_stuff_left = likes.append(gdf_left)
nu_stuff_right = likes.append(gdf_right)

nu_stuff_left.to_file("left.geojson", driver='GeoJSON')
nu_stuff_right.to_file("right.geojson", driver='GeoJSON')
