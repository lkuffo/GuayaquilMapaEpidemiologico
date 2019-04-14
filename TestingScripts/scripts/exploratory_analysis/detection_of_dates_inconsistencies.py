# coding=utf-8
import pandas as pd
import unicodedata
import re
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt

data = [
    ("Emergencia", pd.read_csv("../../data/ESPOL - EMERGENCIA.csv")),
    ("Hospitalizacion", pd.read_csv("../../data/ESPOL - HOSPITALIZACION.csv")),
    ("Consulta Externa", pd.read_csv("../../data/ESPOL - CONSULTA EXTERNA.csv"))
]
sectores_bow = {}

inconsistencies = {
    "not_found": 0,
    "barrios": 0,
    "circuitos": 0,
    "distritos": 0,
    "mena": 0,
    "calles": 0
}

sectores = pd.read_csv("../../data/Guayaquil Consolidado - Sheet1.csv")
sectores_adicionales = pd.read_csv("../../data/Sectores de Guayaquil - centro.csv")
text_not_found = []

def normalize_adicionales(text):
    tokens = text.split("-")
    for i, token in enumerate(tokens):
        token = token.replace("barrio ", "").replace("cdal ", "") \
                .replace("cdla", "").replace("precooperativa", "").replace("precoop", "") \
                .replace("prcoop", "").replace("urb", " ").replace("°", "") \
                .replace("bq", " ").replace("coop", "").replace("condm", "") \
                .replace("etapa", "")
        regex = r'[%s]' % re.escape(string.punctuation)  # signsPattern
        token = re.sub(regex, '', token).replace("bq", "").strip()
        tokens[i] = token
    return tokens

def geolocalizar(direccion, barrios, circuitos, distritos, adicionales):
    text = direccion.decode('utf-8', 'replace').encode('ASCII', 'ignore').lower()
    for barrio in barrios:
        if barrio in text:
            if barrio not in sectores_bow:
                sectores_bow[barrio] = 0
            sectores_bow[barrio] += 1
            inconsistencies["barrios"] += 1
            return
    for circuito in circuitos:
        if circuito in text:
            if circuito not in sectores_bow:
                sectores_bow[circuito] = 0
            sectores_bow[circuito] += 1
            inconsistencies["circuitos"] += 1
            return
    for distrito in distritos:
        if distrito in text:
            if distrito not in sectores_bow:
                sectores_bow[distrito] = 0
            sectores_bow[distrito] += 1
            inconsistencies["distritos"] += 1
            return
    for adicional in adicionales:
        if adicional in text:
            if adicional not in sectores_bow:
                sectores_bow[adicional] = 0
            sectores_bow[adicional] += 1
            inconsistencies["mena"] += 1
            return
    if " y " in text:
        inconsistencies["calles"] += 1
        return
    if text not in text_not_found:
        print text
        text_not_found.append(text)
    inconsistencies["not_found"] += 1


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

        barrios = sectores["Sector/Barrio"].values.tolist()
        circuito = sectores["Circuito"].values.tolist()
        distrito = sectores["Distrito"].values.tolist()
        adicionales = sectores_adicionales["sectores"].values.tolist()
        barrios = [normalize_vocals(x) for x in barrios]
        circuito = [normalize_vocals(x) for x in circuito]
        distrito = [normalize_vocals(x) for x in distrito]
        adicionales = [normalize_vocals(x) for x in adicionales]
        adicionales = [normalize_adicionales(x) for x in adicionales]
        adicc = []
        for adicional in adicionales:
            adicc += adicional
        direcciones = df["direccion"].values.tolist()
        for direccion in direcciones:
            geolocalizar(direccion, barrios, circuito, distrito, adicc)

    print inconsistencies
    print "Total: ", sum(inconsistencies.values())

    print len(set(text_not_found))

    texto = " ".join(set(text_not_found)).replace("coop", "").replace(" mz ", "").replace(" sl ", "").replace("cdla", "").replace("calle", "").replace("villa", "").replace("sur", "").replace(" la ", "").replace(" km ", "").replace("nn", "").replace(" entre ", "").replace(" urb ", "").replace(" cop ", "").replace("etapa", "").replace(" av ", "").replace("via", "").replace(" lo ", "").replace(" bq ", "").replace(" jon ", "").replace(" el ", "").replace(" de ", "").replace(" los ", "").replace(" las ", "").replace("mz", "").replace(" del ", "").replace("sl", "").replace("solar", "")
    wordcloud = WordCloud().generate(texto)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()






