#!/usr/bin/env python
# coding: utf-8
# Ce bot est une copie de client.py, légèrement modifié pour tester de façon automatique la réception des messages passés en argument.
# On connait en avance qui va envoyer quel message afin de tester le contenu (l'username étant passé dans le message)
# Ce qu'on attend du test :
# - premier message reçu : message de connexion de la part du serveur (ignoré, voir plus bas)
# - deuxieme message reçu : message de connexion du bot1 (ignoré car affiche l'heure de connexion,
#                           problème si la connexion se fait à la fin d'une minute... (minute de décalage)
# - troisième message reçu : premier message du bot1 : "bot1 >> coucou" (testé)
# - quatrième message reçu : deuxieme message du bot1 : "bot1 >> salut" (testé)
# - cinquième message reçu : message de déconnexion du bot1 : "<SERVEUR> bot1 s'est déconnecté" (testé)
#
# On écrit dans un fichier .txt si le test est réussi ou raté, puis on récupère ce fichier .txt dans le programme de test principal.

import socket, select, string, sys, time
import os, signal

running_version = sys.version_info[0]
python3 = (running_version == 3)
if python3:
        print("Veuillez lancer le programme avec la commande python (pas python3)")
        sys.exit()

def handler(signal, frame):
        print('\rDeconnexion du chat')
        server.send("\quit")
        sys.exit()
        
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGHUP, handler)

if(len(sys.argv) != 6) :
        print("Erreur : mauvais nombre d'arguments.\npython client.py host port username message1 message2")
        sys.exit()

host = sys.argv[1]
try:
        port = int(sys.argv[2])
except:
        print("Erreur: port incorrect")
        sys.exit()
        
name = sys.argv[3]

#### PARTIE RAJOUTEE POUR LE TEST ####
message_1 = "\rbot1 >> "
message_1 += sys.argv[4]
message_1 += "\n"
message_2 = "\rbot1 >> "
message_2 += sys.argv[5]
message_2 += "\n"
message_3 = "\r<SERVEUR> bot1 s'est déconnecté\n" #on test qu'on reçoit également les messages générés par le serveur...
message_test = ""
compteur = 0
f = open("fichiertest.txt","w")
######################################

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
os.system("clear")

try :
        server.connect((host, port))
except :
        print("Connexion au serveur {} via la port {} impossible".format(host, port))
        sys.exit()

print("Connecté au serveur {} via le port {}".format(host, port))
server.send(name) #envoie du nom d'utilisateur au serveur

#### PARTIE RAJOUTEE POUR LE TEST ####
#On récupère ici le message de connexion de la part du serveur...
message_de_connexion = server.recv(4096)
#...ainsi que le message de connexion du bot1
message_de_connexion = server.recv(4096)
######################################

while True:
        socketlist = [sys.stdin, server]  #entrée standard, serveur // socketlist du client
        rsocket, wsocket, escoket = select.select(socketlist , [], [])
        
        for socket in rsocket:
                if socket == server:
                        message = socket.recv(4096)
                        if message :
                                
                                # CETTE PARTIE A ETE RAJOUTEE EXCLUSIVEMENT POUR LE TEST #######################
                                if message == message_1 or message == message_2 or message == message_3:
                                        compteur += 1
                                        message_test += "Test envoi/réception du message {} : ok\n".format(compteur)
                                        if compteur >= 3 :
                                                server.send("\quit")
                                                f.write(message_test)
                                                f.close()
                                else :
                                        compteur += 1
                                        message_test += "Test envoi/réception du message {} : fail\n".format(compteur)
                                        if compteur >= 3 :
                                                server.send("\quit")
                                                f.write(message_test)
                                                f.close()
                                ################################################################################
                                                
                                sys.stdout.write(message)      #On écrit le message du serveur sur l'entrée standard (terminal)
                                sys.stdout.write(name +" >> ") #affiche le nom sur le terminal
                                sys.stdout.flush()             #ne compte pas le nom affiché
                        else :
                                print('\rVous avez été deconnecté')
                                sys.exit()
                else :
                        message = sys.stdin.readline()
                        if(not message):
                                print('\rDeconnexion du chat')
                                server.send("\quit")
                                sys.exit()
                        if(message.replace(" ", "") != "\n"):
                                server.send(message)
                        sys.stdout.write(name +" >> ") #affiche le nom sur le terminal
                        sys.stdout.flush()             #ne compte pas le nom affiché

server.close()
