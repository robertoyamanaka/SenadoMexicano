import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


#Cargamos el dataframe que generamos en pymongo_to_pandas.py
senadores = pd.read_csv('senadores_clean.csv',index_col=0)

# Recodificamos la variable partido
senadores['partido'] = senadores['partido'].apply(lambda x: 'Morena' if 'Movimiento Regeneración Nacional' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PRI' if 'Grupo Parlamentario delPartido Revolucionario Institucional' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PAN' if 'Grupo Parlamentario delPartido Acción Nacional' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PES' if 'Grupo Parlamentario delPartido Encuentro Social' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PVE' if 'Grupo Parlamentario delPartido Verde Ecologista de México' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PRD' if 'Grupo Parlamentario delPartido de la Revolución Democrática' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'PT' if 'Grupo Parlamentario delPartido del Trabajo' in x else x)
senadores['partido'] = senadores['partido'].apply(lambda x: 'MC' if 'Movimiento Ciudadano' in x else x)
# Agregamos una variable del sexo
senadores['sexo'] = senadores['eleccion'].apply(lambda x: '1' if 'Senadora' in x else 0)
#Quitamos a ese senador que no tiene partido politico
senadores = senadores[senadores["partido"].str.contains('Sin Grupo') == False]

#Hay que cambiar eso de elección para que solo queden tres tipos de elección
senadores['eleccion'] = senadores['eleccion'].apply(lambda x: 'Plurinominal' if '56' in x else x)
senadores['eleccion'] = senadores['eleccion'].apply(lambda x: 'Electo Mayoría' if 'Relativa' in x else x)
senadores['eleccion'] = senadores['eleccion'].apply(lambda x: 'Electo Minoría' if 'Minoría' in x else x)

#Vamos a crear nuestra color palette del Pri para usar en la mayoría de nuestros plots
pricolor = ["#006847","#ce1126", "#225a41", "#ac1f2b","#454b3c","#892e31","#aaaaaa","#673c37"]
sns.set_palette(pricolor)

#Ahora sí graficamos y comparamos variables

#Veamos quienes son los partidos con mejores estudios
plt.figure(figsize=(12,6))
plt.title('Titulos universitarios per partido', fontsize=20)
sns.boxplot(x='partido',y='titulos_univ',data=senadores)
plt.xlabel("Partidos")
plt.ylabel("Titulos Universitarios")
plt.show()

#Como está la composición de num de senadores per partido
plt.figure(figsize=(12,6))
plt.title('Tipo de elección per partido', fontsize=20)
sns.countplot(x='partido',data=senadores,hue='eleccion')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.show()

#Quien tiene los senadores más veteranos
sns.boxplot(x='partido',y=senadores['num_diputaciones'] + senadores['num_senadurias'],data=senadores)
plt.title('Qué tan veteranos son los senadores de cada partido?', fontsize=16)
plt.ylim(0, 10)
plt.show()

#Veamos como está la paridad de género entre los senadores
plt.figure(figsize=(12,6))
plt.title('Tipo de elección per sexo', fontsize=20)
sns.countplot(x='eleccion',data=senadores,hue='sexo')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.show()

#Qué partido tiene los senadores con más chapulines
chapulines = senadores[['partido','PRI_prev', 'PAN_prev', 'MC_prev','Morena_prev','PT_prev']]
chapulines['PRI_prev'] = chapulines['PRI_prev'].apply(lambda x: 1 if x > 0 else 0)
chapulines['PAN_prev'] = chapulines['PAN_prev'].apply(lambda x: 1 if x > 0 else 0)
chapulines['MC_prev'] = chapulines['MC_prev'].apply(lambda x: 1 if x > 0 else 0)
chapulines['Morena_prev'] = chapulines['Morena_prev'].apply(lambda x: 1 if x > 0 else 0)
chapulines['PT_prev'] = chapulines['PT_prev'].apply(lambda x: 1 if x > 0 else 0)
chapulines = chapulines.groupby(by='partido').sum()
chapulines.iloc[1, 3] = 0
chapulines.iloc[2, 1] = 0
chapulines.iloc[5, 0] = 0
chapulines.iloc[6, 4] = 0
chapulines.loc[:,['PRI_prev', 'PAN_prev', 'MC_prev','Morena_prev','PT_prev']].plot.bar(stacked=True, figsize=(10,7),title='Miembros provenientes de otros partidos')
plt.show()

#Ahora veamos las gráficas que se relacionan con las inasistencias y ausencia en votaciones

#Votaciones ausentes
plt.figure(figsize=(12,4))
plt.title('Distribución de las votaciones ausentes', fontsize=20)
sns.distplot(senadores['votaciones_ausente'],kde=False,bins=20)
plt.show()

#Inasistencias
plt.figure(figsize=(12,4))
plt.title('Distribución de las inasistencias', fontsize=20)
sns.distplot(senadores['justificadas'],kde=False,bins=30)
plt.xlabel("Inasistencias")
plt.show()

#Vamos a ver quien es ese caso outlier con más de 50 inasistencias
print(senadores[senadores['justificadas']>50])
#Felicidades Don Carlos Aceves del Olmo

#Que tan marcada es la relacion entre inasistencias y votaciones que faltan
sns.scatterplot(x='justificadas',y='votaciones_ausente',data=senadores)
plt.show()
#Podemos ver que es bastante parecida entonces podemos comparar otras variables con cualquiera de las 2

#Veamos las faltas por partido político
plt.figure(figsize=(12,6))
plt.title('Inasistencias per partido', fontsize=20)
sns.swarmplot(x='partido',y='justificadas',data=senadores,hue='sexo')
plt.xlabel("Partidos")
plt.ylabel("Inasistencias")
plt.show()


#Elección contra las inasistencias separado por sexo
plt.figure(figsize=(12,6))
plt.title('Tipo de elección contra inasistencias', fontsize=20)
sns.barplot(x='eleccion',y='justificadas',data=senadores,hue='sexo')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.show()

#Vemos que los hombres electos son más faltistas. Para el caso de los pluris no se puede decir a primera mano por la alta varianza


#Veamos las intervenciones por partido político
plt.figure(figsize=(12,6))
plt.title('Inasistencias per sexo', fontsize=20)
sns.boxplot(x='sexo',y='tot_intervenciones',data=senadores)
plt.xlabel("Partidos")
plt.ylabel("Intervenciones")
plt.show()

#Veamos si existe una relación entre las intervenciones y las votaciones en las que está ausente
sns.lmplot(x='tot_intervenciones', y='votaciones_ausente', hue='sexo', data=senadores, fit_reg=False)
plt.xlabel("Intervenciones")
plt.ylabel("Votaciones Ausente")
plt.show()
#No parece haber una distinción por sexo, pero si hay una relación para valores más extremos entre ambas variables

#Veamos si existe una relación entre veteranez y las inasistencias
sns.scatterplot(x=senadores['num_diputaciones']+senadores['num_senadurias'],y='votaciones_ausente',data=senadores)
#No parece haber una relación...

#Veamos en promedio cuanto falta el senador de cada estado
inas_estados=senadores[['estado','justificadas']].groupby(by='estado').mean().reset_index()
inas_estados['estado_peque']=inas_estados['estado'].apply(lambda x: x[:4])
inas_estados.iloc[2, 2] = 'BS'
inas_estados.iloc[4, 2] = 'Chia'
plt.figure(figsize=(20,4))
sns.barplot(x='estado_peque',y='justificadas',data=inas_estados)
plt.show()
#Parece que sí hay una clara distinción entre los estados

#Hay alguna diferencia según el número de comisiones al cual pertenezcan?
comisiones=senadores[['Integrante: ','Presidente(a): ','Secretario(a): ','votaciones_ausente']]
comisiones = comisiones.dropna()
comisiones['suma_comisiones']=comisiones['Integrante: ']+comisiones['Presidente(a): ']+comisiones['Secretario(a): ']
comisiones.dtypes
sns.lmplot(x='suma_comisiones', y='votaciones_ausente', data=comisiones, fit_reg=False)
plt.show()

#No realmente, pero sí vemos en cuantas comisiones en promedio tiene cada uno

