#!/usr/bin/env python
# coding: utf-8
# Ce bot est une copie de client.py, légèrement modifié pour tester de façon automatique l'envoi des messages passés en argument.
# Ce qu'on attend du test :
# - envoi du premier message passé en argument
# - envoi du second message passé en argument
# - envoi du message de déconnexion \quit
#
# Le bon envoi des messages est testé dans le bot de réception des messages.

import socket, select, string, sys , time
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
message_1 = sys.argv[4]
message_2 = sys.argv[5]
message_1 += "\n"
message_2 += "\n"
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
time.sleep(2)
server.send(message_1)
time.sleep(2)
server.send(message_2)
time.sleep(2)
server.send("\quit")
######################################


while True:
        socketlist = [sys.stdin, server]  #entrée standard, serveur // socketlist du client
        rsocket, wsocket, escoket = select.select(socketlist , [], [])
        
        for socket in rsocket:
                if socket == server:
                        message = socket.recv(4096)
                        if message :
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
