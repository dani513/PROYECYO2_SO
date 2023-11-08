from socket import socket, AF_INET, SOCK_STREAM
import os
from datetime import datetime
import json
import pandas as pd
from io import StringIO



def main():
    """
    Función principal que maneja la interaccion con el usuario y la comunicacion con el servidor.

    Conecta el cliente al servidor, muestra un menu al usuario y procesa su seleccion. 
    Las opciones incluyen agregar una cancion,mostrar la lista de reproduccion y salir del programa. 

    La comunicacion con el servidor se realiza a traves de un socket.
    """
    client_socket = socket(AF_INET, SOCK_STREAM)  # Creacion de un objeto socket
    client_socket.connect(('localhost', 12345))  # conexion al servidor en localhost en el puerto 12345
    
    while True:
        os.system('clear')
        print("\nMenu:")
        print("[1]--> Agregar cancion")
        print("[2]--> Mostrar lista de reproduccion")
        print("[3]--> Salir")
        
        opcion = input("Seleccione una opcion: ")
        
        if opcion == "1":
            # Se solicita al usuario que introduzca los atributos de la cancion
            titulo = input("Titulo de la cancion: ")
            interprete = input("Interprete: ")
            album = input("Album: ")
            usuario = input("Usuario que agrego: ")
            duracion = input("Duracion: ")
            
            #se crea un diccionario con los atributos de la cancion
            cancion = {"titulo": titulo, "interprete": interprete, "album": album, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                       "usuario":usuario, "duracion": duracion}
            #Se crea una solicitud con la opción y los atributos de la cancion
            solicitud = f"1 {json.dumps(cancion)}"
            client_socket.send(solicitud.encode())  #se envia la solicitud al servidor
            respuesta = client_socket.recv(1024).decode() 
            print(respuesta)
        
        elif opcion == "2":
            
            solicitud = "2"  #se crea una solicitud con la opcion
            client_socket.send(solicitud.encode())  #se envía la solicitud al servidor
            data_string = client_socket.recv(1024).decode()  #se recibe la respuesta del servidor
            print("Lista de Reproduccion:")
            print(data_string)
            df = pd.read_csv(StringIO(data_string))
            print("\n2 ultimas canciones agregadas recientemente:")
            print(df.tail(2).to_string(index=False))
            input("Presiona Enter para continuar...")
            
        elif opcion == "3":
            break  
        
        else:
            print("Opcion no valida. Por favor, elija una opcion del menu.")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
