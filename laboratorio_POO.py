import json
import mysql.connector
from mysql.connector import Error
from decouple import config

class Colaborador:
    def __init__(self, dni, nombre, apellido, edad, salario):
        self.__dni = self.validar_dni(dni)  #con el doble guión lo encapsulamos, por eso debemos ponerle getter con @property y setter
        self.__nombre = nombre
        self.__apellido = apellido
        self.__edad = edad
        self.__salario = self.validar_salario(salario)

    @property  #esto lo convierte a una propiedad
    def dni(self):
        return self.__dni
    
    @property
    def nombre(self):
        return self.__nombre.capitalize()
    
    @property
    def apellido(self):
        return self.__apellido.capitalize()

    @property
    def edad(self):
        return self.__edad

    @property
    def salario(self):
        return self.__salario

    @salario.setter
    def salario(self, salario):
        self.__salario = self.validar_salario(salario)

    def __str__(self):
        return f"DNI: {self.__dni}, Nombre: {self.__nombre}, Apellido: {self.__apellido}, Edad: {self.__edad}, Salario: {self.__salario}"
        #return f"{self.nombre} {self.apellido}"
    def to_dict(self):
        return {
            "dni": self.dni,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "edad": self.edad,
            "salario": self.salario
        }
   
    def validar_salario(self, salario):
        try:
            
            salario_num = float(salario)
            if salario_num < 0:
                raise ValueError("El salario no puede ser negativo")
            return salario_num
        
        except ValueError:
            raise ValueError("El salario debe ser un número válido")
        

    def validar_dni(self, dni):
        try:
            dni_num = int(dni)
            if len(str(dni_num)) not in [1, 8]:
                raise ValueError("El DNI debe tener entre 7 u 8 dígitos")
            return dni_num
        except ValueError:
            raise ValueError("El DNI debe ser un número válido")
    
class ColaboradorTiempoCompleto(Colaborador):
    def __init__(self, DNI, Nombre, Apellido, Edad, Salario, departamento):
        super().__init__(DNI, Nombre, Apellido, Edad, Salario)
        self.__departamento = departamento

    @property
    def departamento(self):
        return self.__departamento

    def to_dict(self):
        data = super().to_dict()
        data["departamento"] = self.departamento
        return data

    def __str__(self):
        return f"{super().__str__()} - Departamento: {self.departamento}"
    
class ColaboradorTiempoParcial(Colaborador):

    def __init__(self, DNI, Nombre, Apellido, Edad, Salario, horas_semanales):
        super().__init__(DNI, Nombre, Apellido, Edad, Salario)
        self.__horas_semanales = horas_semanales

    @property
    def horas_semanales(self):
        return self.__horas_semanales

    def to_dict(self):
        data = super().to_dict()
        data["horas_semanales"] = self.horas_semanales
        return data

    def __str__(self):
        return f"{super().__str__()} - Horas Semanales: {self.horas_semanales}"
    
