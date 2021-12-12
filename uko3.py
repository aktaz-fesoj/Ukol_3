from pyproj import Transformer      #Knihovna pyproj pro práci se souřadnicovými systémy
import json                         # v praxi 4 fce: load, loads, dump, dumps
import math
import statistics
from geojson import Point, Feature, FeatureCollection

def otevri_data(adresy, kontejnery):
    with open(adresy, encoding="utf-8") as adresy_f:
        adresy_gj = json.load(adresy_f)
    with open(kontejnery, encoding="utf-8") as kontejnery_f:
        kontejnery_gj = json.load(kontejnery_f)
    data_adresy = adresy_gj['features']
    data_kontejnery = kontejnery_gj['features']
    print(f"Úspěšně načtěno {len(data_adresy)} adresních bodů.")
    print(f"Úspěšně načtěno {len(data_kontejnery)} lokalit kontejnerů na tříděný odpad.")
    return(data_adresy, data_kontejnery)

def prevod_wgs2jtsk(x, y):
    wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy = True)
    out = wgs2jtsk.transform(x, y) #always xy je true
    return(out)

def vzdalenost_bodu(x1,y1,x2,y2):
    delta_x = abs(x1-x2)
    delta_y = abs(y1-y2)
    vzd = math.sqrt(delta_x**2 + delta_y**2)
    return(vzd)

def roztrid_kontejnery(data_kontejnery):
    data_volne_kontejnery = []
    data_privatni_kontejnery = []
    for i in range (len(data_kontejnery)):
        data_kontejner_i = data_kontejnery[i]
        if data_kontejner_i["properties"]["PRISTUP"] == "volně":
            data_volne_kontejnery.append(data_kontejner_i)
        elif data_kontejner_i["properties"]["PRISTUP"] == "obyvatelům domu":
            data_privatni_kontejnery.append(data_kontejner_i)
    return(data_volne_kontejnery, data_privatni_kontejnery)

def roztrid_adresy(features, data_adresy, data_privatni_kontejnery):
    data_adresy_bez = []
    data_adresy_s = []
    for a in range (len(data_adresy)):
        data_adresa_a = data_adresy[a]
        shoda = False
        adresa_dohromady = f"{data_adresa_a['properties']['addr:street']} {data_adresa_a['properties']['addr:housenumber']}"
        for e in range(len(data_privatni_kontejnery)):
            data_kontejner_e = data_privatni_kontejnery[e]
            if data_kontejner_e["properties"]["STATIONNAME"] == adresa_dohromady:
                data_adresy_s.append(data_adresa_a)
                priprav_do_geojsonu(features, data_adresa_a["geometry"]["coordinates"][0], data_adresa_a["geometry"]["coordinates"][1], data_adresa_a['properties']['addr:street'], data_adresa_a['properties']['addr:housenumber'], data_kontejner_e["properties"]["ID"])
                shoda = True
        if shoda == False:
            data_adresy_bez.append(data_adresa_a)
    return(features, data_adresy_s, data_adresy_bez)

features = []
def priprav_do_geojsonu(features, sour_x, sour_y, adresa_prozapis_ulice, adresa_prozapis_cislo, kontejner_id):

    point = Point((sour_x, sour_y))

    # add more features...
    # features.append(...)

    features.append(Feature(geometry=point, properties={"addr:street": f"{adresa_prozapis_ulice}", "addr:housenumber": f"{adresa_prozapis_cislo}", "kontejner": f"{kontejner_id}"}))
    return(features)

data_adresy, data_kontejnery = otevri_data("adresy.geojson", "kontejnery.geojson")

data_volne_kontejnery, data_privatni_kontejnery = roztrid_kontejnery(data_kontejnery)
features, data_adresy_s, data_adresy_bez = roztrid_adresy(features, data_adresy, data_privatni_kontejnery)
        
pocet_adres_s = len(data_adresy_s)
pocet_adres_bez = len(data_adresy_bez)
pocet_volnych_kontejneru =  len(data_volne_kontejnery)
pocet_privatnich_kontejneru =  len(data_privatni_kontejnery)

print(f"Celkem {pocet_adres_bez} adres bez domácího kontejneru.")
print(f"Celkem {pocet_adres_s} adres s domácím kontejnerem.")
print(f"Celkem {pocet_volnych_kontejneru} volně přístupných kontejnerů.")
print(f"Celkem {pocet_privatnich_kontejneru} kontejnerů přístupných pouze obyvatelům domu.")

seznam_minimalnich = []
soucet_minimalnich = 0
maximalni_z_minimalnich = 0
for i in range(pocet_adres_bez):
    adresa = data_adresy_bez[i]
    nove_sour = prevod_wgs2jtsk(*adresa["geometry"]["coordinates"])
    adresa["geometry"]["coordinates"] = nove_sour
    vzd = 0
    minimalni = 0
    for u in range(pocet_volnych_kontejneru):
        kontejner = data_volne_kontejnery[u]
        vzd = vzdalenost_bodu(*adresa["geometry"]["coordinates"], *kontejner["geometry"]["coordinates"])
        if u == 0 or vzd < minimalni:
            minimalni = vzd
            minimalni_info = {"ulice_min":adresa["properties"]["addr:street"], "cislo_min":adresa["properties"]["addr:housenumber"], "kontejner_min":kontejner["properties"]["ID"]}
    if minimalni > maximalni_z_minimalnich:
        maximalni_z_minimalnich = minimalni
        if maximalni_z_minimalnich > 10000:
            print(f"Pravděpodobná chyba ve vstupních datech! Existuje adresní místo se vzdáleností více než 10 km (konkrétně {maximalni_z_minimalnich} m) k nejbližšímu kontejneru.")
            print("Běh programu je z tohoto důvodu ukončen. Zkontrolujte prosím vstupní data.")
            exit()
        maximalni_info = {"ulice_max":adresa["properties"]["addr:street"], "cislo_max":adresa["properties"]["addr:housenumber"], "hodnota_max": round(maximalni_z_minimalnich)}
    priprav_do_geojsonu(features, adresa["geometry"]["coordinates"][0], adresa["geometry"]["coordinates"][1], minimalni_info["ulice_min"], minimalni_info["cislo_min"], minimalni_info["kontejner_min"])
    seznam_minimalnich.append(minimalni)
    soucet_minimalnich += minimalni

for i in range(pocet_adres_s):      #Do seznamu přidám vzdálenosti 0 za privátní kontejnery, kvůli následnému výpočtu mediánu
    seznam_minimalnich.append(0)

med = round(statistics.median(seznam_minimalnich))
print(f"Průměrná vzdálenost ke kontejneru je: {round(soucet_minimalnich/len(data_adresy))} m.")
print(f"Medián vzdáleností ke kontejneru je: {med} m.")
print(f"Největší vzdálenost ke kontejneru je z adresy {maximalni_info['ulice_max']} {maximalni_info['cislo_max']} a to {maximalni_info['hodnota_max']} m.")



feature_collection = FeatureCollection(features)

with open('adresy_kontejnery.geojson', 'w', encoding="utf-8") as f:
    json.dump(feature_collection, f, ensure_ascii=False, indent=4)

