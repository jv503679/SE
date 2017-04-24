#!/usr/bin/env python
# coding: utf-8

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
message_1 = "bot1 >> "
message_1 += sys.argv[4]
message_1 += ""
message_2 = "bot1 >> "
message_2 += sys.argv[5]
message_2 += "\n"
message_test = ""
compteur = 0
f = open("fichiertest.txt","w")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
os.system("clear")

try :
        server.connect((host, port))
except :
        print("Connexion au serveur {} via la port {} impossible".format(host, port))
        sys.exit()

print("Connecté au serveur {} via le port {}".format(host, port))
server.send(name) #envoie du nom d'utilisateur au serveur

while True:
        socketlist = [sys.stdin, server]  #entrée standard, serveur // socketlist du client
        rsocket, wsocket, escoket = select.select(socketlist , [], [])
        
        for socket in rsocket:
                if socket == server:
                        message = socket.recv(4096)
                        if message :
                                if message == message_1 or message == message_2 :
                                        compteur += 1
                                        message_test += "Test envoi/réception du message {} : ok\n".format(compteur)
                                        if compteur >= 2 :
                                                server.send("\quit")
                                                f.write(message_test)
                                                f.close()
                                else :
                                        compteur += 1
                                        message_test += "Test envoi/réception du message {} : fail\n".format(compteur)
                                        if compteur >= 2 :
                                                server.send("\quit")
                                                f.write(message_test)
                                                f.close()
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
