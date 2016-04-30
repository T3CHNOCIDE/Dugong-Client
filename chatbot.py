#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    ____                                    				
                   / __ \ __  __ ____ _ ____   ____   ____ _				
                  / / / // / / // __ `// __ \ / __ \ / __ `/				
                 / /_/ // /_/ // /_/ // /_/ // / / // /_/ / 				
                /_____/ \____/ \__, / \____//_/ /_/ \__, /  				
                 -.. ..- --.  /____/   --- -. --.  /____/   				
																			
                             Dugong Chat Client								
                                   v1.1.0									
																			
    This program is free software: you can redistribute it and/or modify	
    it under the terms of the GNU General Public License as published by	
    the Free Software Foundation, either version 3 of the License, or		
    (at your option) any later version.										
																			
    This program is distributed in the hope that it will be useful,			
    but WITHOUT ANY WARRANTY; without even the implied warranty of			
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the			
    GNU General Public License for more details.							
																			
    You should have received a copy of the GNU General Public License		
    along with this program.  If not, see <http://www.gnu.org/licenses/>.	
																			
						Copyright (C) 2014 T3CHNOCIDE						
			  <http://community.wikia.com/wiki/User:T3CHNOCIDE>				
																			
	This chat module was inspired by Hairr's chat bot client. Using the		
	prefered requests module and with a simplified object architecture		
	for ease of use by new Python programmers. Recent updates borrowed from
	Sactage's Ruby chatbot because I'm not in the dev loop!
																			
	Hairr's chatbot <http://community.wikia.com/wiki/User:Hairr/Chatbot>	
	Sactage's chatbot <https://github.com/sactage/chatbot-rb>	
																			
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import re
import os
import sys
import json
import time
import urllib
import requests
from datetime import datetime
from threading import Thread
		
#Sets HTTP request session as global variable for saving/utilising cookies
global session
session = requests.session()

