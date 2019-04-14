"""
ARCHIVO UTILITARIO PARA EL MAPEO DE CALLES
"""
import re
import string

calles_numeros = [str(x) + "AVA" for x in range(10, 100)]
calles_numeros += [
    "2DA", "3RA", "4TA", "5TA","6TA", "7MA", "8AVA", "9NA", "10MA"
]
calles_numeros_escritos = [
    "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA", "SEXTA", "SEPTIMA", "NOVENA"
]
calles_letras = ["LA " + x for x in string.ascii_uppercase]
calles_letras_aux = [x for x in string.ascii_uppercase]
calles_letras.append("LA CH")
calles_meses = [
    "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]
calles_meses_abreviados = [
    "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"
]

all=string.maketrans('','')

def hasDigit(text):
    return any(c.isdigit() for c in text)

def getDigits(text):
    nodigs = all.translate(all, string.digits)
    return text.translate(all, nodigs)

calles_numeros_aux = [getDigits(x) for x in calles_numeros]
def getNumberCalleOnToken(text):
    for i, calle in enumerate(calles_numeros_aux):
        if text == calle:
            return calles_numeros[i]
    #print "CALLE NUMERICA NO ENCONTRADA. ERROR EN ===> ", text
    return None

def getNumberCalleOnTokenAlternative(text):
    for i, calle in enumerate(calles_numeros_aux):
        if text == calle:
            return "CALLE " + text
    #print "CALLE NUMERICA ALTERNATE NO ENCONTRADA. ERROR EN ===> ", text
    return None

def findEntityMeses(tokens):
    '''
    Formo la entidad en caso de tratarse de una calle de meses
    3 partes: [DIA] DE [MES]
    :param tokens:
    :return:
    '''
    for i,token in enumerate(tokens):
        if token in calles_meses:
            j = i-1
            # BUSCO EL DIA CORRESPONDIENTE AL MES
            while not tokens[j].isdigit():
                if j == 0:
                    return None
                j -= 1
            return tokens[j] + " DE " + token
        if token in calles_meses_abreviados:
            j = i-1
            while not tokens[j].isdigit():
                if j == 0:
                    return None
                j -= 1
            return tokens[j] + " DE " + calles_meses[calles_meses_abreviados.index(token)]
    return None

def findEntity(part, part_tokens):
    filtered_tokens = part_tokens[:]
    #print "ENTIDAD A BUSCAR: ", part
    isCalleMeses = findEntityMeses(part_tokens) # Suposicion: Es una calle de mes
    if isCalleMeses:
        if isCalleMeses == "4 DE NOVIEMBRE":
            isCalleMeses = "Carlos Guevara Moreno"
        #print "ES UNA ENTIDAD DE MES"
        return isCalleMeses, None
    for token in part_tokens:
        if token == "ENTRE": # Dont care
            filtered_tokens.remove(token)
            continue
        if token == "LA": # Dont care
            filtered_tokens.remove(token)
            continue
        if token == "EL": # Dont care
            filtered_tokens.remove(token)
            continue
        if token.startswith("0"):
            filtered_tokens.remove(token)
            continue
        if hasDigit(token): # Suposicion: Es una calle numerica
            sanitazed_token = token
            if not token.isdigit():
                sanitazed_token = getDigits(token)
            if len(sanitazed_token) < 3:
                entity = getNumberCalleOnToken(sanitazed_token)
                entity_alt = getNumberCalleOnTokenAlternative(sanitazed_token)
                if entity:
                    #print "ES UNA ENTIDAD DE NUMERO"
                    return entity, entity_alt
            else:
                filtered_tokens.remove(token)
        if len(token) == 1 and token.isalpha(): # Suposicion: Es una calle de letra
            #print "ES UNA ENTIDAD DE LETRA"
            return calles_letras[calles_letras_aux.index(token)], None
    # Si no es ninguna de las suposiciones, devuelvo el ultimo elemento de los tokens
    # Que probabelemente, sea el mas representativo
    #print "ES UNA ENTIDAD NORMAL"
    if len(filtered_tokens) == 0:
        return "NOT FOUND", None
    return max(filtered_tokens, key=len), None

def tokenize(text):
    p1, p2 = text.split(" Y ")[-2:]
    p1_tokens = p1.split(" ")
    p2_tokens = p2.split(" ")
    entity_1, entity_alt_1 = findEntity(p1, p1_tokens)
    #print "ENTIDAD: ", entity_1, entity_alt_1
    entity_2, entity_alt_2 = findEntity(p2, p2_tokens)
    #print "ENTIDAD: ", entity_2, entity_alt_2
    return entity_1, entity_2, entity_alt_1, entity_alt_2

def mapear_calles(direccion, data, streets):
    direccion = direccion.upper().replace(".", "").replace(";", " ").replace(":", " ")
    token1, token2, token1_alt, token2_alt = tokenize(direccion)
    reg_a = r"" + re.escape(token1) + r".*" + re.escape(token2)
    reg_b = None
    reg_c = None
    if token1_alt:
        reg_b = r"" + re.escape(token1_alt) + r".*" + re.escape(token2)
    elif token2_alt:
        reg_c = r"" + re.escape(token1) + r".*" + re.escape(token2_alt)
    for i, street in enumerate(streets):
        match = re.search(reg_a, street)
        if match:
            return data.iloc[i, 3], data.iloc[i, 2]
        if reg_b:
            match = re.search(reg_b, street)
            if match:
                return data.iloc[i, 3], data.iloc[i, 2]
        if reg_c:
            match = re.search(reg_c, street)
            if match:
                return data.iloc[i, 3], data.iloc[i, 2]
    #print "NO SE PUDO ENCONTRAR ", direccion
    return 0, 0


# if __name__ == '__main__':
# 
#     data = pd.read_csv("../../data/calles_guayaquil.csv", sep=";", decimal=",")
#     streets = data['SIMPLESPEL'].values
#     lat, lon = mapear_calles("15 DE SEP Y PSJE", data, streets)
#     #print lat, lon
    # #print
    # lat, lon = mapear_calles("guerrero valenzuela y el oro", data, streets)
    # #print lat, lon
    # #print
    # lat, lon = mapear_calles("el tungurahua y los chambers", data, streets)
    # #print lat, lon
    # #print
    # lat, lon = mapear_calles("argentina entre la 39 y 40", data, streets)
    # #print lat, lon
    # #print
    #
    # lat, lon = mapear_calles("carchi y azuay  n 3905", data, streets)
    # #print lat, lon
    # #print
    #
    # lat, lon = mapear_calles("oriente y la 13 ava", data, streets)
    # #print lat, lon
    # #print
    #
    # lat, lon = mapear_calles("capitan najera y chimborazo", data, streets)
    # #print lat, lon
    # #print
    #
    # lat, lon = mapear_calles("fancisco de marco 1920 y jose mascote", data, streets)
    # #print lat, lon
    # #print
