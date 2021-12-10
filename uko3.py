#Instalována knihovna pyproj pro práci se souřadnicovými systémy

from pyproj import Transformer
import json                 # v praxi 4 fce: load, loads, dump, dumps
import math

def prevod_wgs2jtsk(x, y):
    wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy = True)
    out = wgs2jtsk.transform(x, y) #always xy je true
    return(out)

def vzdalenost_bodu(x1,y1,x2,y2):
    delta_x = abs(x1-x2)
    delta_y = abs(y1-y2)
    vzd = math.sqrt(delta_x**2 + delta_y**2)
    return(vzd)



with open("adresy.geojson", encoding="utf-8") as adresy:
    adresy_gj = json.load(adresy)

with open("kontejnery.geojson", encoding="utf-8") as kontejnery:
    kontejnery_gj = json.load(kontejnery)

seznam_minimalnich = []
for i in range(len(adresy_gj['features'])):
    data_adresy = adresy_gj['features'][i]
    nove_sour = prevod_wgs2jtsk(*data_adresy["geometry"]["coordinates"])
    data_adresy["geometry"]["coordinates"] = nove_sour
    vzd = 0
    o = 0
    minimalni = 0
    pocet_kontejneru = len(kontejnery_gj['features'])
    for u in range(pocet_kontejneru):
        o += 1
        data_kontejnery = kontejnery_gj['features'][u]
        if data_kontejnery["properties"]["CITYDISTRICT"] == "Praha 2":
            vzd = vzdalenost_bodu(*data_adresy["geometry"]["coordinates"], *data_kontejnery["geometry"]["coordinates"])
            if u == 0 or vzd < minimalni:
                minimalni = vzd
    seznam_minimalnich.append(minimalni)

print(seznam_minimalnich)
print(len(seznam_minimalnich))
print(len(adresy_gj['features']))
    


#print(json.dumps(joo))      #Převedo do json reprezentace
