# Dugong-Client
Python framework for connecting to the Wikia chat server.
Version: 1.1.0

How to run
======
To run this chat bot simply edit the settings.json file using any text editor and fill in the wikia site, username and password.

    {"site":"community", "username":"WikiaUser", "password":"Password123"}

Then run chatbot.py from the command line. 

Please note that the requests and json libraries must be installed prior to use. 
See PIP for more details: https://pip.pypa.io/en/stable/installing/

Features
======
This chat bot already has chat logging capabilities included. Logs are updated every hour to Project:Chat/Logs/DATE.

The chat bot also contains basic commands which can be run from the chat.

Admin commands
- !exit - Forces chat bot to leave chat
- !reboot - Forces program to restart

Mod commands
- !kick - Kicks specified user from the chat
- !ban - Bans specified user from the chat
- !unban - Unbans specified user from the chat
- !status - Returns basic chat bot running information
- !update - Forces chat log update prior to end of hour

Credits
======
This chat bot design has been heavily influenced by Hairr's Python chatbot (deprecated) and Sactage's Ruby chatbot. Please do take a look at their fantastic work:

Hairr's chatbot: http://community.wikia.com/wiki/User:Hairr/Chatbot
Sactage's chatbot: https://github.com/sactage/chatbot-rb
