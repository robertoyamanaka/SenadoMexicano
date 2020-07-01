import pandas as pd
import numpy as np
from pymongo import MongoClient

client = MongoClient('localhost',port=27017)

db = client['senado']

# Nombre de las colecciones que vamos a acceder creadas en info_senadores.py
col_semblanzas = db['semblanzas']
col_personal = db['personal']
col_comisiones = db['comisiones']
col_intervenciones = db['intervenciones']
col_votaciones = db['votaciones']
col_asistencias = db['asistencias']

# Limpiando y guardando la data

# Limpiamos los \r\n en los detalles de trayectoria
col_semblanzas.update_many(
    {},
    {"$pull":{'detalle_trayectoria':{
        "$regex": ".*\r\n.*"
    }
    }
    }
)

# Obtengamos cada detalle_trayectoria per trayectoria per senador

detalles_trayectoria = col_semblanzas.aggregate([
    {
        "$project": {
        "clave_senador":"$clave_senador",
        "trayectoria":"$trayectoria",
        "detalle_trayectoria":"$detalle_trayectoria"
        }
    },
    {"$unwind": "$detalle_trayectoria"}
])

# Transformamos los datos de la trayectoria en un df
detalles_trayectoria = pd.DataFrame(list(detalles_trayectoria))

# Transformamos los datos personales a un df
detalles_personal = pd.DataFrame(list(col_personal.find()))

# Obtengamos cada comision per cargo_comision per senador
detalles_comisiones = col_comisiones.aggregate([

    {
        "$project": {
        "clave_senador":"$clave_senador",
        "cargo_comision":"$cargo_comision",
        "comisiones":"$comisiones"
        }
    },
    {"$unwind":"$comisiones"}
])
# Transformamos los datos de comisión a un df
detalles_comisiones = pd.DataFrame(list(detalles_comisiones))

# Sacamos el total de intervenciones por Senador
detalles_intervenciones = pd.DataFrame(list(col_intervenciones.find()))

# Sacamos las votaciones por Senador
detalles_votaciones = pd.DataFrame(list(col_votaciones.find()))

# Sacamos las asistencias por Senador
detalles_asistencias = pd.DataFrame(list(col_asistencias.find()))

# Creamos el dataframe al cual le estaremos agregando nuestra data del webscrapping ya formateada
senadores = detalles_personal
senadores.drop('_id',axis=1,inplace=True)
senadores['clave_senador'] = pd.to_numeric(senadores['clave_senador'])


# Ok... ahora si nos vamos a encargar de extraer cosas de la semblanza
# Lo tenemos que hacer de esta forma porque hay NA
form_academica = detalles_trayectoria[detalles_trayectoria["trayectoria"].str.contains('acad', na=False)]


# Se cuentan los grados de estudios superiores con los que cuenta un senador
titulos = ['Lic', 'Maes','Ingen','Doct']
edu_superior = form_academica[form_academica["detalle_trayectoria"].str.contains('|'.join(titulos), na=False)]
edu_superior['titulos_univ'] = 1
edu_superior = edu_superior.groupby(by="clave_senador").sum().reset_index()
edu_superior = edu_superior[['clave_senador','titulos_univ']]
# También cambiemos la clave del senador a num de una vez
edu_superior['clave_senador'] = pd.to_numeric(edu_superior['clave_senador'])
# La agregamos al dataframe de senadores
senadores = pd.merge(senadores,edu_superior,how='left', on='clave_senador')
senadores['titulos_univ'].fillna(0, inplace=True)


# Se obtienen las veces que antes ha sido senador
# Primero para los casos pasados de senador
senadurias = detalles_trayectoria[detalles_trayectoria["detalle_trayectoria"].str.contains("Sena",na=False)]
# Evitamos capturar un "candidato a senador jajajja"
senadurias = senadurias[senadurias["detalle_trayectoria"].str.contains('Candi') == False]
# Como la senaduría es un cargo federal vienen acompañadas de su legislatura
senadurias['num_senadurias'] = senadurias['detalle_trayectoria'].str.count('LI') + senadurias['detalle_trayectoria'].str.count('LV') + senadurias['detalle_trayectoria'].str.count('LX')
senadurias = senadurias[['clave_senador','num_senadurias']]
senadurias = senadurias.groupby(by="clave_senador").sum().reset_index()
# También cambiemos la clave del senador a num de una vez
senadurias['clave_senador'] = pd.to_numeric(senadurias['clave_senador'])
# La agregamos al dataframe de senadores
senadores = pd.merge(senadores,senadurias,how='left', on='clave_senador')
senadores['num_senadurias'].fillna(0, inplace=True)



