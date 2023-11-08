from socket import socket, AF_INET, SOCK_STREAM
import os
from datetime import datetime
import json
import pandas as pd
from io import StringIO



def main():
    """
    Función principal que maneja la interacción con el usuario y la comunicación con el servidor.

    Conecta el cliente al servidor, muestra un menú al usuario y procesa su selección. 
    Las opciones incluyen agregar una canción,mostrar la lista de reproducción y salir del programa. 

    La comunicación con el servidor se realiza a través de un socket.
    """
    client_socket = socket(AF_INET, SOCK_STREAM)  # Creación de un objeto socket
    client_socket.connect(('localhost', 12345))  # conexión al servidor en localhost en el puerto 12345
    
    while True:
        os.system('clear')
        print("\nMenu:")
        print("[1]--> Agregar cancion")
        print("[2]--> Mostrar lista de reproduccion")
        print("[3]--> Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            # Se solicita al usuario que introduzca los atributos de la canción
            titulo = input("Titulo de la canción: ")
            interprete = input("Interprete: ")
            album = input("Album: ")
            usuario = input("Usuario que agrego: ")
            duracion = input("Duracion: ")
            
            #se crea un diccionario con los atributos de la canción
            cancion = {"titulo": titulo, "interprete": interprete, "album": album, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                       "usuario":usuario, "duracion": duracion}
            #Se crea una solicitud con la opción y los atributos de la canción
            solicitud = f"1 {json.dumps(cancion)}"
            client_socket.send(solicitud.encode())  #se envía la solicitud al servidor
            respuesta = client_socket.recv(1024).decode() 
            print(respuesta)
        
        elif opcion == "2":
            
            solicitud = "2"  #se crea una solicitud con la opción
            client_socket.send(solicitud.encode())  #se envía la solicitud al servidor
            data_string = client_socket.recv(1024).decode()  #se recibe la respuesta del servidor
            print("Lista de Reproducción:")
            print(data_string)
            df = pd.read_csv(StringIO(data_string))
            print("\n2 ultimas canciones agregadas recientemente:")
            print(df.tail(2).to_string(index=False))
            input("Presiona Enter para continuar...")
            
        elif opcion == "3":
            break  
        
        else:
            print("Opción no válida. Por favor, elija una opción del menú.")
            input("Presiona Enter para continuar...")

if __name__ == "__main__":
    """
    Verifica si el script se está ejecutando como programa principal. Si es así, llama a la función main().
    """
    main()
