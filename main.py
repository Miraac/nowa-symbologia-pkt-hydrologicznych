from qgis.core import QgsVectorLayer
import tools
import importlib
importlib.reload(tools)


gpkg_path = r'D:\projekty\QGIS\EnviroRekrutacja\zadaniex.gpkg'
linie = 'cieki'
points_name = 'punkty'

# wczytanie warstw
cieki_layer = QgsVectorLayer(f"{gpkg_path}|layername={linie}", linie, 'ogr')
punkty_layer = QgsVectorLayer(f"{gpkg_path}|layername={points_name}", points_name, 'ogr')


punkty_layer.startEditing()

tools.align_old_signs(punkty_layer)
# unikalne oznaczenia cieków
unique_streams = set([f["oznaczenie"] for f in cieki_layer.getFeatures()])
# tymczasowa warstwa liniowa z połączonymi geometriami dla danego oznaczenia
cieki_merge = tools.temp_line_layer(cieki_layer)
for stream in cieki_merge.getFeatures():
    points_on_stream = tools.find_points(stream.geometry(), punkty_layer)
    if not points_on_stream:
        continue
    tools.new_symbols(points_on_stream)
    for p in points_on_stream:
        punkty_layer.updateFeature(p["feature"])
punkty_layer.commitChanges()

print("DONE")
