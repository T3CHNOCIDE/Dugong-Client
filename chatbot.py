#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    ____                                    				
                   / __ \ __  __ ____ _ ____   ____   ____ _				
                  / / / // / / // __ `// __ \ / __ \ / __ `/				
                 / /_/ // /_/ // /_/ // /_/ // / / // /_/ / 				
                /_____/ \____/ \__, / \____//_/ /_/ \__, /  				
                 -.. ..- --.  /____/   --- -. --.  /____/   				
																			
                           Dugong Chat Framework
                                   v1.2.0
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
	for ease of use by new Python programmers. Chat bot client improved
	using Sactage's chat bot client (written in Ruby).
	
	Hairr's chatbot <http://community.wikia.com/wiki/User:Hairr/Chatbot>
	Sactage's chatbot <https://github.com/sactage/chatbot-rb>
	
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import os
import sys
import time
import json
import dugong
import wikiaapi
from threading import Thread
from datetime import datetime

class ChatBot(dugong.Dugong):	
	def __init__(self, site, username, password):
		"""
		Runs chatbot client from class.
		"""  
		
		#Set global variables within the class
		global admin_list
		admin_list = []

		global mod_list
		mod_list = []

		global bot_start_time
		bot_start_time = datetime.utcnow()
		
		#Starts regular chat ping and connects to chat
		self.log_thread()
		self.chat_connect(site, username, password)
		
	def on_join(self, username, rank):
		"""
		Method for action on user joining the chat.
		"""
	
		#Bypass unicode errors when printing/saving (because Py 2.7 unicode sucks)
		unic_username = username.encode('ascii', 'xmlcharrefreplace')
		
		#Writes user joining chat to temporary chat log file
		chat_time = datetime.utcnow().strftime("%H:%M:%S")
		with open("chat_log.txt", "a") as log_file:
			log_file.write("[%s] ~ %s has joined the chat. ~\n" % (chat_time, unic_username))
		log_file.close()
		print "[%s] ~ %s has joined the chat. ~" % (chat_time, unic_username)
		
		#Saves usergroup information for command permissions
		#If user demoted, removes from admin/mod list
		if rank == "admin":
			if unic_username not in admin_list:
				admin_list.append(unic_username)
		elif rank == "moderator":
			if unic_username not in mod_list:
				mod_list.append(unic_username)
		else:		
			if unic_username in admin_list:
				list_index = admin_list.index(unic_username)
				admin_list.pop(list_index)
			if unic_username in mod_list:
				list_index = mod_list.index(unic_username)
				mod_list.pop(list_index)

	def on_logout(self, username):
		"""
		Method for action on user leaving the chat.
		"""
		
		#Bypass unicode errors when printing/saving
		unic_username = username.encode('ascii', 'xmlcharrefreplace')
		
		#Writes user leaving chat to temporary chat file
		chat_time = datetime.utcnow().strftime("%H:%M:%S")
		with open("chat_log.txt", "a") as log_file:
			log_file.write("[%s] ~ %s has left the chat. ~\n" % (chat_time, unic_username))
		log_file.close()
		print "[%s] ~ %s has left the chat. ~" % (chat_time, unic_username)

	def on_message(self, username, message):
		"""
		Method for action on user messages the chat.
		"""
		
		#Bypass unicode errors when printing/saving
		unic_message = message.encode('ascii', 'xmlcharrefreplace')
		unic_username = username.encode('ascii', 'xmlcharrefreplace')
	
		#Writes message structure to temp file and terminal for chat logging
		chat_time = datetime.utcnow().strftime("%H:%M:%S")
		with open("chat_log.txt", "a") as log_file:
			log_file.write("[%s] %s: %s\n" % (chat_time, unic_username, unic_message))
		log_file.close()
		print "[%s] %s: %s" % (chat_time, unic_username, unic_message)
		
		#Ensures message is a command before parsing (saves on memory)
		if message.startswith("!"):
		
			##
			##Admin Commands
			##
			
			#Forces clean exit from chat
			if message.startswith("!exit") and username in admin_list:
				self.message('Exiting the chat!')
				sys.exit()
			#Forces program to reboot
			elif message.startswith("!reboot") and username in admin_list:
				self.restart()
			
			##			
			##Mod Commands
			##
			
			#Kicks specified user from the chat
			#Format: !kick>username
			elif message.startswith("!kick") and (username in admin_list or username in mod_list):
				kicked_user = message.split(">")[-1]
				self.kick(kicked_user)
			#Bans specified user from the chat
			#Format: !ban>username[>length][>reason] (length and reason optional)
			elif message.startswith("!ban") and (username in admin_list or username in mod_list):
				banned_info = message.split(">")
				if len(banned_info) == 2:
					self.ban(banned_info[-1])
				elif len(banned_info) == 3:
					try:
						ban_length = int(banned_info[-1])
						self.ban(banned_info[1], length=ban_length)
					except ValueError:
						self.ban(banned_info[1], reason=banned_info[2])
				elif len(banned_info) == 4:
					try:
						ban_length = int(banned_info[-1])
						self.ban(banned_info[1], length=ban_length, reason=banned_info[2])
					except ValueError:
						self.ban(banned_info[1], length=banned_info[2], reason=banned_info[3])
				else:
					self.message('Command syntax error.')
			#Unbans specified user from the chat
			#Format: !unban>username
			elif message.startswith("!unban") and (username in admin_list or username in mod_list):
				banned_user = message.split(">")[-1]
				self.unban(banned_user)
			#Returns basic bot operation information
			elif message.startswith("!status") and (username in admin_list or username in mod_list):
				time_on_bot = datetime.utcnow().strftime("%H:%M:%S %d %B %Y")
				running_diff = datetime.utcnow() - bot_start_time
				log_diff = datetime.utcnow() - last_log_time
			
				rseconds = running_diff.seconds
				rminutes, rseconds = divmod(rseconds, 60)
				rhours, rminutes = divmod(rminutes, 60)
				rdays, rhours = divmod(rhours, 24)
				lseconds = log_diff.seconds
				lminutes, lseconds = divmod(lseconds, 60)
				lhours, lminutes = divmod(lminutes, 60)
				ldays, lhours = divmod(lhours, 24)
				
				running_time = "%s days, %s hours, %s minutes and %s seconds" % (rdays, rhours, rminutes, rseconds)
				log_time = "%s days, %s hours, %s minutes and %s seconds" % (ldays, lhours, lminutes, lseconds)
				status_response = "Time on bot is: %s UTC.\nBot has been running for %s.\nLast log was %s." % (time_on_bot, running_time, log_time)
				self.message(status_response)
			#Forces bot to add chat logs to the wiki
			elif message.startswith("!update") and (username in admin_list or username in mod_list):
				self.force_chat_log()
				current_log = "[[Project:Chat/Logs/%s|Chat logs]] updated!" % datetime.utcnow().strftime("%d %B %Y")
				self.message(current_log)
			
	def on_kick(self, kickeduser, moderator):
		"""
		Method for action on user being kicked from the chat.
		"""
		
		#Bypass unicode errors when printing/saving
		unic_kickeduser = kickeduser.encode('ascii', 'xmlcharrefreplace')
		unic_moderator = moderator.encode('ascii', 'xmlcharrefreplace')
		
		#Writes user being kicked from chat to temporary chat log file
		chat_time = datetime.utcnow().strftime("%H:%M:%S")
		with open("chat_log.txt", "a") as log_file:
			log_file.write("[%s] ~ %s has been kicked by %s. ~\n" % (chat_time, unic_kickeduser, unic_moderator))
		log_file.close()
		print "[%s] ~ %s has been kicked by %s. ~" % (chat_time, unic_kickeduser, unic_moderator)
			
	def on_ban(self, banneduser, moderator, time, reason):
		"""
		Method for action on user being banned/unbanned from the chat.
		"""
		
		#Bypass unicode errors when printing/saving
		unic_reason = reason.encode('ascii', 'xmlcharrefreplace')
		unic_banneduser = banneduser.encode('ascii', 'xmlcharrefreplace')
		unic_moderator = moderator.encode('ascii', 'xmlcharrefreplace')
		
		#Checks if user was banned or unbanned before writing the user being
		#banned from the chat to temporary chat log file
		chat_time = datetime.utcnow().strftime("%H:%M:%S")
		if int(time) == 0:
			print "[%s] ~ %s has been unbanned by %s. ~" % (chat_time, unic_banneduser, unic_moderator)
			with open("chat_log.txt", "a") as log_file:
				log_file.write("[%s] ~ %s has been unbanned by %s. ~\n" % (chat_time, unic_banneduser, unic_moderator))
			log_file.close()
		else:
			print "[%s] ~ %s has been banned by %s. ~" % (chat_time, unic_banneduser, unic_moderator)
			with open("chat_log.txt", "a") as log_file:
				log_file.write("[%s] ~ %s has been banned by %s. ~\n" % (chat_time, unic_banneduser, unic_moderator))
			log_file.close()
			
			#Adds ban warning template to banned users talk page
			#See http://halo.wikia.com/wiki/Template:Chat_ban for example template
			talk_page = "User_talk:%s" % banneduser
			ban_date = datetime.utcnow().strftime("%d %B %Y")			
			ban_template = "==Chat Ban: %s==\n{{Chat ban|user=%s|mod=%s|reason=%s|length=%s|date=%s}}\n" % (ban_date, banneduser, moderator, reason, time, ban_date)
			
			talk_contents = wikiaapi.view(talk_page)
			if not talk_contents:
				talk_contents = ""
			talk_contents += ban_template

			wikiaapi.edit(talk_page, talk_contents,summary='Automatically adding chat ban information.')
			
	def log_thread(self):
		"""
		Creates daemon thread to run regular chat logs.
		"""
		
		#Sets up daemon thread and runs in background
		log_thr = Thread(target=self.chat_log)
		log_thr.daemon = True
		log_thr.start()

	def chat_log(self):
		"""
		Regularly uploads cached chat logs to the wiki every hour.
		"""

		while True:
			print "[%s] ~ Uploading Chat Log. ~" % datetime.utcnow().strftime("%H:%M:%S")
			log_title = "Project:Chat/Logs/%s" % datetime.utcnow().strftime("%d %B %Y")
			
			#Fetches temporary log file and truncates ready for next hour
			with open("chat_log.txt", "r+") as log_file:
				log_data = log_file.read()
			log_file.close()
			with open("chat_log.txt", "r+") as log_file:
				log_file.truncate()
			log_file.close()
			
			#Gets current log from wiki and extends with temporary log file
			#If log doesn't exist, creates new page
			page_text = wikiaapi.view(log_title)
			if page_text:
				page_text = page_text[5:][:-33]
				page_text += log_data
				page_text = "<pre>%s</pre>[[Category:Chat_logs/%s]]" % (page_text, datetime.utcnow().strftime("%Y"))
			else:
				page_text = "<pre>%s</pre>[[Category:Chat_logs/%s]]" % (log_data, datetime.utcnow().strftime("%Y"))
			
			#Saves log to wiki and protects page
			wikiaapi.edit(log_title, page_text,summary='Automated chat log update.')
			wikiaapi.protect(log_title, reason="Automatically protecting chat log.")
			
			#Saves last log time for !status command
			global last_log_time
			last_log_time = datetime.utcnow()
			
			#Sets chat log to sleep until end of next hour
			sleep_diff = (int(datetime.utcnow().strftime("%M")) * 60) + int(datetime.utcnow().strftime("%S"))
			sleep_time = (3600 - sleep_diff)
			
			if sleep_time <= 0:
				sleep_time = 3600 - int(datetime.utcnow().strftime("%S"))
				time.sleep(sleep_time)
			else:
				time.sleep(sleep_time)
				
	def force_chat_log(self):
		"""
		Forces upload of cached chat logs to the wiki.
		"""

		print "[%s] ~ Uploading Chat Log. ~" % datetime.utcnow().strftime("%H:%M:%S")
		log_title = "Project:Chat/Logs/%s" % datetime.utcnow().strftime("%d %B %Y")
		
		#Fetches temporary log file and truncates ready for next hour
		with open("chat_log.txt", "r+") as log_file:
			log_data = log_file.read()
		log_file.close()
		with open("chat_log.txt", "r+") as log_file:
			log_file.truncate()
		log_file.close()
		
		#Gets current log from wiki and extends with temporary log file
		#If log doesn't exist, creates new page
		page_text = wikiaapi.view(log_title)
		if page_text:
			page_text = page_text[5:][:-33]
			page_text += log_data
			page_text = "<pre>%s</pre>[[Category:Chat_logs/%s]]" % (page_text, datetime.utcnow().strftime("%Y"))
		else:
			page_text = "<pre>%s</pre>[[Category:Chat_logs/%s]]" % (log_data, datetime.utcnow().strftime("%Y"))
		
		#Saves log to wiki and protects page
		wikiaapi.edit(log_title, page_text,summary='Admin/moderator forced chat log update.')
		wikiaapi.protect(log_title, reason="Automatically protecting chat log.")
		
		#Saves last log time for !status command
		global last_log_time
		last_log_time = datetime.utcnow()
		
if __name__ == "__main__":
	#Checks if settings file, aborts if not set
	if os.path.exists("settings.json"):
		#Fetches user information from settings file
		with open('settings.json') as settings_file:    
			local_settings = json.load(settings_file)
		#Logs into wiki for log writing then initiates chat bot client
		wikiaapi.login(local_settings["site"], local_settings["username"], local_settings["password"])
		ChatBot(local_settings["site"], local_settings["username"], local_settings["password"])
	else:
		raise Exception('Local settings file not found!')
