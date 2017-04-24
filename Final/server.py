#!/usr/bin/env python
# coding: utf-8

import socket, select, sys, signal, os, time, re
from multiprocessing import Queue

running_version = sys.version_info[0]
python3 = (running_version == 3)
if python3:
        print("Veuillez lancer le programme avec la commande python (pas python3)")
        sys.exit()

if(len(sys.argv) != 3) :
        print("Erreur : mauvais nombre d'arguments.\npython server.py port port_web")
        sys.exit()
        
try:
        port = int(sys.argv[1])
        port_web = int(sys.argv[2])
except:
        print("Erreur: port incorrect")
        sys.exit()

socketlist = []

client = {}
saved_messages = Queue()
ip = "localhost"          #DEFAUT : "localhost"
max_saved_messages = 5    #DEFAUT : 5
TIMEOUT_TIME = 3.0        #DEFAUT : 3.0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #evite l'erreur "Adress already in use" lorsqu'on relance le serveur sur le même (ip,port)

server_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_web.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
        server.bind((ip, port))
        server_web.bind((ip, port_web))
except:
        print("Erreur: port incorrect")
        sys.exit()
        
server.listen(10)      #DEFAUT : 10
server_web.listen(10)  #DEFAUT : 10

SHUT_RDWR = socket.SHUT_RDWR

socketlist.append(server)     #on rajoute le serveur à la liste des sockets
socketlist.append(server_web) #on rajoute également le serveur web

#Message de lancement du serveur
print("|=================|\n| Chat IRC débuté |\n|=================|\n -- IP: {}\n -- PORT: {}\n -- WEB: {}\n|=================|\n -- VICTOR JUNG\n -- STEVE MALALEL\n|=================|".format(ip, port, port_web))


#Handler pour la fermeture du serveur (CTRL+C)
def handler(signal, none):
        print("\r!! FERMETURE DU SERVEUR !!")
        for socket in socketlist:   #on ferme chaque socket disponible
                if socket != server and socket != server_web:
                        user = socket.getpeername()
                        print("{} a été déconnecté {}".format(client[user], user))
                socket.shutdown(SHUT_RDWR)
                socket.close()
        sys.exit()                  #on exit le programme

#Installation du handler sur SIGINT (CTRL+C)
signal.signal(signal.SIGINT, handler)

#Fonction pour envoyer les messages aux utilisateurs
def send_to_all_users (initial_socket, username, message):
        for socket in socketlist:   #Pour tous les sockets...
                if socket != server and socket != server_web and socket != initial_socket :  #... qui ne sont pas le serveur ni le client ayant envoyé le message...
                        try:
                                socket.send(username + message)   #on envoie le message
                        except:  #erreur si le socket n'existe plus mais est toujours ouvert... donc on le ferme et on le remove de la liste
                                socket.close()
                                user = socket.getpeername()
                                del client[user]
                                socketlist.remove(socket)

#Envoie de la liste de tous les clients connectés au serveur (dans le dictionnaire client) (automatique à chaque connexion, \list)
def all_connected_users():
        message = "\r  |==================================|\n  | Clients connectés sur le serveur |\n  |==================================|\n"
        for clients in client:
                message += "\r  | -- "+client[clients]+"\n"
        message += "\r  |==================================|\n\n"
        return message

#Envoie des informations à propos du serveur (ip, port, nombre de client) \info
def server_information():
        S = ""
        if(len(client) > 1) :
                S = "S"
        message = "\r  |============================|\n  | Information sur le serveur |\n  |============================|\n"
        message += "  | -- IP : "+str(ip)+"\n"
        message += "  | -- PORT : "+str(port)+"\n"
        message += "  | -- WEB : "+str(port_web)+"\n"
        message += "  | -- "+str(len(client))+" CLIENT"+S+"\n"
        message += "  |============================|\n\n"
        return message

#Envoie des informations à propos des commandes disponibles sur le chat (automatique à chaque connexion, \command)
def command_info():
        message = "\r  |===============================|\n  |     Commandes disponibles     |\n  |===============================|\n"
        message += "  | -- \quit : deconnexion\n"
        message += "  | -- \info : informations sur\n"
        message += "  |            le serveur\n"
        message += "  | -- \list : liste des clients\n"
        message += "  | -- \command : informations sur\n"
        message += "  |               les commandes\n"
        message += "  | @Username : envoie un message\n"
        message += "  |             privé à Username\n"
        message += "  |===============================|\n\n"
        return message

