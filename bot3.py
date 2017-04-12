#!/usr/bin/env python
# coding: utf-8

import sys, socket, os, time, signal, select

#Programme qui permet de tester le bon fonctionnement du client
#Le programme du client utiliser pour ces test est un copie conforme du
#programme client de base , avec en plus des ajouts permettant de
#réaliser ces tests

#Tests :
# - Réception de message
# - Envoi de message
#
#On utilise le modèle père fils pour tester l'envoi/réception.

host = "localhost"
port = 2555

socketlist = []

def handler(signal, none) :
    for s in socketlist :
        s.close()
    sys.exit()

signal.signal(signal.SIGINT, handler)

        
pid = os.fork()
if pid == 0 :
    time.sleep(3)
    os.system("xterm -e python clienttest.py localhost 2555 bot1 test2 coucou")
    time.sleep(5)
    sys.exit()
else :
    #création de serveur de test pour le client
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(10)
    socketlist.append(server)
    while True :
        rsockets, wsockets, esockets = select.select(socketlist, [], [])
        for socket in rsockets:
            if socket == server :
                newsocket, ipport = server.accept()
                socketlist.append(newsocket)
                name = newsocket.recv(4096)
            else :
                message = socket.recv(4096)
                user = socket.getpeername()
                if message == "coucou" :
                    print("Test envoi : ok")
                else :
                    print("Test envoi : fail")
                handler(signal.SIGINT,0)

        


