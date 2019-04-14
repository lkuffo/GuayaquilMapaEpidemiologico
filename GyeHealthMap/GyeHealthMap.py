# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, session, jsonify, request
from CONSTANTS import CONSTANTS
from MapGenerator import MapGenerator
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask("GyeHealthMap")
app.secret_key = 'shhhhhhhh'

@app.route('/')
def init():
    return render_template('init.html',
                           active="init")

@app.route('/institutions')
def institutions():
    c = CONSTANTS(APP_STATIC)
    return render_template('institutions.html',
                           active="institutions",
                           institutions=c.institutions)

@app.route('/contacto')
def contact():
    return render_template('contacto.html',
                           active="contact")

@app.route('/healthmap/<string:institution_id>')
def healthMap(institution_id):
    c = CONSTANTS(APP_STATIC, load_cie10=True)
    return render_template('healthmap.html',
                           active="institutions",
                           institution=c.findInstitution(institution_id),
                           capitulos=c.capitulos,
                           agrupacion=c.agrupaciones,
                           cie10=c.getCIE10forInstitution(institution_id))

@app.route('/obtainMeasures', methods=["POST"])
def obtainMeasures():
    startDate = request.form.get("start")
    endDate = request.form.get("end")
    institution = request.form.get("institution")
    edad = request.form.get("edad")
    capitulo = request.form.get("capitulo")
    agrupacion = request.form.get("agrupacion")
    cie10 = request.form.get("cie10")

    cleanedCie10 = None
    cleanedAgrupacion = None
    cleanedCapitulo = None
    if cie10 != "" and cie10:
        cleanedCie10 = cie10.split("-")[0]
    if agrupacion != "" and agrupacion:
        cleanedAgrupacion = agrupacion.split(":")[0]
    if capitulo != "" and capitulo:
        cleanedCapitulo = capitulo.split(":")[0]

    MG = MapGenerator(app, institution, cleanedCapitulo, cleanedAgrupacion, cleanedCie10, startDate, endDate, edad)
    geojson, filterUsed = MG.generateMap()

    mapTitle = filterUsed
    if filterUsed == "cie10":
        mapTitle = "Pacientes de: " + cie10
    elif filterUsed == "capitulo":
        mapTitle = "Pacientes de: " + capitulo
    elif filterUsed == "agrupacion":
        mapTitle = "Pacientes de: " + agrupacion

    return jsonify(
        gyeData = geojson,
        mapTitle = mapTitle
    )


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
