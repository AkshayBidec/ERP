# this page contains all the data about the leads
# from apploiERP.LoginPage import first_time_login_SA
import _pickle as cPickle
import xmlrpc.client as xmlrpclib # import the rpc file
import json as json # JSON library

import ssl


def leads_add():
	
	serverport=request.env.http_host

	session.message=" "
	lRequestData={
	'request_type': 'get',		# get and add
	'lead_key_id': '16',
	'user_id': 2,				##############
	'company_id':25,		##############
	'update_head': 'notes',
	'update_data': 'yes',
	'lead_status_id':1,					#request.vars.status_id,
	'session_id':0		##############
	#'lead_update_id':request.vars.lead_update_id
	}
	link=str(request.env.wsgi_url_scheme)+"://"+str(request.env.http_host)+str(URL('CRM','Leads','call/xmlrpc'))
	
	if lRequestData['request_type']=='get': 		# we just have to send the table
		
		# make the connection to the desired server
		context = ssl.SSLContext()
		leadserver = xmlrpclib.ServerProxy(link,allow_none=True,context=context)	# make the connection to the api server of lead

		lData={}		# a dict to store the respose data

		
		try:		# try to get the data
			lData = leadserver.fetch_lead_update_details(lRequestData)			#	dict(data=lRequestData)
			pass
		except Exception as e:
			session.message=" error in geting the leads update %s" %e
			 
		else:
			# data= json.dumps(lData)
			pass

	return locals()



# # def call(): return service()

# def tester():
# 	import xmlrpclib
# 	server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/test/call/xmlrpc')

# 	session.a=1
# 	session.b=2

# 	# data= server.add(3242,1)
# 	data= server.sub(session.a,session.b)
# 	session.b+=2
# 	return dict(data=data)