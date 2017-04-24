#!/usr/bin/env python
# coding: utf-8

import socket, select, string, sys
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

if(len(sys.argv) != 4) :
        print("Erreur : mauvais nombre d'arguments.\npython client.py host port username")
        sys.exit()

host = sys.argv[1]
try:
        port = int(sys.argv[2])
except:
        print("Erreur: port incorrect")
        sys.exit()
        
name = sys.argv[3]

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
