#!/usr/bin/env python
# coding: utf-8

import sys, socket, os, select, time , re

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

def test3() :
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((host, port))
    client1.send("bot1")
    client2.connect((host, port))
    client2.send("bot2")
    client3.connect((host, port))
    client3.send("bot3")
    time.sleep(1)
    message_de_connexion_1 = client1.recv(4096)
    message_de_connexion_2 = client2.recv(4096)
    message_de_connexion_3 = client3.recv(4096)
    message_test_1 = "Coucou\n"
    message_test_2 = "Salut\n"
    try :
        client1.send(message_test_1)
        client2.send(message_test_2)
        print("Test envoi multiple : ok")
    except :
        print("Test envoi multiple : fail")
        sys.exit()
    test = True
    while test :
        socketlist = [client1, client2, client3]
        ready, write, error = select.select(socketlist, [], [])
        for s in ready :
            if s == client3 :
                message_1 = s.recv(4096)
                message_2 = s.recv(4096)
                if ((message_1 == "\rbot1 >> " + message_test_1 or message_1 == "\rbot2 >> " + message_test_2) and (message_2 == "\rbot1 >> " + message_test_1 or message_2 == "\rbot2 >> " + message_test_2)) :
                    print("Test réception multiple : ok")
                    test = False
                else :
                    print("Test réception multiple : fail")
                    sys.exit()
    client1.send("\quit")
    time.sleep(1)
    client2.send("\quit")
    time.sleep(1)
    client3.send("\quit")
    time.sleep(1)
    client1.close()
    client2.close()
    client3.close()

#test4() pour connexion web

def test5() :
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client1.connect((host, port))
    client1.send("bot1")
    time.sleep(1)
    message_de_connexion_1 = client1.recv(4096)
    client1.send("\info\n")
    message_1 = client1.recv(4096)
    print(message_1) #pour voir visuellement le message reçu , à enlever
    if re.match(r"(.)*Information(.)*",message_1) is not None : #http://apprendre-python.com/page-expressions-regulieres-regular-python
        print("Test commande \\info : ok")
    else :
        print("Test commande \\info : fail")
    

pid = os.fork()
if pid == 0:
    os.system("xterm -e python server.py 2555 2556")
else:
    time.sleep(2)
    test1() #à revoir
    test2()
    test3()
    #test4()
    test5() #à revoir
sys.exit()
