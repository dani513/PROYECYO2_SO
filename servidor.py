import pandas as pd
import time
import csv
import threading
from socket import socket, AF_INET, SOCK_STREAM
import json

#clase para representar un reproductor de musica con semáforos
class ReproductorMusica:
    """
    Clase para representar un reproductor de música con semáforos.

    Esta clase administra una lista de reproducción de canciones y proporciona métodos para agregar canciones, guardar y modificar la lista de reproducción.
    También, tiene un semáforo para garantizar la exclusión mutua al agregar anciones.
    """
    def __init__(self):
        """
        Inicializa el reproductor de música.
        Crea un DataFrame vacío para la lista de reproducción y establece el nombre del archivo para guardar y cargar la lista de reproducción.
        """
        self.playlist = pd.DataFrame(columns=["Titulo", "Interprete", "Album", "Fecha", "Usuario", "Duracion"])
        self.nombre_archivo = "playlist.csv"
        self.semaforo = threading.Semaphore()
        
    def cargar_playlist(self):
        """Carga la lista de reproducción desde un archivo CSV."""
        try:
            self.playlist = pd.read_csv(self.nombre_archivo)
        except FileNotFoundError:
            print("El archivo no existe")

    def guardar_playlist(self):
        """Guarda la lista de reproducción en un archivo CSV."""
        self.playlist.to_csv(self.nombre_archivo, index=False)
        
        print("Agregada exitosamente a la playlist")


    def agregar_cancion(self, titulo, interprete, album, fecha, usuario, duracion):
        """
        Agrega una canción a la lista de reproducción, asegurándose que no exista una 
        canción con el mismo título e interprete.
        """
        self.semaforo.acquire()
        self.cargar_playlist()

        if not self.playlist[(self.playlist['Titulo'] == titulo) & (self.playlist['Interprete'] == interprete)].empty:
            print(f"La canción '{titulo}' de '{interprete}' ya está en la playlist.")
            time.sleep(3)

            self.semaforo.release()
            return
             
        nueva_cancion = pd.DataFrame([[titulo, interprete, album, fecha, usuario, duracion]],
                                      columns=["Titulo", "Interprete", "Album", "Fecha", "Usuario", "Duracion"])
        self.playlist = pd.concat([self.playlist, nueva_cancion], ignore_index=True)
        time.sleep(5)
        self.guardar_playlist()
        self.semaforo.release()

        time.sleep(2)

    def mostrar_playlist(self):
        """Muestra la lista de reproducción."""
        self.cargar_playlist()
        ultimas_canciones = self.playlist.tail(2)
        print("\nLista de Reproducción:") 
        print(self.playlist.to_string(index=False))
        print("\nÚltimas dos canciones agregadas:")
        print(ultimas_canciones.to_string(index=False))
        time.sleep(10)

    def ver_playlist(self):
        """Retorna la lista de reproducción."""
        self.cargar_playlist()
        return self.playlist()
        
#clase para representar el servidor
class ServidorReproductor:
    """
    Clase para representar el servidor del reproductor de música.

    Esta clase gestiona la comunicación entre el cliente y el reproductor de música.
    """
    def __init__(self, reproductor):
        """
        Inicializa el servidor del reproductor de música.

        Establece el reproductor de música que se utilizará.
        """
        self.reproductor = reproductor

    def ejecutar_servidor(self):
        """
        Ejecuta el servidor del reproductor de música.

        Crea un socket de servidor y espera conexiones de clientes.
        Cuando se establece una conexión, crea un nuevo hilo para atender al cliente.
        """
        server_socket = socket(AF_INET, SOCK_STREAM)  #creación de un objeto socket
        server_socket.bind(('localhost', 12345))  #vincula el socket del servidor a la dirección localhost y al puerto 12345
        server_socket.listen(5)  #permite al servidor escuchar conexiones entrantes
        
        while True:
            print("Esperando conexiones...")
            (client_socket, client_address) = server_socket.accept()
            print(f"Conexión establecida con {client_address}")
            client_thread = threading.Thread(target=self.atender_cliente, args=(client_socket,))
            client_thread.start()

    def atender_cliente(self, client_socket):
        """
        Maneja la solicitud de un cliente.

        Recibe solicitudes del cliente y las procesa.
        Las solicitudes pueden ser para agregar una canción a la lista de reproducción o para obtener la lista de reproducción.
        """
        while True:
            
            solicitud = client_socket.recv(1024).decode()
            if not solicitud: 
                break
            
            if solicitud == "2":  #solicitud de mostrar la lista
                playlist = pd.read_csv("playlist.csv")
                resp = playlist.to_string(index=False)
                
                client_socket.send(resp.encode())
                
            elif solicitud == "3":  #solicitud de salir
                break
                      
            elif solicitud.startswith('1'):  #solicitud para agregar una canción
                cancion = json.loads(solicitud.split(" ",1)[1])
                self.reproductor.agregar_cancion(**cancion)
                client_socket.send("Canción agregada exitosamente".encode())
        client_socket.close()  #cierra la conexión con el cliente
                
#funcion para ejecutar el servidor
def ejecutar_servidor():
    """
    Función para ejecutar el servidor.

    Crea un reproductor de música y un servidor de reproductor, y luego ejecuta el servidor.
    """
    reproductor = ReproductorMusica()
    servidor = ServidorReproductor(reproductor)
    servidor.ejecutar_servidor()

if __name__ == "__main__":
    """
    Verifica si el script se está ejecutando como programa principal. Si es así, inicia el servidor en un hilo separado.
    """
    servidor_thread = threading.Thread(target=ejecutar_servidor)
    servidor_thread.start()