class Dugong(object):
	def __init__(self, site, username, password):
		"""
		Runs chatbot client from class.
		"""  
		
		self.chat_connect(site, username, password)
		
	##
	## METHODS ENCODING CHAT ROOM LOGIN AND BASIC SERVER INTERACTIONS
	##
	
	def login(self, site, username, password):
		"""
		Logs into the Wikia API and saves login cookies to the session.
		"""

		#Sets Wikia API and chat API URLs as global variables for later use
		global chat_site
		chat_site = 'http://' + site + '.wikia.com/wikia.php'
		
		global wikia_site
		wikia_site = 'http://' + site + '.wikia.com/api.php'
		
		#Sets initial login parameters using username and password
		login_data = { 
			'action'    : 'login',
			'lgname'    : username, 
			"lgpassword": password, 
			'format'    : 'json'
		}
		
		#Sends initial data to Wikia API
		#Saves cookies to session and keeps response data
		response = session.post(wikia_site, data=login_data)
		content = json.loads(response.text)

		#Parses login token from response data
		login_data['lgtoken'] = content['login']['token']

		#Re-sends data to Wikia API with login token
		#Saves additional cookies and keeps response data for errors
		response = session.post(wikia_site, data=login_data)
		content = json.loads(response.text)
		
		#Aborts program if there is an successful login
		if content['login']['result'] != 'Success':
			raise Exception("Login error: Could not log in via MediaWiki API.")
			
	def byte_encode(self, message):
		"""
		Encodes message in stupid format for chat.
		All information must be posted to chat in format: 
			\x00 + length of message in bytes + \xff + message as string
		"""
	
		#Converts message length (integer) to bytes (string)
		#Returns concatenated encoded length and message
		encoded_message = ""
		for number in str(len(message)):
			encoded_message += chr(int(number))
		return "\x00%s\xff%s" % (encoded_message, message)
		
	def post(self, data):
		"""
		Sends data to chat servers as post request and returns response.
		Data length is encoded in byte format by byte_encode() before sending
		to chat in format: message length in bytes + message string
		"""
		
		#Checks if post request is a chat ping
		if data == "keep-alive":
			body = self.byte_encode("2")
			chat_room_data_string = urllib.urlencode(chat_room_data)
			url = chat_room_url + '?' + chat_room_data_string
			chat_response = session.post(url, data=body, headers=chat_headers)
			
		#If post request is not chat ping, sends data as chat command
		else:
			body = self.byte_encode('42' + json.dumps(['message', json.dumps({'id': None, 'attrs': data})]))
			chat_room_data_string = urllib.urlencode(chat_room_data)
			url = chat_room_url + '?' + chat_room_data_string
			chat_response = session.post(url, data=body, headers=chat_headers)
			
		#Returns response
		return chat_response

	def restart(self):
		"""
		Restarts the program.
		"""

		#Reboots program using os and sys modules
		#Probably not a clean method...
		python = sys.executable
		os.execl(python, python, * sys.argv)

	def socket_connect(self):
		"""
		Creates daemon thread to run regular chat pings as a background process.
		"""
		
		#Sets up daemon thread and runs in background
		ping_thr = Thread(target=self.socket_ping)
		ping_thr.daemon = True
		ping_thr.start()

	def socket_ping(self):
		"""
		Regularly sends random ping to chat server every 24 seconds to keep connection alive.
		"""

		while True:
			#print "~ Ping sent to server. ~"
			self.post("keep-alive")
			time.sleep(24)

	def fetch_chat_info(self, site, username, password):
		"""
		Fetches chat server information and logs into chat.
		Saves chat data as global variables for later editing.
		"""
		
		#Logs into Wikia servers via API
		self.login(site, username, password)
		
		#Sets initial headers and parameters for GET request
		#Saves as global variable for later editing
		global chat_headers
		chat_headers = {
			"User-Agent" : "Dugong chat client v1.1.0",
			"Content-Type" : "application/octet-stream",
			"Accept" : "*/*",
			"Pragma" : "no-cache",
			"Cache-Control" : "no-cache"
		}
		
		chat_init_data = { "controller" : "Chat", "format" : "json" }
		
		#Performs GET request to Wikia chat servers to find and saves
		#current chat server and login tokens
		json_response = session.get(chat_site, params=chat_init_data, headers=chat_headers)
		json_content = json.loads(json_response.text)
		
		with open("temp_json.txt", "w") as temp_file:
			json.dump(json_content, temp_file, indent=5)
		
		chat_key = json_content["chatkey"]
		chat_room = json_content["roomId"]
		chat_host = json_content['chatServerHost']
		chat_port = json_content['chatServerPort'] #Not needed unless a developer
		chat_mod = json_content["isModerator"]
		
		#Performs GET request to Wikia API to find and save
		#cityId (wiki ID) as authentication now requires this
		chat_id_data = { "action" : "query", "meta" : "siteinfo", "siprop" : "wikidesc", "format" : "json" }
		json_response = session.get(wikia_site, params=chat_id_data, headers=chat_headers)
		json_content = json.loads(json_response.text)
		
		chat_server = json_content["query"]["wikidesc"]["id"]
		
		#Sets chat server headers
		#Saves as global variable for later editing
		global chat_room_data
		chat_room_data = {
			"name" : str(username),
			"EIO" : str(2),
			"transport" : "polling",
			"key" : str(chat_key),
			"roomId" : str(chat_room),
			"serverId" : str(chat_server),
			"wikiId" : str(chat_server)
		}
		
		#Sets chat room URL based on earlier server information
		global chat_room_url
		chat_room_url = "http://%s/socket.io/" % (chat_host)
		
		#Performs second GET request to get session ID for regular server 
		#communication and adds data to chat server headers
		json_response = session.get(chat_room_url, params=chat_room_data, headers=chat_headers)
		json_content = json.loads(json_response.text[5:])
		
		chat_room_data["sid"] = json_content["sid"]
		
		global bot_name
		bot_name = chat_room_data["name"]
		
	##
	## METHODS ENCODING CHAT EVENT RESPONSES
	##

	def on_join(self, username, rank):
		"""
		Blank method for override in separate file.
		Allows tailored bot response to users joining the chat. 
		"""
		
		pass

	def on_logout(self, username):
		"""
		Blank method for override in separate file.
		Allows tailored bot response to users leaving the chat. 
		"""
		
		pass

	def on_message(self, username, message):
		"""
		Blank method for override in separate file.
		Allows tailored bot response to users message the chat. 
		"""
		
		pass

	def on_kick(self, kickeduser, moderator):
		"""
		Blank method for override in separate file.
		Allows tailored bot response to a user being kicked from the chat. 
		"""
		
		pass

	def on_ban(self, kickeduser, moderator):
		"""
		Blank method for override in separate file.
		Allows tailored bot response to a user being banned from the chat. 
		"""
		
		pass
		
	##
	## METHODS ENCODING CHAT EVENT ACTIONS
	##
		
	def message(self, message):
		"""
		Sends a specified message to the chat
		"""
		
		self.post({'msgType': 'chat', 'text': message, 'name': bot_name})

	def kick(self, username):
		"""
		Kicks specified user from chat
		"""
		self.post({'msgType': 'command', 'command': 'kick', 'userToKick': username})
		
	def ban(self, username, length=7200, reason="Misbehaving in chat"):
		"""
		Bans specified user from chat
		Uses 2 hour ban and misbehhaving in chat as default length and reasons
		"""
		
		self.post({'msgType' : 'command', 'command' : 'ban', 'userToBan' : username, 'time' : length, 'reason' : reason})
		
	def unban(self, username):
		"""
		Bans specified user from chat
		Uses 2 hour ban and misbehhaving in chat as default length and reasons
		"""
		
		self.post({'msgType' : 'command', 'command' : 'ban', 'userToBan' : username, 'time' : 0, 'reason' : 'Undoing previous ban.'})

	def logout(self, disconnect=True):
		"""
		Logs bot out of chat cleanly
		"""
		
		self.post({'msgType': 'command', 'command': 'logout'})
		if disconnect:
			sys.exit()
		
	## 
	## METHODS ENCODING CHAT JOIN AND RESPONSE PARSER
	##
		
	def chat_event(self, content):
		"""
		Parses chat server responses by event type for bot logging/responses.
		"""
		
		if content["event"] == "chat:add":
			chat_data = json.loads(content["data"])
			if chat_data["attrs"]["name"].encode('ascii', 'xmlcharrefreplace') != "":
				self.on_message(chat_data["attrs"]["name"], chat_data["attrs"]["text"])
		elif content["event"] == "logout":
			chat_data = json.loads(content["data"])
			self.on_logout(chat_data["attrs"]["name"])
		elif content["event"] == "part":
			chat_data = json.loads(content["data"])
			self.on_logout(chat_data["attrs"]["name"])
		elif content["event"] == "join":
			chat_data = json.loads(content["data"])
			if chat_data["attrs"]["canPromoteModerator"]:
				self.on_join(chat_data["attrs"]["name"], "admin")
			elif chat_data["attrs"]["isModerator"]:
				self.on_join(chat_data["attrs"]["name"], "moderator")
			else:
				self.on_join(chat_data["attrs"]["name"], "none")
		elif content["event"] == "kick":
			chat_data = json.loads(content["data"])
			self.on_kick(chat_data["attrs"]["kickedUserName"], chat_data["attrs"]["moderatorName"])
		elif content["event"] == "ban":
			chat_data = json.loads(content["data"])
			self.on_ban(chat_data["attrs"]["kickedUserName"], chat_data["attrs"]["moderatorName"], str(chat_data["attrs"]["time"]), chat_data["attrs"]["reason"])
		elif content["event"] == "updateUser":
			pass
		
	def chat_connect(self, site, username, password):
		"""
		Connects to chat server and regularly retrieves server responses.
		"""
		
		#Fetches chat server information and creates headers
		self.fetch_chat_info(site, username, password)
		
		#Sets background server ping to keep connection alive
		self.socket_connect()
		
		#Run persistant while loop to regularly check server for new chat data
		while True:
			
			#Sets time frame of chat in UNIX time and saves to header
			unix = time.time()
			__timestamp__ = str(int(round(unix, 0)))
			chat_room_data['t'] = "{}-{}".format(__timestamp__, 0)
			
			#Requests new data from the chat
			json_response = session.get(chat_room_url, params=chat_room_data).content

			#Finds relevant JSON data from horrible format and parses for chat response
			if "\x00\x02\xff40" in json_response:
				match = re.findall('40\x00.*\xff42\[.*?,(.*)\]', json_response)
				try:
					content = json.loads(match[0])
					self.chat_event(content)
					
				except:
					#If the bot fails to join the chat, exits program
					print json_response
					print "Failed connect to chat."
					#sys.exit()

			elif "\xff42[" in json_response:
				match = re.findall('\x00.*\xff42\[.*?,(.*)\]', json_response)
				content = json.loads(match[0])
				self.chat_event(content)

			else:
				#If session ID expires, reboots program
				if "Session ID unknown" in str(json_response):
					print "Server forced exit - rebooting!"
					self.restart()
		
if __name__ == "__main__":
	print "\nThis module cannot be executed directly.\nPlease see Dugong client instructions: http://halo.wikia.com/wiki/User:T3CHNOCIDE\n"
