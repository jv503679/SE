#!/usr/bin/env python
# coding: utf-8

import socket, select, string, sys
import os, signal

def handler(signal, frame):
        print('\rDeconnexion du chat')
        server.send("\quit")
        sys.exit()
        
signal.signal(signal.SIGINT, handler)

if(len(sys.argv) != 4) :
        print("Erreur : mauvais nombre d'arguments.\npython client.py host port username")
        sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])
name = sys.argv[3]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
os.system("clear")

def write() :
	sys.stdout.write(name +" >> ") #affiche le nom sur le terminal
	sys.stdout.flush()             #ne compte pas le nom affiché

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
                        data = socket.recv(4096)
                        if data :
                                sys.stdout.write(data)   #On écrit le message du serveur sur l'entrée standard (terminal)
                                write()
                        else :
                                print('\rVous avez été deconnecté')
                                sys.exit()
                else :
                        msg = sys.stdin.readline()
                        server.send(msg)
                        write()

