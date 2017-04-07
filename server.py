#!/usr/bin/env python
# coding: utf-8

import socket, select, sys, signal, os

ip = sys.argv[1]
port = int(sys.argv[2])
socketlist = []
client = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
server.listen(10)

socketlist.append(server) #on rajoute le serveur à la liste des sockets

def handler(signal, none):
        print("\r\n!! FERMETURE DU SERVEUR !! \n")
        for socket in socketlist:
                socket.close()
        server.close()
        sys.exit()

signal.signal(signal.SIGINT, handler)

#Fonction pour envoyer les messages aux utilisateurs
def send_to_all_users (initial_socket, username, message):
        for socket in socketlist:   #Pour tous les sockets...
                if socket != server and socket != initial_socket :  #... qui ne sont pas le serveur ni le client ayant envoyé le message...
                        try:
                                socket.send(username + message)   #on envoie le message
                        except:
                                socket.close()
                                user = socket.getpeername()
                                del client[user]
                                socketlist.remove(socket)


def send_all_connected_users(socket):
        message = "\r  |==================================|\n  | Clients connectés sur le serveur |\n  |==================================|\n"
        for clients in client:
                message += "\r  | -- "+client[clients]+"\n"
        message += "\r  |==================================|\n\n"
        socket.send(message)

def send_server_information(socket):
        S = ""
        if(len(client) > 1) :
                S = "S"
        message = "\r  |============================|\n  | Information sur le serveur |\n  |============================|\n"
        message += "  | -- IP : "+str(ip)+"\n"
        message += "  | -- PORT : "+str(port)+"\n"
        message += "  | -- "+str(len(client))+" CLIENT"+S+"\n"
        message += "  |============================|\n\n"
        socket.send(message)

def send_command_info(socket):
        message = "\r  |===============================|\n  |     Commandes disponibles     |\n  |===============================|\n"
        message += "  | -- \quit : deconnexion\n"
        message += "  | -- \info : informations sur\n"
        message += "  |            le serveur\n"
        message += "  | -- \list : liste des clients\n"
        message += "  | -- \command : informations sur\n"
        message += "  |               les commandes\n"
        message += "  |===============================|\n\n"
        socket.send(message)

def search_user_socket(username, socklist):
        user = [s for s, c in client.items() if c == username]
        if(user):
                user = user[0]
                for socket in socklist:
                        if socket != server:
                                u = socket.getpeername()
                                if u == user:
                                        return socket
        return False

def search_user_name(msg):
        username = ""
        for c in msg:
                if c == " ":
                        break;
                if c != "@":
                        username += c
        return username

def private_message_handler(username, msg):
        return msg[len(username)+2::]

def command_handler(command, socket, user):
        if(command == "\quit"):
                socket.send("\rFermeture du chat \n")
                send_to_all_users(socket, "\r<SERVEUR> {}".format(str(client[user])), " s'est déconnecté\n")
                socket.close()
                del client[user]
                socketlist.remove(socket)

                return False
        if(command == "\list"):
                send_all_connected_users(socket)
                return False
        if(command == "\info"):
                send_server_information(socket)
                return False
        if(command == "\command"):
                send_command_info(socket)
                return False
        return True

print("|=================|\n| Chat IRC débuté |\n|=================|\n -- IP: {}\n -- PORT: {}\n|=================|\n -- VICTOR JUNG\n|=================|".format(ip, port))

while True:
        rsockets, wsockets, esockets = select.select(socketlist, [], [])

        for socket in rsockets:
                if socket == server:   #Connexion d'un client au serveur
                        newsocket, ipport = server.accept()
                        socketlist.append(newsocket)  #on rajouter le socket du client à la liste des sockets disponibles
                        name = newsocket.recv(4096)   #on récupère le nom envoyé par le client directement après sa connexion (identifiant)
                        if([s for s, c in client.items() if c == name]):
                                newsocket.send("\r<SERVEUR> L'username est déjà utilisé !")
                                socketlist.remove(newsocket)
                                newsocket.close()
                        else:
                                client[ipport] = name         #on rajoute au dictionnaire le couple (ip,port):name pour identifier les utilisateurs                        print("{} vient de se connecter {}".format(name, ipport))     #message pour le serveur (avec (ip,port) du client)
                                send_to_all_users(newsocket, "\r<SERVEUR> ","{} vient de se connecter\n".format(name))  #message pour les utilisateurs (avec seulement le nom)
                                send_command_info(newsocket)
                                send_all_connected_users(newsocket)
                else:
                        try:
                                data = socket.recv(4096)
                                user = socket.getpeername()
                                if data:
                                    command = data.replace(" ", "").replace("\n", "")
                                    if(command_handler(command, socket, user)):
                                        if data[0] == "@":
                                                private_u = search_user_name(data)
                                                private = search_user_socket(private_u, socketlist)
                                                if(private):
                                                        data = private_message_handler(private_u, data)
                                                        private.send("\rfrom " + str(client[user]) + ': ' + data)
                                                else:
                                                        socket.send("\r<SERVEUR> Client introuvable !\n")
                                        else:
                                                send_to_all_users(socket, "\r" + str(client[user]) + ' >> ', data)                
                        
                        except:
                                send_to_all_users(server, "\r<SERVEUR> {}".format(str(client[user])), " s'est déconnecté\n")
                                print("{} s'est déconnecté {}".format(client[user], user))
                                del client[user]
                                socket.close()
                                socketlist.remove(socket)
                                continue

server.close()
