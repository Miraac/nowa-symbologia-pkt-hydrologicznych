from qgis.core import QgsGeometry, QgsVectorLayer, QgsFeature, QgsFields, QgsField
from PyQt5.QtCore import QVariant
import string

BUFFER_DISTANCE = 5

def align_old_signs(punkty):
    new_num_col = punkty.fields().indexFromName('numer-nowy')
    for point in punkty.getFeatures():
        old_num = point['numer-stary']
        if old_num:
            point[new_num_col] = old_num
            punkty.updateFeature(point)

def temp_line_layer(cieki_layer):
    temp_layer = QgsVectorLayer("LineString?crs=" + cieki_layer.crs().authid(), "cieki_merge", "memory")
    provider = temp_layer.dataProvider()
    fields = QgsFields() 
    # pole oznaczenie
    fields.append(QgsField("oznaczenie", QVariant.String))
    provider.addAttributes(fields)
    temp_layer.updateFields()
    unique_streams = set(f["oznaczenie"] for f in cieki_layer.getFeatures())
    new_features = []
    for ozn in unique_streams:
        geoms = [f.geometry() for f in cieki_layer.getFeatures() if f["oznaczenie"] == ozn]
        if not geoms:
            continue
        merged_geom = QgsGeometry.unaryUnion(geoms)
        new_feat = QgsFeature(temp_layer.fields())
        new_feat.setGeometry(merged_geom)
        new_feat["oznaczenie"] = ozn
        new_features.append(new_feat)

    provider.addFeatures(new_features)

    return temp_layer


def find_points(stream_geom, points_layer):
    result = []
    for pt in points_layer.getFeatures():
        if stream_geom.distance(pt.geometry()) <= BUFFER_DISTANCE:
            pos = stream_geom.lineLocatePoint(pt.geometry())
            result.append({ "feature": pt, "position": pos, "old": pt["numer-stary"], "new": pt["numer-nowy"]})

    result.sort(key=lambda x: x["position"])
    return result

def new_symbols(points):
    print('numerowanie punktów:', len(points))

    letters = string.ascii_uppercase
    old_num = [i for i,p in enumerate(points) if p["old"]]
    # warunek 1: gdy brak poprzedniej numeracji
    if not old_num:

        for i,p in enumerate(points):
            new_val = f"{i+1}P"
            p["feature"]["numer-nowy"] = new_val

        return

    # warunek 2 - gdy istnieje numeracja, ale nie zaczyna się od pierwszego punktu
    first_old_num = old_num[0]

    for i in range(first_old_num):

        new_val = f"{i+1}P nowy"
        points[i]["feature"]["numer-nowy"] = new_val

    # warunek 3 - nieponumerowane punkty między starą numeracją
    for idx in range(len(old_num)-1):

        start = old_num[idx]
        end = old_num[idx+1]

        letter_index = 0

        for i in range(start+1, end):

            new_val = f"{points[start]['old']}{letters[letter_index]}"
            points[i]["feature"]["numer-nowy"] = new_val

            letter_index += 1

    # warunek 4 - punkty po ostatniej starej numeracji
    last_old_point = old_num[-1]
    base = points[last_old_point]["old"]

    try:
        num = int(base.replace("P",""))
    except:
        num = 0
    counter = 1
    for i in range(last_old_point+1, len(points)):

        new_val = f"{num+counter}P"
        points[i]["feature"]["numer-nowy"] = new_val

        counter += 1
