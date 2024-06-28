import math
import pandas as pd
import numpy as np
import random
import geopandas as gpd
import matplotlib.pyplot as plt


def creador_Lista(padre1, padre2, numCiudades):
    # Arreglo de celdas
    ListaCiudadesVecinas = {i+1: [] for i in range(numCiudades)}
    
    for padre, otro_padre in zip([padre1, padre2], [padre2, padre1]):  # Recorrer ambos padres simultáneamente 
        for i in range(numCiudades):
            ciudad = padre[i]
            idx1 = [(i-1) % numCiudades, (i+1) % numCiudades]
            idx2 = np.where(np.array(otro_padre) == ciudad)[0]

            vecinas = []

            # Agregar vecinos de padre
            for idx in idx1:
                if padre[idx] not in vecinas:
                    vecinas.append(padre[idx])

            # Agregar vecinos de otro_padre
            for idx in idx2:
                if otro_padre[(idx-1) % numCiudades] not in vecinas:
                    vecinas.append(otro_padre[(idx-1) % numCiudades])
                if otro_padre[(idx+1) % numCiudades] not in vecinas:
                    vecinas.append(otro_padre[(idx+1) % numCiudades])

            # Ciudades vecinas no repetidas
            ListaCiudadesVecinas[ciudad] = vecinas

    return ListaCiudadesVecinas

def edge_recombination(Padre1, Padre2, numCiudades):
    Hijos = np.zeros(numCiudades, dtype=int)

    # Crear lista de ciudades vecinas
    ListaCiudadesVecinas = creador_Lista(Padre1, Padre2, numCiudades)

    # Seleccionar ciudad inicial
    ciudadActual = Padre1[0] if random.random() < 0.5 else Padre2[0]
    Hijos[0] = ciudadActual
    
    #Recorrer las ciudades
    for i in range(1, numCiudades):
        for lista in ListaCiudadesVecinas.values():
            if ciudadActual in lista:
                lista.remove(ciudadActual)

        #Ciudades vecinas de la ciudad actual
        vecindarioActual = ListaCiudadesVecinas[ciudadActual]
        if not vecindarioActual:
            #Determinar las ciudades no visitadas 
            todas_las_ciudades = set(range(1, numCiudades + 1))
            ciudades_visitadas = set(Hijos[:i])
            ciudades_no_visitadas = list(todas_las_ciudades - ciudades_visitadas)
            ciudadActual = random.choice(ciudades_no_visitadas)
        else:
            # Seleccionar la ciudad con el menor número de conexiones
            conexiones = [len(ListaCiudadesVecinas[vecino]) for vecino in vecindarioActual]
            min_conexiones = min(conexiones)
            mejores_vecinos = [vecindarioActual[idx] for idx, conex in enumerate(conexiones) if conex == min_conexiones]
            ciudadActual = random.choice(mejores_vecinos)
        
        Hijos[i] = ciudadActual
    
    return Hijos

def mutacion(hijo, pM):
    if random.random() < pM:
        idx1, idx2 = random.sample(range(len(hijo)), 2)
        hijo[idx1], hijo[idx2] = hijo[idx2], hijo[idx1]
    return hijo

#esta funcion calcula la distancia entre dos puntos en la tierra // Se puede usar la libreria haversine para hacerlo más fácil
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2]) # Convertir a radianes
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad # Diferencia de latitud y longitud en radianes 
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2 # Fórmula de Haversine (distancia entre los puntos)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) # Calcular el ángulo entre los puntos
    return R * c # Distancia entre los puntos en kilómetros

#########################################################################################################################################################

