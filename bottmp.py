#!/usr/bin/env python
# coding: utf-8

import sys, socket, os, select, time, re

#Programme qui permet de tester le bon fonctionnement de chat client/serveur
#Test :
# - Connexion / Deconnexion
# - Connexion multiple
# - Envoi d'un message
# - Réception du message
# - Envoi multiple / Reception multiple
# - Connexion web - recupération des derniers messages
#
#On utilise le modèle père/fils pour tester l'envoi/réception.

host = "localhost"
port = 2555
port_web = 2556

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

#Connexion multiples, envoi/réception unique
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

#Envoi/réception multiple
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
    client2.send("\quit")
    client3.send("\quit")
    time.sleep(1)
    client1.close()
    client2.close()
    client3.close()

#Connexion + requête web
def test4():
    client_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fake_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_web.connect((host, port_web))
    fake_client.connect((host, port_web))
    
    client_web.send("GET / HTTP/1.0")
    fake_client.send("Coucou passe le web stp")
    
    html = client_web.recv(4096)
    error = fake_client.recv(4096)

    client_web.close()
    fake_client.close()

    match_web = re.match("HTTP/1.0 200 OK\n", html)
    match_err = re.match('\rRequête non valide.\n', error)
    
    if match_web and match_err :
        print("Test web : ok")
    else:
        print("Test web : fail")
        sys.exit()

#Commandes \info
def test5() :
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("bot1")
    time.sleep(1)
    message_de_connexion_1 = client.recv(4096)
    client.send("\info\n")
    message = client.recv(4096)
    match = re.match("| Information sur le serveur |", message)
    if match:
        print("Test commande \\info : ok")
    else :
        print("Test commande \\info : fail")

    client.send("\quit")
    client.close()

#Commandes \list
def test6() :
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("bot1")
    time.sleep(1)
    message_de_connexion_1 = client.recv(4096)
    client.send("\list\n")
    message = client.recv(4096)
    match = re.match("| Clients connectés sur le serveur |", message)
    if match:
        print("Test commande \\list : ok")
    else :
        print("Test commande \\list : fail")

    client.send("\quit")
    client.close()

#Commandes \command
def test7() :
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("bot1")
    time.sleep(1)
    message_de_connexion_1 = client.recv(4096)
    client.send("\command\n")
    message = client.recv(4096)
    match = re.match("|     Commandes disponibles     |", message)
    if match:
        print("Test commande \\command : ok")
    else :
        print("Test commande \\command : fail")

    client.send("\quit")
    client.close()

#Message privé
def test8():
    #Client va envoyer un message, puis un message privé à receveur
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.send("client")
    m = client.recv(4096)

    #Reçoit le message privé
    receveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receveur.connect((host, port))
    receveur.send("receveur")
    m = receveur.recv(4096)

    #Permet de vérifier que le message privé est envoyé seulement au destinataire
    observer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    observer.connect((host, port))
    observer.send("observer")
    m = observer.recv(4096)

    message = "Coucou tout le monde\n"
    message_prive = "@receveur Coucou receveur\n"
    message_erreur = "@dalle Une bonne note svp\n"

    test = True

    msg = "\rclient >> Coucou tout le monde"
    msg_p = "\rfrom client: Coucou receveur"
    msg_e = "\r<SERVEUR> Client introuvable ! (\list pour la liste des clients)"
    
    socketlist = [client,receveur,observer]

    #On attend ici...
    msg_obs = ""  #Coucou tout le monde
    msg_rec = ""  #Coucou receveur
    msg_cli = ""  #Client introuvable!

    
    client.send(message)
    time.sleep(1)
    client.send(message_erreur)
    time.sleep(1)
    client.send(message_prive)
    
    while test:
        ready, write, error = select.select(socketlist, [], [])
            
        for s in ready:
            if s == client:
                msg_cli = s.recv(4096).split("\n")
                #Dernier message reçu (fini par \n, donc on prend -2 pour avoir le message plutot que "" pour -1)
                msg_cli = msg_cli[len(msg_cli)-2]
                
            if s == receveur:
                msg_rec = s.recv(4096).split("\n")
                msg_rec = msg_rec[len(msg_rec)-2]
                
            if s == observer:
                msg_obs = s.recv(4096).split("\n")
                msg_obs = msg_obs[len(msg_obs)-2]
                
            if msg_cli == msg_e and msg_obs == msg and msg_rec == msg_p:
                print("Test de message privé : ok")
                test = False

    client.send("\quit")
    receveur.send("\quit")
    observer.send("\quit")
    time.sleep(1)
    client.close()
    receveur.close()
    observer.close()

def test9():
    os.system("umask 000")
    os.system("touch fichiertest.txt")
    pid = os.fork()
    if pid == 0 :
        time.sleep(3)
        os.system("xterm -e python clienttest1.py localhost 2555 bot1 coucou salut")
    else :
        pid = os.fork()
        if pid == 0 :
            os.system("xterm -e python clienttest2.py localhost 2555 bot2 coucou salut")
        else :
            time.sleep(10)
            f = open("fichiertest.txt","r")
            print(f.read())
            f.close()
            os.system("rm fichiertest.txt")
    
    
pid = os.fork()
if pid == 0:
    os.system("xterm -e python server.py 2555 2556")
else:
    time.sleep(2)
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
    test9()
    
sys.exit()
