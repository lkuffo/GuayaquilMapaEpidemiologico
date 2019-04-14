"""
ANALISIS EXPLORATORIO DE DATOS
"""
import pandas as pd

data = [
    ("Emergencia", pd.read_csv("../../data/ESPOL - EMERGENCIA.csv")),
    ("Hospitalizacion", pd.read_csv("../../data/ESPOL - HOSPITALIZACION.csv")),
    ("Consulta Externa", pd.read_csv("../../data/ESPOL - CONSULTA EXTERNA.csv"))
]

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

        #df.to_csv("../../data/emergency_cleaned_data.csv", index=False)

        print "AGRUPACION POR PARROQUIA"
        print (df[["paciente", "parroquia"]]
               .groupby(["parroquia"])
               .count()
               .sort_values(by="paciente", ascending=False)
               .head(10))


        print "AGRUPACION POR CIE 10"
        print (df[["paciente", "cie_10"]]
               .groupby(["cie_10"])
               .count()
               .sort_values(by="paciente", ascending=False)
               .head(10))

        print (df[["paciente", "cie_10", "parroquia"]]
               .groupby(["cie_10", "parroquia"])
               .count()
               .sort_values(by="paciente", ascending=False)
               .head(10))

        print "\n"

    print len(set(all_sectors))