# Coordenadas de las 32 entidades federativas de México
lat_and_lon_entidades = {
    (21.7013073,-102.3163765): "Aguascalientes",
    (32.6282599,-115.250378) : "Baja California",    #B
    (24.0761292,-110.3673995) : "Baja California Sur",#B
    (19.8140443, -90.5038872) : "Campeche",
    (16.5591606, -93.023166) : "Chiapas",
    (28.7040064,-105.96896) : "Chihuahua",
    (26.9548687,-101.4639787) : "Coahuila", #B
    (19.2810614,-103.5778798) : "Colima",
    (24.1259979,-104.5338957) : "Durango",
    (20.993517,-101.4805699) : "Guanajuato",
    (16.7618765,-99.7666197) : "Guerrero",
    (20.074479,-98.7827981) : "Hidalgo",
    (20.5255415,-103.309643) : "Jalisco",
    (19.3383818,-99.5712754) : "Estado de México", #B
    (19.8464645,-101.0281372) : "Michoacán",
    (18.8330098,-99.2616462) : "Morelos",
    (21.417062,-104.8393056) : "Nayarit",
    (25.8221153,-100.2588659) : "Nuevo León",
    (17.0007518,-96.7220523) : "Oaxaca",
    (19.1638385,-98.3786678) : "Puebla",
    (20.676179,-100.4088138) : "Querétaro",
    (21.0419331,-86.8745916) : "Quintana Roo", #B
    (22.2568861,-100.9341508) : "San Luis Potosí",
    (24.7669669,-107.469744) : "Sinaloa",
    (29.0899962,-111.0519752) : "Sonora",
    (17.9955072,-92.8198758) : "Tabasco",
    (26.0117829,-98.2297176) : "Tamaulipas",
    (19.531768,-98.1802654) : "Tlaxcala",
    (19.1448114,-96.1863998) : "Veracruz",
    (20.9338584,-89.663073) : "Yucatán", #B
    (22.9002505,-102.6803963) : "Zacatecas",
    (19.4360762, -99.0744832) : "CDMX" #B
}

# Extraer nombres y coordenadas
nombres = list(lat_and_lon_entidades.values()) # Nombres de las entidades en una lista
coordenadas = list(lat_and_lon_entidades.keys()) # Coordenadas de las entidades en una lista

# Crear una matriz de distancias de 32x32
distancias = np.zeros((32, 32)) # Matriz de distancias

# Calcular las distancias y llenar la matriz
for i in range(32):
    for j in range(32):
        lat1, lon1 = coordenadas[i]
        lat2, lon2 = coordenadas[j]
        distancias[i][j] = haversine(lat1, lon1, lat2, lon2)


# Parámetros del algoritmo genético
nG = 400  # Número de generaciones
pM = 0.5  # Probabilidad de mutación
numCiudades = len(nombres)
padres = 500  # Número de padres
#repeticiones = input("Ingrese el numero de repeticiones: ")
repeticiones = 1

