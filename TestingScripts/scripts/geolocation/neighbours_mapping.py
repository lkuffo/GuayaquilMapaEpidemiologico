# coding=utf-8
"""
ARCHIVO PRINCIPAL PARA MAPEAR DE DIRECCIONES A SECTORES DE GUAYAQUIL
"""
import pandas as pd
import unicodedata
import re
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from mapear_calles import mapear_calles
import numpy as np
import operator

data = [
    ("Emergencia", pd.read_csv("../../data/ESPOL - EMERGENCIA.csv")),
    ("Hospitalizacion", pd.read_csv("../../data/ESPOL - HOSPITALIZACION.csv")),
    ("Consulta Externa", pd.read_csv("../../data/ESPOL - CONSULTA EXTERNA.csv"))
]

streets_data = pd.read_csv("../../data/calles_guayaquil.csv", sep=";", decimal=",")
streets = streets_data['SIMPLESPEL'].values

sectores_bow = {}

inconsistencies = {
    "sector": 0,
    "parroquia": 0,
    "sectorAdicional": 0,
    "sectorGeneral": 0,
    "calles": 0,
    "not_found": 0,
}
#
# fx = open("streets_address_file.csv", "w")
#

top_barrio = {

}

sectors_data = pd.read_csv("../../data/Guayaquil - Mapeo - Sectores.csv", dtype=str)
sectors_data = sectors_data.replace(np.nan, '', regex=True)
text_not_found = []


def normalize_adicionales(text):
    tokens = text.split("-")
    for i, token in enumerate(tokens):
        regex = r'[%s]' % re.escape(string.punctuation)  # signsPattern
        token = re.sub(regex, '', token).strip()
        token = token.replace("barrio ", "").replace("cdal ", "") \
                .replace("cdla", "").replace("precooperativa", "").replace("precoop", "") \
                .replace("prcoop", "").replace("urb ", " ").replace("°", "") \
                .replace("bq", " ").replace("coop", "").replace("condm", "") \
                .replace("etapa", "").replace("urbanizacion", "").strip()
        token = re.sub(' +', ' ', token)
        tokens[i] = token
    return tokens

def buscar_sector(text, sectores, n_grams):
    z = 0
    max_iteration = len(max(sectores,key=len))
    for iteration in range(0, max_iteration):
        if iteration == 0:
            for z, sector in enumerate(sectores):
                for token in sector:
                    if token in text:
                        if token not in sectores_bow:
                            sectores_bow[token] = 0
                        sectores_bow[token] += 1
                        inconsistencies["sector"] += 1
                        return True, z
            #sectores = filter(lambda x: len(x) != 1, sectores)
    return False, z

def geolocalizar(direccion, parroquias, sectores_adicionales,
                 sectores_generales, sectores, shapeNames=[]):
    text = direccion.decode('utf-8', 'replace').encode('ASCII', 'ignore').lower()
    if " y " in text:
        try:
            lat,lon = mapear_calles(text, streets_data, streets)
            if lat != 0:
                inconsistencies["calles"] += 1
                return str(lat) + "|" + str(lon)
            # print direccion, "\t\t\t\t", lat, "|", lon
            # fx.write(direccion + "@" + str(lat) + "@" + str(lon) + "\n")
        except Exception as e:
            print direccion, "ERROR \n\n"

    found, z = buscar_sector(text, sectores, 5)
    if found:
        return shapeNames[z]

    for z, sectorGeneral in enumerate(sectores_generales):
        if sectorGeneral in text and sectorGeneral != "":
            if sectorGeneral not in sectores_bow:
                sectores_bow[sectorGeneral] = 0
            sectores_bow[sectorGeneral] += 1
            inconsistencies["sectorGeneral"] += 1
            return shapeNames[z]

    for z, sectorAdicional in enumerate(sectores_adicionales):
        if sectorAdicional in text and sectorAdicional != "":
            if sectorAdicional not in sectores_bow:
                sectores_bow[sectorAdicional] = 0
            sectores_bow[sectorAdicional] += 1
            inconsistencies["sectorAdicional"] += 1
            return shapeNames[z]

    for z, parroquia in enumerate(parroquias):
        if parroquia in text and parroquia != "":
            if parroquia not in sectores_bow:
                sectores_bow[parroquia] = 0
            sectores_bow[parroquia] += 1
            inconsistencies["parroquia"] += 1
            return shapeNames[z]

    if text not in text_not_found:
        text_not_found.append(text)
    #print text
    inconsistencies["not_found"] += 1
    return "NOT_FOUND"

def normalize_vocals(text):
    text = text.decode('utf-8', 'replace')
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').lower()


if __name__ == '__main__':

    all_sectors = []
    # Numero de Registros
    for name, df in data[0:1]:
        all_sectors += df["cie_10"].values.tolist()
        print name
        row_n = len(df)
        print row_n

        missing_data_address = df[df["direccion"].apply(lambda x: len(x) < 5)]
        print len(missing_data_address)

        missing_data_cie10 = df[df['cie_10'].apply(lambda x: len(str(x)) < 2)]
        print len(missing_data_cie10)

        # Dropping Missing Data
        df.drop(missing_data_address.index, inplace=True)
        df.drop(missing_data_cie10.index, inplace=True, errors='ignore')

        shapeNames = sectors_data["ShapeName"].values.tolist()
        parroquias = sectors_data["Parroquia"].values.tolist()
        sectoresAdicionales = sectors_data["SectorAdicional"].values.tolist()
        sectoresGenerales = sectors_data["SectorGeneral"].values.tolist()
        sectores = sectors_data["Sector"].values.tolist()
        parroquias = [normalize_vocals(x) for x in parroquias]
        sectoresAdicionales = [normalize_vocals(x) for x in sectoresAdicionales]
        sectoresGenerales = [normalize_vocals(x) for x in sectoresGenerales]
        sectores = [normalize_vocals(x) for x in sectores]
        sectores = [normalize_adicionales(x) for x in sectores]

        direcciones = df["direccion"].values.tolist()
        cie_10 = df["cie_10"].values.tolist()

        f = open("neughboursMappingV2.csv", "w")
        f.write("shapeName,cie10\n")

        for j, direccion in enumerate(direcciones):
            shapeName = geolocalizar(
                direccion,
                parroquias,
                sectoresAdicionales,
                sectoresGenerales,
                sectores,
                shapeNames=shapeNames,
            )
            # if shapeName == "":
            #     shapeName = "NOT_FOUND"
            cie10Mapping = cie_10[j]
            f.write(shapeName + "," + cie10Mapping + "\n")
        f.close()


    # exit()
    print inconsistencies

    #print sectores_bow
    # sorted_x = sorted(sectores_bow.items(), key=operator.itemgetter(1))
    # for k in sorted_x:
    #     print k

    #print "Total: ", sum(inconsistencies.values())

    #print len(set(text_not_found))
    #
    # texto = " ".join(set(text_not_found)).replace("coop", "").replace(" mz ", "").replace(" sl ", "").replace("cdla", "").replace("calle", "").replace("villa", "").replace("sur", "").replace(" la ", "").replace(" km ", "").replace("nn", "").replace(" entre ", "").replace(" urb ", "").replace(" cop ", "").replace("etapa", "").replace(" av ", "").replace("via", "").replace(" lo ", "").replace(" bq ", "").replace(" jon ", "").replace(" el ", "").replace(" de ", "").replace(" los ", "").replace(" las ", "").replace("mz", "").replace(" del ", "").replace("sl", "").replace("solar", "")
    # print texto
    # wordcloud = WordCloud().generate(texto)
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()



