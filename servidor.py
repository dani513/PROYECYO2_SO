import os
import pandas as pd
import time
import csv
import threading
from socket import socket, AF_INET, SOCK_STREAM
import pickle
import json

# Clase para representar un reproductor de música con semáforos
class ReproductorMusica:
    def __init__(self):
        self.playlist = pd.DataFrame(columns=["Titulo", "Interprete", "Album", "Fecha", "Usuario", "Duracion"])
        self.nombre_archivo = "playlist.csv"
        self.bloqueo = "bloqueo.txt"
        self.semaforo = threading.Semaphore()
        
    def cargar_playlist(self):
        try:
            self.playlist = pd.read_csv(self.nombre_archivo)
        except FileNotFoundError:
            print("El archivo no existe")

    def guardar_playlist(self):
        self.playlist.to_csv(self.nombre_archivo, index=False)
        
        print("Agregada exitosamente a la playlist")

    def verificar_bloqueo(self):
        return os.path.isfile(self.bloqueo)

    def crear_bloqueo(self):
        with open(self.bloqueo, mode='w', newline='') as archivo_bloqueo:
            escritor = csv.writer(archivo_bloqueo)
            escritor.writerow(["En proceso"])

    def eliminar_bloqueo(self):
        os.remove(self.bloqueo)

    def agregar_cancion(self, titulo, interprete, album, fecha, usuario, duracion):
        self.semaforo.acquire()
        self.cargar_playlist()

        if not self.playlist[(self.playlist['Titulo'] == titulo) & (self.playlist['Interprete'] == interprete)].empty:
            print(f"La canción '{titulo}' de '{interprete}' ya está en la playlist.")
            time.sleep(3)
            self.eliminar_bloqueo()
            return
        
        #self.crear_bloqueo()        
        nueva_cancion = pd.DataFrame([[titulo, interprete, album, fecha, usuario, duracion]],
                                      columns=["Titulo", "Interprete", "Album", "Fecha", "Usuario", "Duracion"])
        self.playlist = pd.concat([self.playlist, nueva_cancion], ignore_index=True)
        print("si llega")
        time.sleep(5)
        self.guardar_playlist()
        self.semaforo.release()

        time.sleep(2)
        #self.eliminar_bloqueo()

    def mostrar_playlist(self):
        self.cargar_playlist()
        ultimas_canciones = self.playlist.tail(2)
        print("\nLista de Reproducción:") 
        print(self.playlist.to_string(index=False))
        print("\nÚltimas dos canciones agregadas:")
        print(ultimas_canciones.to_string(index=False))
        time.sleep(10)

    def ver_playlist(self):
        self.cargar_playlist()
        return self.playlist()
        
# Clase para representar el servidor
class ServidorReproductor:
    def __init__(self, reproductor):
        self.reproductor = reproductor

    def ejecutar_servidor(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('localhost', 12345))
        server_socket.listen(5)
        
        while True:
            print("Esperando conexiones...")
            (client_socket, client_address) = server_socket.accept()
            print(f"Conexión establecida con {client_address}")
            client_thread = threading.Thread(target=self.atender_cliente, args=(client_socket,))
            client_thread.start()

    def atender_cliente(self, client_socket):
        while True:
            
            solicitud = client_socket.recv(1024).decode()
            if not solicitud: 
                break
            
            if solicitud == "2":
                playlist = pd.read_csv("playlist.csv")
                resp = playlist.to_string(index=False)
                #playlist_data = self.reproductor.playlist.to_dict(orient='records')
                #data_string = pickle.dumps(playlist_data)
                
                x = playlist.tail(2)
                client_socket.send(resp.encode())
                
            elif solicitud == "3":
                break
                      
            elif solicitud.startswith('1'):
                print("past")
                cancion = json.loads(solicitud.split(" ",1)[1])
                self.reproductor.agregar_cancion(**cancion)
                client_socket.send("Canción agregada exitosamente".encode())
        client_socket.close()
                
# Función para ejecutar el servidor
def ejecutar_servidor():
    reproductor = ReproductorMusica()
    servidor = ServidorReproductor(reproductor)
    servidor.ejecutar_servidor()

if __name__ == "__main__":
    # Inicia el servidor en un hilo separado
    servidor_thread = threading.Thread(target=ejecutar_servidor)
    servidor_thread.start()