lista_repeticiones = []
for i in range(int(repeticiones)):
    # Generar población de padres únicos
    poblacion_padres = []
    distanciasPadres = []

    while len(poblacion_padres) < padres:
        padre = np.random.permutation(range(1, numCiudades+1))
        #Agregar el padre a la población si no está repetido
        if list(padre) not in poblacion_padres:
            poblacion_padres.append(list(padre))

    # Evaluar la población de padres
    for padre in poblacion_padres:
        distancia = sum(distancias[padre[i]-1][padre[(i+1) % numCiudades]-1] for i in range(numCiudades))
        distanciasPadres.append(distancia)

    listaPadres = list(poblacion_padres)
    listaDistPadres = list(distanciasPadres)

    cont = 0
    while cont < nG:
        aleatorios = {i+1: [] for i in range(padres//2)}
        numeros_seleccionados = set()

        for lista in aleatorios.values():
            for _ in range(2):
                numero_aleatorio = random.randint(0, padres - 1)
                while numero_aleatorio in numeros_seleccionados or numero_aleatorio in lista:
                    numero_aleatorio = random.randint(0, padres - 1)
                lista.append(numero_aleatorio)
                numeros_seleccionados.add(numero_aleatorio)

        hijos_generados = []
        distanciaHijos = []

        # Generar hijos
        for i in range(padres // 2):
            padre1 = listaPadres[aleatorios[i+1][0]]
            padre2 = listaPadres[aleatorios[i+1][1]]

            Hijos = edge_recombination(padre1, padre2, numCiudades)

            for j in range(numCiudades):
                if Hijos[j] in Hijos[j+1:]:
                    idx = [i for i, x in enumerate(Hijos) if x == Hijos[j]]
                    for k in range(numCiudades):
                        if k+1 not in Hijos:
                            Hijos[idx[0]] = k+1
                            break
            
            Hijos = mutacion(Hijos, pM)
            hijos_generados.append(Hijos)

            distancia = sum(distancias[Hijos[j]-1][Hijos[(j+1) % numCiudades]-1] for j in range(numCiudades))
            distanciaHijos.append(distancia)

        # Comparar los hijos con los padres
        for i in range(padres//2):
            indice_padre1 = aleatorios[i+1][0]
            indice_padre2 = aleatorios[i+1][1]
            distancia_padre1 = listaDistPadres[indice_padre1]
            distancia_padre2 = listaDistPadres[indice_padre2]
            distancia_hijo = distanciaHijos[i]

            if distancia_padre1 < distancia_padre2:
                if distancia_hijo < distancia_padre2:
                    listaPadres[indice_padre2] = hijos_generados[i]
                    listaDistPadres[indice_padre2] = distancia_hijo
            else:
                if distancia_hijo < distancia_padre1:
                    listaPadres[indice_padre1] = hijos_generados[i]
                    listaDistPadres[indice_padre1] = distancia_hijo

        poblacion_padres = list(listaPadres)
        distanciasPadres = list(listaDistPadres)

        distanciasPadres, poblacion_padres = zip(*sorted(zip(distanciasPadres, poblacion_padres), key=lambda x: x[0]))
        
        cont += 1
    
    #Guardar la distancia del mejor individuo y la permutación del mejor individuo
    lista_repeticiones.append((distanciasPadres[0], poblacion_padres[0]))

#Ordenar la lista de repeticiones
lista_repeticiones = sorted(lista_repeticiones, key=lambda x: x[0])


#Imprimir la peor distancia y la peor permutación
print(f"La peor distancia es: {lista_repeticiones[-1][0]}")
print(f"La peor permutación es: {lista_repeticiones[-1][1]}")


#Imprimir la mejor distancia y la mejor permutación
print(f"La mejor distancia es: {lista_repeticiones[0][0]}")
#Imprimir la mejor permutación
print(f"La mejor permutación es: {lista_repeticiones[0][1]}")


#Desviación estándar de las 10 repeticiones
distancias = [distancia for distancia, _ in lista_repeticiones]
desviacion_estandar = np.std(distancias)
print(f"La desviación estándar de las 10 repeticiones es: {desviacion_estandar}")

#Imprimir la media de las 10 repeticiones
media = np.mean(distancias)
print(f"La media de las 10 repeticiones es: {media}")

#Imprimir el nombre de las entidades federativas en la mejor permutación
ruta = [nombres[i-1] for i in lista_repeticiones[0][1]]

print("Ruta:")
print(" -> ".join(ruta))
#

##########################################################################################################################################
#Mapa
print("\n\n\n")

# Crear un GeoDataFrame con las entidades federativas
gdf_entidades = gpd.GeoDataFrame()
gdf_entidades["Nombre"] = nombres
gdf_entidades["geometry"] = gpd.points_from_xy([coordenada[1] for coordenada in coordenadas], [coordenada[0] for coordenada in coordenadas])

# Crear un GeoDataFrame con la ruta
gdf_ruta = gpd.GeoDataFrame()
gdf_ruta["Nombre"] = ruta
gdf_ruta["geometry"] = gpd.points_from_xy([coordenadas[nombres.index(entidad)][1] for entidad in ruta], [coordenadas[nombres.index(entidad)][0] for entidad in ruta])


# Crear un mapa con las entidades federativas y la ruta
ax = gdf_entidades.plot(figsize=(10, 10), color="white", edgecolor="black")
gdf_ruta.plot(ax=ax, color="red", markersize=10)
ax.set_axis_off()

#Dibujar la ruta
for i in range(len(ruta) - 1):
    ciudad1 = coordenadas[nombres.index(ruta[i])]
    ciudad2 = coordenadas[nombres.index(ruta[i+1])]
    #Dibujar la línea entre las ciudades 
    plt.plot([ciudad1[1], ciudad2[1]], [ciudad1[0], ciudad2[0]], color="blue" , linewidth=1)

#Cargar el mapa de México
mapa_file = r"u_territorial_estados_mgn_inegi_2013\u_territorial_estados_mgn_inegi_2013.shp"
mapa = gpd.read_file(mapa_file)


#Añadir la ruta al mapa 
for i, entidad in enumerate(ruta):
    plt.text(1.05, 0.9-i*0.03, f"{i+1}. {entidad}", transform=ax.transAxes)

#Añadir la distancia total al mapa con 2 decimales
plt.text(1.05, 0.9-len(ruta)*0.03, f"Distancia total: {round(lista_repeticiones[0][0], 2)} km", transform=ax.transAxes)



#Dibujar el mapa en el mismo plot
mapa.boundary.plot(ax=ax, linewidth=.5, color="black")
plt.title("Ruta más corta para visitar las 32 entidades federativas de México")
plt.show()