# Ahora vamos por los que fueron diputados
# Primero para los casos pasados de senador
diputaciones = detalles_trayectoria[detalles_trayectoria["detalle_trayectoria"].str.contains("Dipu",na=False)]
# Evitamos capturar un "candidato a diputado jajajja"
diputaciones = diputaciones[diputaciones["detalle_trayectoria"].str.contains('Candi') == False]
diputaciones['num_diputaciones'] = diputaciones['detalle_trayectoria'].str.count('LI') + diputaciones['detalle_trayectoria'].str.count('LV') + diputaciones['detalle_trayectoria'].str.count('LX')
# Como no solo hay diputados a niveles federales en muchas semblanzas venían casos como  'diputado local' entonces tenemos que capturar esos
diputaciones['num_diputaciones'] = np.where(diputaciones['num_diputaciones'] == 1, diputaciones['num_diputaciones'],1)
diputaciones = diputaciones[['clave_senador','num_diputaciones']]
diputaciones = diputaciones.groupby(by="clave_senador").sum().reset_index()
# También cambiemos la clave del senador a num de una vez
diputaciones['clave_senador'] = pd.to_numeric(diputaciones['clave_senador'])
# La agregamos al dataframe de senadores
senadores = pd.merge(senadores,diputaciones,how='left', on='clave_senador')
senadores['num_diputaciones'].fillna(0, inplace=True)

# Ahora vamos por los que fueron gobernadores
gobernadores = detalles_trayectoria[detalles_trayectoria["detalle_trayectoria"].str.contains("Gobernad",na=False)]
# Evitamos capturar un "candidato a gobernador jajajja"
gobernadores = gobernadores[gobernadores["detalle_trayectoria"].str.contains('Candi') == False]
gobernadores['num_gobernador'] = 1
gobernadores = gobernadores.groupby(by="clave_senador").sum().reset_index()
gobernadores = gobernadores[['clave_senador','num_gobernador']]
# También cambiemos la clave del senador a num de una vez
gobernadores['clave_senador'] = pd.to_numeric(gobernadores['clave_senador'])
# La agregamos al dataframe de senadores
senadores = pd.merge(senadores,gobernadores,how='left', on='clave_senador')
senadores['num_gobernador'].fillna(0, inplace=True)

# Ahora saquemos en los partidos en los que ha andado y que tanto se involucraron con su partido
detalles_trayectoria['PRD_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'PRD' in x else 0)
detalles_trayectoria['Morena_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'Morena' in x else 0)
detalles_trayectoria['PRI_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'PRI' in x else 0)
detalles_trayectoria['PAN_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'PAN' in x else 0)
detalles_trayectoria['Verde_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'Verde' in x else 0)
detalles_trayectoria['MC_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'MC' in x else 0)
detalles_trayectoria['PT_prev'] = detalles_trayectoria["detalle_trayectoria"].apply(lambda x: 1 if 'PT' in x else 0)
partidos = detalles_trayectoria[['clave_senador','PRD_prev','PRI_prev','PAN_prev','Verde_prev','MC_prev','Morena_prev','PT_prev']].groupby(by='clave_senador').sum().reset_index()
partidos['clave_senador'] = pd.to_numeric(partidos['clave_senador'])
# La agregamos al dataframe de senadores
senadores = pd.merge(senadores,partidos,how='left', on='clave_senador')
senadores['PRD_prev'].fillna(0, inplace=True)
senadores['PRI_prev'].fillna(0, inplace=True)
senadores['PAN_prev'].fillna(0, inplace=True)
senadores['Verde_prev'].fillna(0, inplace=True)
senadores['PAN_prev'].fillna(0, inplace=True)
senadores['MC_prev'].fillna(0, inplace=True)
senadores['Morena_prev'].fillna(0, inplace=True)
senadores['PT_prev'].fillna(0, inplace=True)


# Ahora falta agregarle la info de las otras tablas (comisiones,intervenciones,votaciones,asistencias)

# Pues como son unas 60 comisiones la verdad por el momento solo meteremos al enorme df de senadores si son presis, integrantes o secretarios en cuantas comisiones
comision_dummies = pd.get_dummies(detalles_comisiones['cargo_comision'])
detalles_comisiones = detalles_comisiones.join(comision_dummies)
detalles_comisiones = detalles_comisiones.groupby(by='clave_senador').sum().reset_index()
detalles_comisiones['clave_senador'] = pd.to_numeric(detalles_comisiones['clave_senador'])
senadores = pd.merge(senadores,detalles_comisiones,how='left', on='clave_senador')

# Ahora agreguemos las intervenciones
detalles_intervenciones = detalles_intervenciones[['clave_senador','tot_intervenciones']]
detalles_intervenciones['clave_senador'] = pd.to_numeric(detalles_intervenciones['clave_senador'])
senadores = pd.merge(senadores,detalles_intervenciones,how='left', on='clave_senador')

# Ahora sus votaciones
detalles_votaciones = detalles_votaciones[['clave_senador','votaciones_ausente']]
detalles_votaciones['clave_senador'] = pd.to_numeric(detalles_votaciones['clave_senador'])
senadores = pd.merge(senadores,detalles_votaciones,how='left', on='clave_senador')

# Por último, las asistencias
detalles_asistencias = detalles_asistencias[['clave_senador','asistencias','ausencias','justificadas']]
detalles_asistencias['clave_senador'] = pd.to_numeric(detalles_asistencias['clave_senador'])
senadores = pd.merge(senadores,detalles_asistencias,how='left', on='clave_senador')


# For more on that, check https://stackoverflow.com/questions/17098654/how-to-store-a-dataframe-using-pandas
senadores.to_csv('senadores_clean.csv')
