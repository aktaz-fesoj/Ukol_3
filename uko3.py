from pyproj import Transformer      #Knihovna pyproj pro práci se souřadnicovými systémy
import json                         # v praxi 4 fce: load, loads, dump, dumps
import math
import statistics

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
print(f"Úspěšně načtěno {len(data_adresy)} adresních bodů.")
print(f"Úspěšně načtěno {len(data_kontejnery)} lokalit kontejnerů na tříděný odpad.")
data_volne_kontejnery = []
data_privatni_kontejnery = []
data_adresy_bez = []
data_adresy_s = []
kon = 0
for i in range (len(data_kontejnery)):
    data_kontejner_i = data_kontejnery[i]
    if data_kontejner_i["properties"]["PRISTUP"] == "volně":
        data_volne_kontejnery.append(data_kontejner_i)
    elif data_kontejner_i["properties"]["PRISTUP"] == "obyvatelům domu":
        data_privatni_kontejnery.append(data_kontejner_i)
        
for a in range (len(data_adresy)):
    data_adresa_a = data_adresy[a]
    shoda = False
    adresa_dohromady = f"{data_adresa_a['properties']['addr:street']} {data_adresa_a['properties']['addr:housenumber']}"
    for e in range(len(data_privatni_kontejnery)):
        data_kontejner_e = data_privatni_kontejnery[e]
        if data_kontejner_e["properties"]["STATIONNAME"] == adresa_dohromady:
            data_adresy_s.append(data_adresa_a)
            shoda = True
    if shoda == False:
        data_adresy_bez.append(data_adresa_a)


pocet_adres_s = len(data_adresy_s)
pocet_adres_bez = len(data_adresy_bez)
pocet_volnych_kontejneru =  len(data_volne_kontejnery)
pocet_privatnich_kontejneru =  len(data_privatni_kontejnery)

print(pocet_adres_bez, pocet_adres_s, pocet_volnych_kontejneru, pocet_privatnich_kontejneru)

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
    if minimalni > maximalni_z_minimalnich:
        maximalni_z_minimalnich = minimalni
        if maximalni_z_minimalnich > 10000:
            print(f"Pravděpodobná chyba ve vstupních datech! Existuje adresní místo se vzdáleností více než 10 km (konkrétně {maximalni_z_minimalnich} m) k nejbližšímu kontejneru.")
            print("Běh programu je z tohoto důvodu ukončen. Zkontrolujte prosím vstupní data.")
            exit()
        maximalni_info = {"ulice_max":adresa["properties"]["addr:street"], "cislo_max":adresa["properties"]["addr:housenumber"], "hodnota_max": round(maximalni_z_minimalnich)}
    seznam_minimalnich.append(minimalni)
    soucet_minimalnich += minimalni

med = round(statistics.median(seznam_minimalnich))
print(f"Průměrná vzdálenost ke kontejneru je: {round(soucet_minimalnich/pocet_adres_bez)} m.")
print(f"Medián vzdáleností ke kontejneru je: {med} m.")
print(f"Největší vzdálenost ke kontejneru je z adresy {maximalni_info['ulice_max']} {maximalni_info['cislo_max']} a to {maximalni_info['hodnota_max']} m.")

print(len(seznam_minimalnich))
print(len(adresy_gj['features']))



med = round(statistics.median(seznam_minimalnich))
print(f"Průměrná vzdálenost ke kontejneru je: {round(soucet_minimalnich/len(data_adresy))} m.")
print(f"Medián vzdáleností ke kontejneru je: {med} m.")
print(f"Největší vzdálenost ke kontejneru je z adresy {maximalni_info['ulice_max']} {maximalni_info['cislo_max']} a to {maximalni_info['hodnota_max']} m.")

print(len("minimalni_seznam delka porovnani s poctem adres:"))
print(len(seznam_minimalnich))
print(len(adresy_gj['features']))
print(len("private_seznam delka porovnani s poctem shodnych adres:"))
print(len(data_privatni_kontejnery))
print(pocet_private_kontejneru)

#print(json.dumps(joo))      #Převedo do json reprezentace
