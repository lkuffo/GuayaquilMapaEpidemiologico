"""
GENERA UN HEAT MAP HTML A PARTIR DE UN ARCHIVO
"""
import pandas as pd

data = [
    ("Emergencia", pd.read_csv("../../data/ESPOL - EMERGENCIA.csv")),
    ("Hospitalizacion", pd.read_csv("../../data/ESPOL - HOSPITALIZACION.csv")),
    ("Consulta Externa", pd.read_csv("../../data/ESPOL - CONSULTA EXTERNA.csv"))
]

street_file = pd.read_csv("./streets_address_file.csv", sep="@")

dirs = street_file["dir"].values
lats = street_file["lat"].values
lngs = street_file["lon"].values
enfermedades = []


df = data[0][1]

address = list(df["direccion"].values)
cie_10 = df["cie_10"].values


for dir in dirs:
    i = address.index(dir)
    enfermedad = cie_10[i]
    enfermedades.append(enfermedad)

#file = open("first_coords_test.csv", "w")
for i, elem in enumerate(enfermedades):
    dir = dirs[i]
    lat = lats[i]
    lon = lngs[i]
    c10 = enfermedades[i]
    if lat != 0 and c10 == "A09":
        print "new google.maps.LatLng(", lat, ",", lon, "),"