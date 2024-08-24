import os
import platform

from laboratorio_POO import (
    ColaboradorTiempoCompleto,
    ColaboradorTiempoParcial,
    GestionColaboradores,
)

def limpiar_pantalla():
    ''' Limpiar la pantalla según el sistema operativo'''
    if(platform.system() == 'Windows'):
        os.system('cls')
    else:
        os.system('clear')
        
def mostrar_menu():
    print("**************** Menú de Gestión de Colaboradores ***************")
    print("1. Agregar colaborador Tiempo Completo")
    print("2. Agregar colaborador Tiempo Parcial")
    print("3. Buscar colaborador por DNI")
    print("4. Actualizar salario de colaborador")
    print("5. Eliminar colaborador")
    print("6. Mostrar todos los colaboradores")
    print("7. Salir")
    print('======================================================')

def agregar_colaborador(gestion, tipo_coloborador):
    try:
        dni = input("Ingrese el DNI:")
        nombre = input("Ingrese Nombre:")
        apellido = input("Ingrese Apellido:")
        edad = int(input("Ingrese Edad:"))
        salario = float(input("Ingrese Salario:"))
        
        if tipo_coloborador == '1':
            departamento = input("Ingrese Departamento:")
            colaborador = ColaboradorTiempoCompleto(dni, nombre, apellido, edad, salario, departamento)
        elif tipo_coloborador == '2':
            horas_semanales = int(input("Ingrese Horas Semanales:"))
            colaborador = ColaboradorTiempoParcial(dni, nombre, apellido, edad, salario, horas_semanales)
        else:
            print("Opción inválida")
            return
        
        gestion.crear_colaborador(colaborador)
        input("Presione enter para continuar...")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def buscar_colaborador_por_dni(gestion):
    try:
        dni = input('Ingrese el DNI del colaborador a buscar: ')
        colaborador = gestion.leer_colaborador(dni)
        if not colaborador:
            print('Colaborador no encontrado')
        else:
            print(colaborador)
    except Exception as e:
        print(f'Error al leer colaborador: {e}')
    input('Presione enter para continuar...')

def actualizar_salario_colaborador(gestion):
    dni = input('Ingrese el DNI del colaborador para actualizar salario: ')
    #TODO agregar try catch para validar la conversion a float4
    salario = float(input('Ingrese el nuevo salario: '))
    gestion.actualizar_colaborador(dni, salario)
    input('Presione enter para continuar...')

def eliminar_colaborador(gestion):
    dni = input('Ingrese el DNI del colaborador a eliminar: ')
    gestion.eliminar_colaborador(dni)

    input('Presione enter para continuar...')

def mostrar_todos_los_colaboradores(gestion):
    gestion.mostrar_colaboradores()

    input('Presione enter para continuar...')

def leer_todos_los_colaboradores(gestion):
    print('---------------------Listado de colaboradores----------------------------')
    try:
        colaboradores = gestion.leer_todos_los_colaboradores()
        for colaborador in colaboradores:
            if isinstance(colaborador, ColaboradorTiempoCompleto):
                print(f'{colaborador.dni}, {colaborador.nombre}, {colaborador.apellido}, {colaborador.departamento}')
            elif isinstance(colaborador, ColaboradorTiempoParcial):
                print(f'{colaborador.dni}, {colaborador.nombre}, {colaborador.apellido} {colaborador.horas_semanales}')
            else:
                print(f'{colaborador}')

    except Exception as e:
        print(f'Error al mostrar los colaboradores: {e}')
    
    input('Presione enter para continuar...')

if __name__ == "__main__":

    archivo_colaboradores = 'miLaboratorio/colaboradores_db.json'
    gestion = GestionColaboradores()

    while True:
        limpiar_pantalla()
        mostrar_menu()
        opcion = input('Seleccione una opción: ')

        if opcion == '1' or opcion == '2':
            agregar_colaborador(gestion, opcion)
        elif opcion == '3':
            buscar_colaborador_por_dni(gestion)
        elif opcion == '4':
            actualizar_salario_colaborador(gestion)
        elif opcion == '5':
            eliminar_colaborador(gestion)
        elif opcion == '6':
            #mostrar_todos_los_colaboradores(gestion)
            leer_todos_los_colaboradores(gestion)
        elif opcion == '7':
            print('Saliendo del programa...')
            break
        else:
            print('Opción no válida. Por favor, seleccione una opción válida (1-7)')