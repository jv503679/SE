#!/usr/bin/env python
# coding: utf-8

import sys, socket, os, select, time

#Programme qui permet de tester le bon fonctionnement de chat client/serveur
#Test :
# - Connexion / Deconnexion
# - Connexion multiple
# - Envoi d'un message
# - Réception du message
# - Envois multiples / Reception multiple
# - Connexion web - recupération des derniers messages
#
#On utilise le modèle père/fils pour tester l'envoi/réception.

host = "localhost"
port = 2555

#Connexion / Déconnexion
def test1():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.connect((host, port))
    except:
        print("Test de connexion : fail")
        sys.exit()

    server.send("bot1")
    test_connexion = True
    test_deconnexion = False
    
    while test_connexion:
        socketlist = [sys.stdin, server]
        ready, write, error = select.select(socketlist, [], [])
        for s in ready:
            if s == server:
                message = s.recv(4096)
                if message :
                    print("Test de connexion : ok")
                    test_connexion = False
                    test_deconnexion = True
                else:
                    print("Test de connexion : fail")
                    sys.exit()

    server.send("\quit")
    
    while test_deconnexion:
        socketlist = [sys.stdin, server]
        ready, write, error = select.select(socketlist, [], [])
        for s in ready:
            if s == server:
                message = s.recv(4096)
                if message == "\rDéconnexion" :
                    print("Test de déconnexion : ok")
                    test_deconnexion = False
                else:
                    print("Test de déconnexion : fail")
                    sys.exit()
    server.close()

def test2():
    try:
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client1.connect((host, port))
        client1.send("bot1")
        client2.connect((host, port))
        client2.send("bot2")
    except:
        print("Test de connexion multiple : fail")
    
    print("Test de connexion multiple : ok")
    time.sleep(1)
    message_de_connexion = client2.recv(4096)
    message_test = "Coucou\n"
    test = True
    client1.send(message_test)
    while test:
        socketlist = [client1, client2]
        ready, write, error = select.select(socketlist, [], [])
        for s in ready:
            if s == client2:
                message = s.recv(4096)
                if(message == "\rbot1 >> " + message_test):
                    print("Test envoi/réception : ok")
                    test = False
                else:
                    print("Test envoi/réception : fail")
                    sys.exit()
                    
    client1.send("\quit")
    time.sleep(1)
    client2.send("\quit")
    time.sleep(1)
    client1.close()
    client2.close()

pid = os.fork()
if pid == 0:
    os.system("xterm -e python server.py 2555 2556")
else:
    time.sleep(2)
    test1()
    test2()
    sys.exit()
