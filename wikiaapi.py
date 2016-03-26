#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
																			
                              Wikia API Wrapper
                                   v1.0.0

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

	This chat module was heavily influenced by Hairr's MediaWiki API using
	the Python requests module instead of the urllib module. The module is
	cut down compared to Hairr's API wrapper.
	
	Hairr's MediaWiki API <https://github.com/hairr/mwhair-r>
	
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import sys
import json
import requests
import wikiaapi

def login(site, username, password):
	"""
	Logs into the wiki and saves edit tokens for site updates
	"""
	
	global session
	session = requests.session()
	
	global wikia_site
	wikia_site = 'http://' + site + '.wikia.com/api.php'
	
	login_data = { 
		'action'    : 'login',
		'lgname'    : username, 
		"lgpassword": password, 
		'format'    : 'json'
	}
		
	response = session.post(wikia_site, params=login_data)
	content = json.loads(response.text)

	login_data['lgtoken'] = content['login']['token']

	response = session.post(wikia_site, params=login_data)
	content = json.loads(response.text)

	if content['login']['result'] == 'Success':
		edittokens()
	elif content ['login']['result'] == 'NeedToken':
		print 'Error occured while trying to log in...'
		sys.exit(1)
	elif content ['login']['result'] == 'WrongPass':
		print 'Incorrect password.'
		sys.exit(1)
	else:
		print 'Error occured.'
		sys.exit(1)

def edittokens():
	"""
	Saves edit tokens for log in cycle
	"""

	edit_token_data = {
		'action':'query',
		'prop':'info',
		'titles':'Main Page',
		'intoken':'edit|delete|protect|move|block|unblock|email|import',
		'format':'json'
	}
	
	response = session.post(wikia_site, params=edit_token_data)
	content = json.loads(response.text)
	
	s = content['query']['pages']
	thes = tuple(s.values())[0]
	try:
		warnings = content['warnings']['info']['*']
	except:
		warnings = None
	if warnings != None:
		if 'edit' in warnings:
			print 'No edit token: Quitting....'
			sys.exit(1)
		else:
			global edit_token
			edit_token = thes['edittoken']

		if 'delete' in warnings:
			global delete_token
			delete_token = None
		else:
			delete_token = thes['deletetoken']

		if 'protect' in warnings:
			global protect_token
			protect_token = None
		else:
			protect_token = thes['protecttoken']

		if 'move' in warnings:
			global move_token
			move_token = None
		else:
			move_token = thes['movetoken']

		if 'block' in warnings:
			global block_token
			block_token = None
		else:
			block_token = thes['blocktoken']

		if 'unblock' in warnings:
			global unblock_token
			unblock_token = None
		else:
			unblock_token = thes['unblocktoken']

		if 'email' in warnings:
			email_token = None
		else:
			email_token = thes['emailtoken']

		if 'import' in warnings:
			import_token = None
		else:
			import_token = thes['importtoken']
	else:
		edit_token = thes['edittoken']
		delete_token = thes['deletetoken']
		protect_token = thes['protecttoken']
		move_token = thes['movetoken']
		block_token = thes['blocktoken']
		unblock_token = thes['unblocktoken']
		email_token = thes['emailtoken']
		import_token = thes['importtoken']

def upload(filename, url, comment='', ignorewarnings=False):
	"""
	Uplaods image to wiki using url
	"""
	upload_data = {
		'action':'upload',
		'filename':filename,
		'url':url,
		'comment':comment,
		'token':edit_token,
		'format':'json'
	}
	
	if ignorewarnings == True:
		upload_data['ignorewarnings'] = True
	
	response = session.post(wikia_site, params=upload_data)
	content = json.loads(response.text)
	return content
	
def pageid(title):
	"""
	Fetches page ID of given article title
	"""
	pageid_data = {
		'action':'query',
		'prop':'revisions',
		'titles':title,
		'format':'json'
	}
	
	response = session.post(wikia_site, params=pageid_data)
	content = json.loads(response.text)
	s = content['query']['pages']
	thes = tuple(s.values())[0]
	pageid = thes['pageid']
	return pageid
	
def edit(title, page_text,summary='',minor=False,bot=True,section=False):
	"""
	Edits page with given article title and page contents.
	Optional parameters: edit summary, minor edit, bot edit and section number.
	"""
	save_data = {
		'action':'edit',
		'title':title,
		'summary':summary,
		'token':edit_token,
		'format':'json'
	}
	try:
		save_data['text'] = page_text.encode('utf-8')
	except:
		save_data['text'] = page_text
	
	if bot is False:
		pass
	else:
		save_data['bot'] = 'True'
	
	if minor != False:
		save_data['minor'] = minor
	
	if section != False:
		save_data['section'] = section
	
	if page_text:
		response = session.post(wikia_site, data=save_data)
		content = json.loads(response.text)
		return content

def view(title, section=None):
	"""
	Fetches current page contents from given title.
	Optional parameter: section number.
	"""
	read_page_data = {
		'action':'query',
		'prop':'revisions',
		'titles':title,
		'rvprop':'timestamp|content',
		'format':'json'
	}
	
	if section:
		read_page_data['rvsection'] = section
	
	response = session.post(wikia_site, data=read_page_data)
	content = json.loads(response.content)
	
	with open('edit_json.json', 'w') as outfile:
		json.dump(content, outfile)
	
	s = content['query']['pages']
	thes = tuple(s.values())[0]
	wikipage = ''
	try:
		wikipage = thes['revisions'][0]['*']
		return wikipage
	except KeyError:
		pass
		
def category(title, limit=None, namespace=None, pageid=False):
	"""
	Gets all pages in given category title (E.g. Category:Browse)
	Optional parameters: page number limit, page namespace, page id.
	"""
	category_data = {
		'action':'query',
		'list':'categorymembers',
		'cmtitle':title,
		'format':'json'
	}
	
	if limit:
		category_data['cmlimit'] = limit
	
	if namespace:
		category_data['cmnamespace'] = namespace
	
	response = session.post(wikia_site, data=category_data)
	content = json.loads(response.content)
	
	try:
		raise Warning(content["error"]["info"])
	except KeyError:
		pass
	
	category_members = content['query']['categorymembers']
		
	category_pages = []
	
	for category in category_members:
		
		if pageid:
			category_pages.append(category["pageid"])
		else:
			category_pages.append(category["title"])
			
	return category_pages
	
def protect(title, protections=None, length=None, reason=False):
	"""
	Protects page for given article title.
	Optional parameters: protection level, protection length and protection reason.
	"""
	
	protect_data = {
		'action' : 'protect',
		'title' : title,
		'token' : protect_token,
		'format' : 'json'
	}
	
	if length:
		protect_data['expiry'] = length
	else:
		protect_data['expiry'] = "infinite"
	
	if protections:
		protect_data['protections'] = 'edit=%s|move=%s' % protections
	else:
		protect_data['protections'] = 'edit=sysop|move=sysop'
		
	if reason:
		protect_data['reason'] = reason
	else:
		protect_data['reason'] = "Suspected vandalism."
	
	response = session.post(wikia_site, data=protect_data)
	content = json.loads(response.content)
	
	try:
		raise Warning(content["error"]["info"])
	except KeyError:
		pass