class GestionColaboradores:
    def __init__(self):
        self.host = config('DB_HOST')
        self.database = config('DB_NAME')
        self.user = config('DB_USER')  
        self.password = config('DB_PASSWORD')
        self.port = config('DB_PORT')

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if connection.is_connected():
                return connection
            
        except Error as error:
            print(f'Error al conectar a la base de datos: {error}')
            return None
                  
    def leer_datos(self):
        try:
            with open(self.archivo, 'r') as file:
                datos = json.load(file)
        except FileNotFoundError:
            return {}
        except Exception as error:
            raise Exception(f'Error al leer datos del archivo: {error}')
        else:
            return datos

    def guardar_datos(self, datos):
        try:
            with open(self.archivo, 'w') as file:
                json.dump(datos, file, indent=4)

        except IOError as error:
            print(f'Error al intentar guardar los datos en {self.archivo}: {error}')
        except Exception as error:
            print(f'Error al guardar datos en el archivo: {error}')
        
    def crear_colaborador(self, colaborador):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    #Verificar si el DNI ya existe
                    cursor.execute("SELECT * FROM colaboradores WHERE dni = %s", (colaborador.dni,))
                    if cursor.fetchone(): #fetchone devuelve la primera fila de la consulta
                        print(f'Colaborador con DNI {colaborador.dni} ya existe')
                        return
                    #Insertar el colaborador con sus datos comunes
                    query = '''INSERT INTO colaboradores (dni, nombre, apellido, edad, salario) VALUES (%s, %s, %s, %s, %s)'''
                    cursor.execute(query, (colaborador.dni, colaborador.nombre, colaborador.apellido, colaborador.edad, colaborador.salario))
                    #Insertar el colaborador dependiendo del tipo
                    if isinstance(colaborador, ColaboradorTiempoCompleto):
                        query = '''INSERT INTO colaborador_tiempo_completo (dni, departamento) VALUES (%s,%s)'''
                        cursor.execute(query, (colaborador.dni, colaborador.departamento))
                    elif isinstance(colaborador, ColaboradorTiempoParcial):
                        query = '''INSERT INTO colaborador_tiempo_parcial (dni, Horas_semanales) VALUES (%s,%s)'''
                        cursor.execute(query, (colaborador.dni, colaborador.horas_semanales))
                    connection.commit()
                    print(f'Colaborador {colaborador.nombre} {colaborador.apellido} fue agregado correctamente')

        except Exception as error:
            print(f'Error inesperado al crear colaborador: {error}')    

    def leer_colaborador(self, dni):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM colaboradores WHERE dni = %s", (dni,)) #le agrego una coma luego de dni para que python entienda que es una dupla
                    colaborador_data = cursor.fetchone()
                    
                    if colaborador_data:
                        cursor.execute('SELECT departamento FROM colaborador_tiempo_completo WHERE dni = %s', (dni,))
                        departamento = cursor.fetchone()
                    
                        if departamento:
                            colaborador_data['departamento'] = departamento['departamento']
                            colaborador = ColaboradorTiempoCompleto(**colaborador_data)
                    
                        else:
                            cursor.execute('SELECT horas_semanales FROM colaborador_tiempo_parcial WHERE dni = %s', (dni,))
                            horas_semanales = cursor.fetchone()
                    
                            if horas_semanales:
                                colaborador_data['horas_semanales'] = horas_semanales['horas_semanales']
                                colaborador = ColaboradorTiempoParcial(**colaborador_data)
                    
                            else:
                                colaborador = Colaborador(**colaborador_data)
                    
                        #print(f'Colaborador encontrado: {colaborador}')
                    else:
                        #print(f'Colaborador con DNI {dni} no existe')
                        colaborador = None
        except Error as e:
            print(f'Error inesperado al leer colaborador: {e}')
        else:
            return colaborador
        finally:
            if connection.is_connected():
                connection.close()

    def actualizar_colaborador(self, dni, nuevo_salario):

        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    #Verificar si el dni existe
                    if not self.leer_colaborador(dni):
                        print(f'Colaborador con DNI {dni} no existe')
                        return
                    #Actualizar el salario dependiendo del tipo de colaborador
                    cursor.execute("UPDATE colaboradores SET salario = %s WHERE dni = %s", (nuevo_salario, dni))
                    #TODO validar salario
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(f'Salario actualizado para el colaborador con DNI: {dni}')
                    else:
                        print(f'Colaborador con DNI {dni} no existe')
        except Exception as error:
            print(f'Error inesperado al actualizar colaborador: {error}')
        finally:
            if connection.is_connected():
                connection.close()

    def eliminar_colaborador(self, dni):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    #Verificar si el dni existe
                    if not self.leer_colaborador(dni):
                        print(f'Colaborador con DNI {dni} no existe')
                        return
                    if isinstance(self.leer_colaborador(dni), ColaboradorTiempoCompleto):
                        cursor.execute("DELETE FROM colaborador_tiempo_completo WHERE dni = %s", (dni,))
                    if isinstance(self.leer_colaborador(dni), ColaboradorTiempoParcial):
                        cursor.execute("DELETE FROM colaborador_tiempo_parcial WHERE dni = %s", (dni, ))
                    cursor.execute("DELETE FROM colaboradores WHERE dni = %s", (dni, ))
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(f'Colaborador con DNI {dni} eliminado correctamente')
        except Exception as error:
            print(f'Error inesperado al eliminar colaborador: {error}')
        finally:
            if connection.is_connected():
                connection.close()

    def mostrar_colaboradores(self):
        print("---------------------Listado completo de los colaboradores----------------------")
        try:
            datos = self.leer_datos()
            if datos:
                for colaborador_data in datos.values():
                    if 'departamento' in colaborador_data:
                        print(colaborador_data['nombre'] + ' ' + colaborador_data['apellido'] + ' ' + colaborador_data['departamento'])
                    else:
                        print(colaborador_data['nombre'] + ' ' + colaborador_data['apellido'] + ' ' + str(colaborador_data['horas_semanales']))
            else:
                print('No hay colaboradores registrados')
        except Exception as error:
            print(f'Error inesperado al mostrar colaboradores: {error}')
        print("-----------------------------------------------------------------------------")

    def leer_todos_los_colaboradores_mio(self):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM colaboradores")
                    colaboradores = cursor.fetchall()
                    for colaborador in colaboradores:
                        dni = colaborador['DNI']
                        cursor.execute("SELECT departamento FROM colaborador_tiempo_completo WHERE dni = %s", (dni,))
                        departamento = cursor.fetchone()
                        if departamento:
                            colaborador['departamento'] = departamento['departamento']
                            print(colaborador)
                        else:
                            cursor.execute("SELECT horas_semanales FROM colaborador_tiempo_parcial WHERE dni = %s", (dni,))
                            horas_semanales = cursor.fetchone()
                            if horas_semanales:
                                colaborador['horas_semanales'] = horas_semanales['horas_semanales']
                                print(colaborador)
                            else:
                                print(colaborador)
        except Exception as error:
            print(f'Error inesperado al leer todos los colaboradores: {error}')

    def leer_todos_los_colaboradores(self):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM colaboradores")
                    colaboradores_data = cursor.fetchall()
                    
                    colaboradores = []
                    for colaborador_data in colaboradores_data:
                        dni = colaborador_data['DNI']
                        cursor.execute('SELECT departamento from colaborador_tiempo_completo where dni = %s', (dni,))
                        departamento = cursor.fetchone()

                        if departamento:
                            colaborador_data['departamento'] = departamento['departamento']
                            colaborador = ColaboradorTiempoCompleto(**colaborador_data)
                        else:
                            cursor.execute('SELECT horas_semanales from colaborador_tiempo_parcial where dni = %s', (dni,))
                            horas_semanales = cursor.fetchone()

                            if horas_semanales:
                                colaborador_data['horas_semanales'] = horas_semanales['horas_semanales']
                                colaborador = ColaboradorTiempoParcial(**colaborador_data)
                            else:
                                colaborador = Colaborador(**colaborador_data)
                        colaboradores.append(colaborador)
        except Exception as error:
            print(f'Error inesperado al leer todos los colaboradores: {error}')
        else:
            return colaboradores