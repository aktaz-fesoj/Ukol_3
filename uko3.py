#Instalována knihovna pyproj pro práci se souřadnicovými systémy

from pyproj import Transformer
import json                 # v praxi 4 fce: load, loads, dump, dumps

def prevod_wgs2jtsk(x, y):
    wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy = True)
    out = wgs2jtsk.transform(x, y) #always xy je true
    return(out)

with open("adresy_vinohrady.geojson", encoding="utf-8") as adresy:
    gj = json.load(adresy)
data = gj['features'][0]

#print(json.dumps(joo))      #Převedo do json reprezentace
