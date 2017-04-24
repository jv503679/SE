# Projet de CHAT IRC
Connexions multiples / déconnexions  
Gestion de la connexion via le web // sauvegarde des derniers messages envoyés  
Gestion des usernames (pas de duplicate)  
Gestion des messages privés (@Username message)  
Gestion des commandes (\quit, \list, \info, \command)  
## server.py
Programme du serveur  
Lancement : python server.py port port_web  
## client.py
Programme du client  
Lancement : python client.py host port username  
## bot.py
Programme principal de test du client et du serveur  
Lancement : python bot.py
## cbot1.py
Programme du bot de test d'envoi du message via le client  
Lancement : python cbot1.py host port username message1 message2  
(lancé automatiquement via bot.py, ne pas lancer indépendamment)
## cbot2.py
Programme du bot de test de réception du message via le client  
Lancement : python cbot1.py host port username message1 message2  
(lancé automatiquement via bot.py, ne pas lancer indépendamment)