def send_new_connection(socket, name):
        message = command_info()
        message += all_connected_users()
        if(saved_messages.qsize() > 0):
                message += last_messages()
        message += "\r<SERVEUR> ({}) {} vient de se connecter\n".format(time.strftime("%H:%M"), name)
        socket.send(message)

#Cherche le socket d'un utilisateur à partir de son username (pas de duplicate dans les usernames)
#Retourne socket s'il existe un socket correspondant, False sinon
def search_user_socket(username, socklist):
        user = [s for s, c in client.items() if c == username]
        if(user):
                user = user[0]
                for socket in socklist:
                        if socket != server and socket != server_web:
                                u = socket.getpeername()
                                if u == user:
                                        return socket
        return False

#Cherche le nom d'un utilisateur à partir d'un message privé (forme : @Username message) => retourne "Username"
def search_user_name(message):
        username = ""
        for c in message:
                if c == " ":
                        break;
                if c != "@":
                        username += c
        return username

#Enleve le nom d'utilisateur d'un message privé (forme : @Username message) => retourne "message"
def private_message_transform(username, msg):
        return msg[len(username)+2::]

#Gère l'envoie des messages privés (forme: @Username message)
#envoie à Username "from xxxx: message" si Username trouvé et retourne True
#message d'erreur et retourne False sinon.
def private_message_handler(message, socket, user):
        #Si le message est un message privé (il commence par "@")
        if message[0] == "@":
                private_u = search_user_name(message)               #On recupere le nom du destinataire
                private = search_user_socket(private_u, socketlist) #On cherche le socket correspondant au destinataire
                if(private):                                        #Si on a trouvé un socket correspondant
                        message = private_message_transform(private_u, message)       #On modifie la forme du message ("@Username message" => "message")
                        private.send("\rfrom " + str(client[user]) + ': ' + message)  #On envoie à Username le message sous la forme "from xxxx: message"
                        return True
                else:   #Impossible de trouver un socket correspondant
                        socket.send("\r<SERVEUR> Client introuvable ! (\list pour la liste des clients)\n")
                        return True
        return False

#Gestion des commandes : retourne False si le message est une commande (et l'execute), True sinon.
def command_handler(command, socket, user):
        if(command == "\quit"):
                send_to_all_users(socket, "\r<SERVEUR> {}".format(str(client[user])), " s'est déconnecté\n")
                socket.send("\rDéconnexion")
                print("{} : {} s'est déconnecté {}".format(time.strftime("%H:%M:%S"),client[user], user))
                socket.close()
                del client[user]
                socketlist.remove(socket)
                return False

        if(command == "\list"):
                socket.send(all_connected_users())
                return False
        
        if(command == "\info"):
                socket.send(server_information())
                return False
        
        if(command == "\command"):
                socket.send(command_info())
                return False
        
        return True

def add_to_saved_messages(user, message):
        if(saved_messages.qsize() >= max_saved_messages):
                saved_messages.get()
        saved_messages.put("("+time.strftime("%H:%M")+") " + user + ">> " + message)

def last_messages_list(last_messages):
        liste = [last_messages.get() for i in range(last_messages.qsize())]
        for i in liste:
                last_messages.put(i)
        return liste

def last_messages():
        last_messages = last_messages_list(saved_messages)
        message = "\r"
        for msg in last_messages:
                message += msg
        return message

def page_html():
        code = "<head><meta charset='utf-8'><title>CHAT IRC</title></head><body>"
        code +="<h1>Les {} derniers message envoyés</h1>".format(max_saved_messages)
        code +="<ul>"
        liste = last_messages_list(saved_messages)
        for m in liste :
                m = m.replace("\r","")
                code += "<li>"+m+"</li>"
        code +="</ul></body></html>"
        return code

