#!/usr/bin/env python

'''
Este script publica el reporte de la prediccion automaticamente en twitter y facebook
'''

import ConfigParser
import getopt
import os
import sys
import twitter
import facebook
import time

__author__ = 'david@villacis.com'

USAGE = '''

Uso: tweet [opciones] mensaje url_media

	Opciones:
	-h --help : Imprime este mensaje
	--consumer_key : twitter consumer key
	--consumer_secret : twitter consumer secret
	--access_key : twitter access token key
	--access_secret : twitter access token secret
	--facebook_app_id : facebook application id
	--facebook_app_secret : facebook application secret
	--facebook_page_id : facebook page id
	--only_twitter : publish twitter only
	--only_facebook : publish facebook only
	--encoding : codificacion de caracteres, "utf-8". [opcional]

	Las credenciales deben estar almacenadas en el archivo .meteosocialconf

'''


def PrintUsageAndExit():
	print USAGE
	sys.exit(2)


def GetConsumerKeyEnv():
	return os.environ.get("TWEETUSERNAME", None)


def GetConsumerSecretEnv():
	return os.environ.get("TWEETPASSWORD", None)


def GetAccessKeyEnv():
	return os.environ.get("TWEETACCESSKEY", None)


def GetAccessSecretEnv():
	return os.environ.get("TWEETACCESSSECRET", None)


def GetFBAppIdEnv():
	return os.environ.get("FACEBOOKAPPID", None)


def GetFBAppSecretEnv():
	return os.environ.get("FACEBOOKAPPSECRET", None)


def GetFBPageIdEnv():
	return os.environ.get("FACEBOOKPAGEID", None)


def GetOnlyFBEnv():
	return os.environ.get("ONLYFACEBOOK", None)


def GetOnlyTwitterEnv():
	return os.environ.get("ONLYTWITTER", None)


class TweetRc(object):

	def __init__(self):
		self._config = None

	def GetConsumerKey(self):
		return self._GetOption('consumer_key')

	def GetConsumerSecret(self):
		return self._GetOption('consumer_secret')

	def GetAccessKey(self):
		return self._GetOption('access_key')

	def GetAccessSecret(self):
		return self._GetOption('access_secret')

	def GetFBAppId(self):
		return self._FBGetOption('facebook_app_id')

	def GetFBAppSecret(self):
		return self._FBGetOption('facebook_app_secret')

	def GetFBPageId(self):
		return self._FBGetOption('facebook_page_id')

	def GetOnlyFB(self):
		return self._FBGetOption('only_facebook')

	def GetOnlyTwitter(self):
		return self._FBGetOption('only_twitter')

	def _GetOption(self, option):
		try:
			return self._GetConfig().get('Tweet', option)
		except:
			return None

	def _FBGetOption(self, option):
		try:
			return self._GetConfig().get('FBPost', option)
		except:
			return None

	def _GetConfig(self):
		if not self._config:
			self._config = ConfigParser.ConfigParser()
			self._config.read(os.path.expanduser('.meteosocialconf'))
		return self._config


def main():
	try:
		shortflags = 'h'
		longflags = ['help', 'consumer_key=', 'consumer_secret='
															, 'access_key=', 'access_secret=', 'facebook_app_id='
															, 'facebook_app_secret=', 'facebook_page_id='
															, 'only_twitter=', 'only_facebook=', 'encoding=']
		opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)

	except getopt.GetoptError:
		PrintUsageAndExit()

	consumer_keyflag = None
	consumer_secretflag = None
	access_keyflag = None
	access_secretflag = None
	encoding = None
	facebook_app_idflag = None
	facebook_app_secretflag = None
	facebook_page_idflag = None
	only_facebookflag = False
	only_twitterflag = False

	for o,a in opts:
		if o in ("h", "--help"):
			PrintUsageAndExit()
		if o in ("--consumer_key"):
			consumer_keyflag = a
		if o in ("--consumer_secret"):
			consumer_secretflag = a
		if o in ("--access_key"):
			access_keyflag = a
		if o in ("--access_secret"):
			access_secretflag = a
		if o in ("--encoding"):
			encoding = a
		if o in ("--facebook_app_id"):
			facebook_app_idflag = a
		if o in ("--facebook_app_secret"):
			facebook_app_secretflag = a
		if o in ("--facebook_page_id"):
			facebook_page_idflag = a
		if o in ("--only_facebook"):
			only_facebookflag = a
		if o in ("--only_twitter"):
			only_twitterflag = a

	message = ';'.join(args)
	if not message and len(args) < 2:
		PrintUsageAndExit()

	rc = TweetRc()
	consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
	consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
	access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
	access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
	facebook_app_id = facebook_app_idflag or GetFBAppIdEnv() or rc.GetFBAppId()
	facebook_app_secret = facebook_app_secretflag or GetFBAppSecretEnv() or rc.GetFBAppSecret()
	facebook_page_id = facebook_page_idflag or GetFBPageIdEnv() or rc.GetFBPageId()
	only_facebook = only_facebookflag or GetOnlyFBEnv() or rc.GetOnlyFB()
	only_twitter = only_twitterflag or GetOnlyTwitterEnv() or rc.GetOnlyTwitter()

	if not consumer_key or not consumer_secret or not access_key or not access_secret or \
		not facebook_app_id or not facebook_app_secret or not facebook_page_id:

		PrintUsageAndExit()

	# Inicializacion del API de Twitter
	api = twitter.Api(consumer_key=consumer_key
																			, consumer_secret=consumer_secret
																			, access_token_key=access_key
																			, access_token_secret=access_secret
																			, input_encoding=encoding)

	# Inicializacion del Graph API de Facebook
	acc_tk = facebook.GraphAPI().get_app_access_token(facebook_app_id, facebook_app_secret)
	graph = facebook.GraphAPI(access_token=acc_tk)
	profile = graph.get_object('me')

	try:
		mensaje = message.split(';')[0]
		path_mapa = message.split(';')[1]

		# Publicacion en Twitter
		if not only_facebook and not only_twitter:
			status = api.PostMedia(mensaje, path_mapa)
			graph.put_wall_post(mensaje, attachment=fb_attachment, profile_id=facebook_page_id)
			print "%s posteo en twitter %s" % (status.user.name, status.text)
			print "%s posteo en facebook %s" % (profile['name'], mensaje)
		else:
			if only_facebook:
				graph.put_wall_post(mensaje, profile_id=facebook_page_id)
				print "%s posteo en facebook %s" % (profile['name'], mensaje)
			else:
				status = api.PostMedia(mensaje, path_mapa)
				print "%s posteo en twitter %s" % (status.user.name, status.text)
		# graph.put_object(parent_object=facebook_page_id, connection_name='feed', message=mensaje)
	except UnicodeDecodeError:
		print "Su mensaje no pudo ser codificado. Esta usando caracteres no ASCII?"
		print "Puede especificar la codificacion usando la bandera --encoding"
		sys.exit(2)

if __name__ == "__main__":
	main()













