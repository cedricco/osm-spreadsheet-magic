# curl https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n2_536295 | grep -A 2 "\"name\":"

# https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n1_536288 => 1518329
# https://umap.openstreetmap.fr/en/map/dessin-de-parcours-n2_536295 => 1518350


import geopandas
from shapely.geometry import Point

LAYER_IDS = [1518329, 1518350]

TRACK_LAYERS = [geopandas.read_file("http://umap.openstreetmap.fr/en/datalayer/%s/" % id) for id in LAYER_IDS]

geometries = geopandas.GeoDataFrame()

for track_layer in TRACK_LAYERS:
    filtered_layer = []
    for geom in track_layer.iterfeatures():
        if geom.get("geometry", {}).get("type") == "LineString":
            
        import ipdb; ipdb.set_trace()
        geometries = geometries.append(geopandas.GeoDataFrame(geom))


if not geometries.empty:
    geometries.to_file("tracks.geojson", driver='GeoJSON')