#Serveur
while True:
        #On récupère les sockets prêts via select.select
        rsockets, wsockets, esockets = select.select(socketlist, [], [])

        #Pour les sockets qui sont prêts (=> qui envoient qqch)
        for socket in rsockets:
                #Connexion d'un client au serveur
                if socket == server:
                        newsocket, ipport = server.accept() #On accepte le nouveau client et on récupère son socket et son (ip, port)
                        socketlist.append(newsocket)        #On rajoute le socket du client à la liste des sockets disponibles
                        name = newsocket.recv(4096)         #On récupère le nom envoyé par le client directement après sa connexion (identifiant)
                        #On vérifie que le nom envoyé par le client n'est pas déjà utlisé
                        if([s for s, c in client.items() if c == name]):
                                #S'il est déjà utilisé, on enlève le socket de la liste et on le ferme.
                                newsocket.send("\r<SERVEUR> L'username est déjà utilisé !")
                                socketlist.remove(newsocket)
                                newsocket.close()
                        else:
                                #Sinon, on rajoute le client à la liste des clients, on envoie l'information de la connexion aux autres utilisateurs
                                client[ipport] = name         #on rajoute au dictionnaire le couple (ip,port):name pour identifier les utilisateurs                        print("{} vient de se connecter {}".format(name, ipport))     #message pour le serveur (avec (ip,port) du client)
                                send_new_connection(newsocket, name)
                                send_to_all_users(newsocket, "\r<SERVEUR> ({}) ".format(time.strftime("%H:%M")),"{} vient de se connecter\n".format(name))  #message pour les utilisateurs (avec seulement le nom)
                                print("{} : {} s'est connecté {}".format(time.strftime("%H:%M:%S"), name, ipport))

                elif socket == server_web:
                        web, ipport = server_web.accept()
                        print("WEB : {} : {} s'est connecté".format(time.strftime("%H:%M:%S"), ipport))
                        web.settimeout(TIMEOUT_TIME)  #on met un timeout sur le socket (3.0 secondes par défaut)
                        
                        #Dans le cas du timeout, s'il arrive à terme, produit une exception.
                        #On lance donc le tout dans un try/except (except étant le timeout)
                        try:
                                request = web.recv(4096)
                                request = re.match("GET / HTTP/", request)
                                if request:
                                        web.send('HTTP/1.0 200 OK\n')            #on répond à la requete
                                        web.send('Content-Type: text/html\n\n')  #on annonce le type de contenu
                                        web.send(page_html())                    #et là tu met le sauce
                                        print("WEB : Contenu envoyé à {}".format(ipport))
                                else:
                                        web.send('\rRequête non valide.\n')
                                        print("WEB : Requête invalide de {}".format(ipport))
                                print("WEB : {} - Déconnexion de {}".format(time.strftime("%H:%M:%S"), ipport))
                                
                        #Aucune requête, timeout du socket
                        except:
                                print("WEB : TIMEOUT de {}, aucune requête reçue".format(ipport))
                                pass
                        web.close()                                      #et on ferme
                        
                #Si ce n'est pas une connexion, alors c'est un message reçu
                else:
                        try:
                                message = socket.recv(4096)  #On récupère le message
                                user = socket.getpeername()  #On récupère l'utilisateur qui a envoyé ce message
                                #S'il existe un message
                                if message :
                                        command = message.replace(" ", "").replace("\n", "")
                                        if(command_handler(command, socket, user)):            #on teste s'il s'agit d'une commande (si oui => False)
                                                if (not private_message_handler(message, socket, user)):  #on teste s'il s'agit d'un message privé (si oui => True)
                                                        send_to_all_users(socket, "\r{} >> ".format((client[user])), message)  #on envoie le message à tous les clients (sauf serveur et client qui envoie le message)
                                                        add_to_saved_messages(client[user], message)

                        #En cas d'erreur, on déconnecte le client ayant engendré l'erreur, et on continue le programme (pas de plantage du serveur)
                        except:
                                send_to_all_users(server, "\r<SERVEUR> ({}) {}".format(time.strftime("%H:%M"), client[user]), " s'est déconnecté\n")
                                print("{} : {} s'est déconnecté {}".format(time.strftime("%H:%M:%S"),client[user], user))
                                del client[user]
                                socket.close()
                                socketlist.remove(socket)
                                continue

server.close()
