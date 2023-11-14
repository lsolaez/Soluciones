import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Nombre del archivo CSV
nombre_archivo = 'demanda.csv'

# Verificar si el archivo ya existe
archivo_existe = False
try:
    with open(nombre_archivo, 'r'):
        archivo_existe = True
except FileNotFoundError:
    archivo_existe = False

# Cargar el DataFrame desde el archivo CSV
demanda_df = pd.read_csv(nombre_archivo)

# Función para calcular el ancho de banda hasta el día especificado
def calcular_ancho_banda(demanda_df, day, bandwidth_day1):
    # Implementa el método de Jacobi para llegar al día especificado
    for d in range(2, day + 1):
        old_bandwidth_day_n = bandwidth_day1.copy()
        for i in range(len(bandwidth_day1)):
            bandwidth_day1[i] = bandwidth_day1[i] + demanda_df.iloc[d - 1, i] * old_bandwidth_day_n[i]

    return bandwidth_day1

# Función para imprimir el ancho de banda actual (último día calculado)
def imprimir_ancho_banda_actual():
    last_day_bandwidth = calcular_ancho_banda(demanda_df, len(demanda_df), bandwidth_day1)
    st.write(f"Ancho de banda actual (último día calculado - Día {len(demanda_df)+1}): {last_day_bandwidth}")

# Función para añadir un nuevo día
def agregar_nuevo_dia():
    nueva_demanda_A = st.number_input("Demanda en la Torre A (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)
    nueva_demanda_B = st.number_input("Demanda en la Torre B (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)
    nueva_demanda_C = st.number_input("Demanda en la Torre C (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)

    # Datos de la nueva fila
    nueva_fila = [nueva_demanda_A, nueva_demanda_B, nueva_demanda_C]

    # Añadir la nueva fila al DataFrame
    demanda_df = demanda_df.append(pd.Series(nueva_fila, index=demanda_df.columns), ignore_index=True)

    # Guardar el DataFrame actualizado en el archivo CSV
    demanda_df.to_csv(nombre_archivo, index=False)

    imprimir_ancho_banda_actual()

# Función para eliminar un día
def eliminar_dia():
    dia_a_eliminar = st.number_input("Ingrese el día que desea eliminar: ", min_value=1, max_value=len(demanda_df))

    # Eliminar la fila correspondiente al día especificado
    demanda_df.drop(index=int(dia_a_eliminar) - 1, inplace=True)

    # Guardar el DataFrame actualizado en el archivo CSV
    demanda_df.to_csv(nombre_archivo, index=False)

    # Calcular el ancho de banda actualizado
    imprimir_ancho_banda_actual()

# Función para editar un día
def editar_dia():
    dia_a_editar = st.number_input("Ingrese el día que desea editar: ", min_value=1, max_value=len(demanda_df))
    nueva_demanda_A = st.number_input("Nueva demanda en la Torre A (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)
    nueva_demanda_B = st.number_input("Nueva demanda en la Torre B (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)
    nueva_demanda_C = st.number_input("Nueva demanda en la Torre C (porcentaje entre 0 y 1): ", min_value=0.0, max_value=1.0)

    # Actualizar los valores de la fila correspondiente al día especificado
    demanda_df.iloc[int(dia_a_editar) - 1] = [nueva_demanda_A, nueva_demanda_B, nueva_demanda_C]

    # Guardar el DataFrame actualizado en el archivo CSV
    demanda_df.to_csv(nombre_archivo, index=False)

    # Calcular el ancho de banda actualizado
    imprimir_ancho_banda_actual()

# Función para consultar el ancho de banda hasta un día específico
def consultar_dia():
    dia_a_consultar = st.number_input("Ingrese el día que desea consultar: ", min_value=1, max_value=len(demanda_df))

    # Calcular el ancho de banda hasta el día especificado
    bandwidth_until_day = calcular_ancho_banda(demanda_df, int(dia_a_consultar), bandwidth_day1)
    st.write(f"Ancho de banda hasta el día {int(dia_a_consultar)}: {bandwidth_until_day}")

# Función para predecir el ancho de banda para el día siguiente
def predecir_ancho_banda_siguiente(demanda_df, last_day_bandwidth, bandwidth_day1):
    # Crear la matriz de diseño (X) y el vector de la variable dependiente (y)
    X = np.arange(1, len(demanda_df) + 1).reshape(-1, 1)  # Días
    y = demanda_df.values.reshape(-1, 3)  # Demandas para cada torre

    # Crear y entrenar el modelo de regresión lineal múltiple
    modelo_regresion = LinearRegression()
    modelo_regresion.fit(X, y)

    # Predecir la demanda para el día siguiente
    dia_siguiente = len(demanda_df) + 1
    demanda_prediccion = modelo_regresion.predict([[dia_siguiente]])

    # Calcular el ancho de banda predicho
    predicted_bandwidth = bandwidth_day1 + demanda_prediccion * last_day_bandwidth

    return predicted_bandwidth.flatten()

# Menú principal de Streamlit
while True:
    st.title("Menú Principal")
    opcion = st.selectbox("Seleccione una opción:", ["Mostrar el ancho de banda actual", "Añadir un nuevo día",
                                                     "Eliminar un día", "Editar un día",
                                                     "Consultar el ancho de banda hasta un día",
                                                     "Predecir el ancho de banda para el día siguiente",
                                                     "Salir"])

    if opcion == "Mostrar el ancho de banda actual":
        imprimir_ancho_banda_actual()
    elif opcion == "Añadir un nuevo día":
        agregar_nuevo_dia()
    elif opcion == "Eliminar un día":
        eliminar_dia()
    elif opcion == "Editar un día":
        editar_dia()
    elif opcion == "Consultar el ancho de banda hasta un día":
        consultar_dia()
    elif opcion == "Predecir el ancho de banda para el día siguiente":
        last_day_bandwidth = calcular_ancho_banda(demanda_df, len(demanda_df), bandwidth_day1)
        predicted_bandwidth = predecir_ancho_banda_siguiente(demanda_df, last_day_bandwidth, bandwidth_day1)
        st.write(f"Ancho de banda predicho para el día siguiente: {predicted_bandwidth}")
    elif opcion == "Salir":
        break
