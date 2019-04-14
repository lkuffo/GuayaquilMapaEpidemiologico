# coding=utf-8
import os
import pandas as pd
from flask import current_app


class CONSTANTS:
    def __init__(self, APP_STATIC, load_cie10=False):

        self.institutions = [
            {
                "id": "all",
                "name": u"TODOS LOS HOSPITALES",
                "pacientes": 15891,
                "tipo": "N/A",
                "link": "#"
            },
            {
                "id": "hlb",
                "name": u"HOSPITAL LEON BECERRA",
                "pacientes": 15891,
                "tipo": "Infantil",
                "link": "https://www.bspi.org/hospital_leon_becerra.html"
            }
        ]

        self.static = APP_STATIC

        if load_cie10:
            self.capitulos = self.getCapitulos()
            self.agrupaciones = self.getAgrupaciones()

    def getCapitulos(self):
        capitulos = {}
        f = open(self.static + "/cie10/cie_capitulos.csv", "r")
        f.readline()
        for line in f:
            info = line.strip().decode('utf-8').split(",")
            capitulos[info[0]] = {
                "id": info[0],
                "nombre": info[1] + ": " + info[-1],
                "onlyNombre": info[-1],
                "ini": info[2],
                "fin": info[3]
            }
        return capitulos

    def getAgrupaciones(self):
        agrupaciones = {}
        availableAgrupaciones = set()
        f = open(self.static + "/cie10/cie_agrupaciones.csv", "r")
        f.readline()
        for line in f:
            info = line.strip().decode('utf-8').split(",")
            agrupaciones[info[2]] = {
                "id": info[2],
                "nombre": info[2] + ": " + info[1],
                "ini": info[-2][0:],
                "fin": info[-1][0:],
                "onlyNombre": info[1],
                "letra": info[-2][0],
                "intervalo": info[-2] + "|" + info[-1]
            }
        return agrupaciones

    def filterForInstitution(self, CIE10list=()):
        return []

    def getCIE10forInstitution(self, institution_id):
        availableCIE10 = set()
        for file in os.listdir(self.static + "/maps/" + institution_id):
            if ".html" in file:
                availableCIE10.add(file.replace(".html", ""))
        all_points = pd.read_csv(current_app.open_resource("neighboursMapping.csv"))
        allcie10 = all_points["cie10"].values
        for c in allcie10:
            availableCIE10.add(c)
        return availableCIE10

    def findInstitution(self, institution_id):
        for elem in self.institutions:
            if elem["id"] == institution_id:
                return elem

    def getJSONserializable(self):
        return {
            "institutions": self.institutions,
            "capitulos": self.capitulos,
            "agrupaciones": self.agrupaciones
        }