from pyproj import Transformer      #Knihovna pyproj pro práci se souřadnicovými systémy
import json                         # v praxi 4 fce: load, loads, dump, dumps
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

with open("adresy.geojson", encoding="utf-8") as adresy_f:
    adresy_gj = json.load(adresy_f)

with open("kontejnery.geojson", encoding="utf-8") as kontejnery_f:
    kontejnery_gj = json.load(kontejnery_f)

data_adresy = adresy_gj['features']
data_kontejnery = kontejnery_gj['features']

data_volne_kontejnery = []
for i in range (len(data_kontejnery)):
    data_kontejnery_tridici = data_kontejnery[i]
    if data_kontejnery_tridici["properties"]["PRISTUP"] == "volně":
        data_volne_kontejnery.append(data_kontejnery_tridici)
print(data_volne_kontejnery)

pocet_adres =       len(data_adresy)
pocet_kontejneru =  len(data_volne_kontejnery)

seznam_minimalnich = []
soucet_minimalnich = 0
for i in range(pocet_adres):
    adresa = data_adresy[i]
    nove_sour = prevod_wgs2jtsk(*adresa["geometry"]["coordinates"])
    adresa["geometry"]["coordinates"] = nove_sour
    vzd = 0
    minimalni = 0
    for u in range(pocet_kontejneru):
        kontejner = data_volne_kontejnery[u]
        vzd = vzdalenost_bodu(*adresa["geometry"]["coordinates"], *kontejner["geometry"]["coordinates"])
        if u == 0 or vzd < minimalni:
            minimalni = vzd
    seznam_minimalnich.append(minimalni)
    soucet_minimalnich += minimalni

print(f"Průměrná vzdálenost ke kontejneru je: {round(soucet_minimalnich/pocet_adres)} m.")

print(len(seznam_minimalnich))
print(len(adresy_gj['features']))
    


#print(json.dumps(joo))      #Převedo do json reprezentace
