# this page contains all the data about the leads
# from apploiERP.LoginPage import first_time_login_SA
import _pickle as cPickle
import xmlrpc.client as xmlrpclib # import the rpc file
import json as json # JSON library
import os
import ssl

def download(): return response.download(request,db)
def link(): return response.download(request,db,attachment=False)
 
def leads_add():
	form = SQLFORM.factory(
		Field('name','string','_required')
		)
	# form.custom.widget.name['_required']=''
	return locals()
	
