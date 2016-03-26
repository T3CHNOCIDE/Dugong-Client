# Dugong-Client
Python framework for connecting to the Wikia chat server.

How to run
======
To run this chat bot simply edit the settings.json file using any text editor and fill in the wikia site, username and password.

    {"site":"community","username":"WikiaUser", "password":"Password123"}

Then run chatbot.py from the command line. 

Please note that the requests and json libraries must be installed prior to use. 
See PIP for more details: https://pip.pypa.io/en/stable/installing/

Features
======
This chat bot already has chat logging capabilities included. Logs are updated every hour to Project:Chat/Logs/DATE.

The chat bot also contains basic commands which can be run from the chat.

Admins commands
*!exit - Forces chat bot to leave chat
*!reboot - Forces program to restart

Mod commans
*!kick - Kicks specified user from the chat
*!ban - Bans specified user from the chat
*!unban - Unbans specified user from the chat
*!status - Returns basic chat bot running information
*!update - Forces chat log update prior to end of hour
