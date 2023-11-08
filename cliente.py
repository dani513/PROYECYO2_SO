from socket import socket, AF_INET, SOCK_STREAM
import pickle
import os
from datetime import datetime
import json
import pandas as pd
from io import StringIO



def main():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    
    while True:
        os.system('clear')
        print("\nMenu:")
        print("[1]--> Agregar canción")
        print("[2]--> Mostrar lista de reproducción")
        print("[3]--> Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            titulo = input("Título de la canción: ")
            interprete = input("Intérprete: ")
            album = input("Álbum: ")
            #fecha = input("Fecha de agregación: ")
            usuario = input("Usuario que agregó: ")
            duracion = input("Duración: ")
            
            cancion = {"titulo": titulo, "interprete": interprete, "album": album, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                       "usuario":usuario, "duracion": duracion}
            
            solicitud = f"1 {json.dumps(cancion)}"
            client_socket.send(solicitud.encode())
            respuesta = client_socket.recv(1024).decode()
            print(respuesta)
        
        elif opcion == "2":
            
            solicitud = "2"
            client_socket.send(solicitud.encode())
            data_string = client_socket.recv(1024).decode()
            print("Lista de Reproducción:")
            print(type(data_string))
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
    main()
