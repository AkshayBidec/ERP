import _pickle as cPickle
import xmlrpc.client as xmlrpclib # import the rpc file
import json as json # JSON library
# it will contain all the views and the api call related to the crm app
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CRM--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def crm():
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--LEADS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads():
	# this function is responcible for the main leads dahboard
	# by default it will contain 10 leads per page
	
	if session.active==1:

				# import the rpc file

		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)		# make the connection to the api server

		lLimit={}		# this dic is to get a single data or a range of data from the api

		lLimit['countTo']=10		# total number of fieds required, replace it with request.vars.* to make it dynamin
		lLimit['countFrom']=0		# no of the row to start from 
		lLimit['order']='~db.crm_lead_field_key.id' 	# the name of field to order on, string will be evaluated in the api
		
		lLeadsList= server.get_leads(lLimit)		# get the data from the api
		# data= cPickle.loads(lLeadsList)

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	return dict(data= lLeadsList)
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_add():
	if session.active==1:
		
		
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)	# make the connection to the api server

		form_fields=server.leads_add_ff()		# ask for the list of the field to make the form and store it into a dict

		fields=[]

		for key in sorted(form_fields.keys()):			# take key one by one in a sequence and make the field list
			if form_fields[key][0]:
				widget=eval(form_fields[key][0])
			else:
				widget='SQLFORM.widgets.string.widget' 		# a default value for a field if the widget not given
			requires=eval(form_fields[key][1]) 		# it is a list and can be empty
			fields.append(Field(key,widget=widget, requires=requires))

		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory

		for key in form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			exec(place)


		if lForm.process().accepted:		
			form_fields.update(lForm.vars)			# store the data into the dict

			form_fields['user_id']=session.user_id			# add other required data
			form_fields['company_id']=session.company_id
			form_fields['session_id']=session.session_id

			# send the data back to the api app
			try:    
				responce= server.add_leads(form_fields) 		# send the dictioinary to the server
				session.message= str(responce)
				session.flash= str(responce)
			except Exception as e:
				session.message=" error while adding leads (%s)" %e.message
				session.flash=" error while adding leads (%s)" %e.message
			else:
				# redirect to the home page
				redirect('leads')
				pass
			pass

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_update():
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_edit():
	return locals()


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CONTACTS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts():
	# this function is responcible for the main contact dahboard
	# by default it will contain 10 contact per page
	
	if session.active==1:


		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)		# make the connection to the api server

		lLimit={}		# this dic is to get a single data or a range of data from the api

		lLimit['countTo']=10		# total number of fieds required, replace it with request.vars.* to make it dynamin
		lLimit['countFrom']=0		# no of the row to start from 
		lLimit['order']='~db.crm_contact_field_key.id' 	# the name of field to order on, string will be evaluated in the api
		
		lContactList= server.get_contact(lLimit)		# get the data from the api
		# data= cPickle.loads(lLeadsList)

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	return dict(data= cPickle.loads(lContactList))

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_add():
	if session.active==1:
		
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)	# make the connection to the api server

		form_fields=server.contact_add_ff()		# ask for the list of the field to make the form and store it into a dict

		fields=[]

		for key in sorted(form_fields.keys()):			# take key one by one in a sequence and make the field list
			if form_fields[key][0]:
				widget=eval(form_fields[key][0])
			else:
				widget='SQLFORM.widgets.string.widget' 		# a default value for a field if the widget not given
			requires=eval(form_fields[key][1]) 		# it is a list and can be empty
			fields.append(Field(key,widget=widget, requires=requires))

		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory

		for key in form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			exec(place)

		if lForm.process().accepted:		
			form_fields.update(lForm.vars)			# store the data into the dict

			form_fields['user_id']=session.user_id			# add other required data
			form_fields['company_id']=session.company_id
			form_fields['session_id']=session.session_id

			# send the data back to the api app
			try:    
				responce= server.add_contact(form_fields) 		# send the dictioinary to the server
				session.message= str(responce)
				session.flash= str(responce)
			except Exception as e:
				session.message=" error while adding contact (%s)" %e.message
				session.flash=" error while adding contact (%s)" %e.message
			else:
				# redirect to the home page
				redirect('contacts')
				pass
			pass

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_edit():
	return locals()


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$-- AJAX request --#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contact_selector():
	if not request.vars.company: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lCompanyList = server.ajax_contact_list(request.vars.company)
			pass
		except Exception as e:
			return 'Error %s' %e
		else:
			return DIV(*[DIV (k[1],
					 data={'id': "%s" % k[0]},
                     _onclick="set_company_value(this)",
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in lCompanyList.items() ] )
			pass
		pass

#Function to get the details of particular contact id
def contact_details():
	if not request.vars.contactId: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lCompantDetails = server.ajax_company_details(request.vars.contactId)
			pass
		except Exception as e:
			return 'Error %s' %e
		else:
			return "setValue(%s);" % json.dumps(lCompantDetails) 
			pass
		pass
	pass
