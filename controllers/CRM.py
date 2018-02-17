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

		server = xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)	# make the connection to the api server of lead
		
		data=[]
		lLimit={}
		lLimit['countTo']=10		# total number of fieds required, replace it with request.vars.* to make it dynamin
		lLimit['countFrom']=0		# no of the row to start from 
		lLimit['order']='~db.crm_lead_field_key.id' 	# the name of field to order on, string will be evaluated in the api
		
		lLeadsList=[]
		try:
			lLeadsList= server.get_leads(lLimit)		# get the data from the api

		except Exception as e:
			session.message=str(lLeadsList) + str(e)
		

		return dict(data=lLeadsList)
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_add():
	if session.active==1:
		done=0
#------------------------------------------------- session is active, make the connection to api		
		leadserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)	# make the connection to the api server of lead
		contactserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)	# make the connection to the api server of contact
		companyserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Company/call/xmlrpc',allow_none=True)	# make the connection to the api server of company
		
		leads_form_fields=leadserver.leads_add_ff()			# ask for the list of the field to make the form and store it into a dict
		contact_form_fields=contactserver.contact_add_ff()		
		company_form_fields=companyserver.company_add_ff()		

		fields=[] 		# a simple list to store the form fields
#------------------------------------------------- add the form fields of leads into the list
		for key in sorted(leads_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if leads_form_fields[key][0]:
				widget=eval(leads_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			
			if leads_form_fields[key][1]:
				requires=eval(leads_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(key,widget=widget, requires=requires))

#------------------------------------------------- now add the form fields of company form
		# # add the form fields of the company
		for key in sorted(company_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if company_form_fields[key][0]:
				widget=eval(company_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if company_form_fields[key][1]:
				requires=eval(company_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty
			fields.append(Field(key,widget=widget, requires=requires))

#------------------------------------------------- add the fields of contact form
		# add the form fields of the contacts
		for key in sorted(contact_form_fields.keys()):			# take key one by one in a sequence and make the field list
			
			if contact_form_fields[key][0]:
				widget=eval(contact_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if contact_form_fields[key][1]:
				requires=eval(contact_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(key,widget=widget, requires=requires))
#------------------------------------------------- make the sql form using the pointer to the list of fields

		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory
#------------------------------------------------- add the place holder using the same dictionary
		for key in leads_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			leads_form_fields[key]=s						
			exec(place)

#-------------------------------------------------
		for key in contact_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			contact_form_fields[key]=s						
			exec(place)
#-------------------------------------------------
		for key in company_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			company_form_fields[key]=s			
			exec(place)
#------------------------------------------------- if the form is accepted
		if lForm.process().accepted:
				company_key_id=int(request.vars.company_key_id)
				contact_key_id=int(request.vars.contact_key_id)
#------------------------------------------------- contact and company is already in the db and we have the key ids of them
				if company_key_id != 0 and contact_key_id !=0: # only new leads
					
					for key in leads_form_fields.keys(): # update the entered data
						leads_form_fields[key]=eval('lForm.vars.'+key)

					leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
					leads_form_fields['user_id']=session.user_id
					leads_form_fields['company_id']=session.company_id
					leads_form_fields['session_id']=session.session_id

					try:    
					
						lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
						session.message+= str(lResponseDict['msg'])							

					except Exception as e:
						session.message=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:
						done=1
						pass

					session.flash='condition 1'+" "+str(company_key_id) +" "+str(type(company_key_id))
					pass
#------------------------------------------------- have the company key id and new data in contact and its new lead

				elif company_key_id != 0 and contact_key_id ==0: # contant and leads
					session.message=''
					for key in contact_form_fields.keys(): # update the entered data
						contact_form_fields[key]=eval('lForm.vars.'+key)
					
					contact_form_fields['company_key_id']=company_key_id		# add the extra data
					contact_form_fields['user_id']=session.user_id
					contact_form_fields['company_id']=session.company_id
					contact_form_fields['session_id']=session.session_id

					try:    
						lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
						
						contact_key_id= lResponseDict['lKeyId']
						
						session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:

						for key in leads_form_fields.keys(): # update the entered data
							leads_form_fields[key]=eval('lForm.vars.'+key)

						leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
						
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass

						pass
					session.flash='condition 2'
					pass
#------------------------------------------------- whole data is new

				elif company_key_id == 0 and contact_key_id ==0: #	all
					
					session.message=""
					for key in company_form_fields.keys(): # update the entered data
						company_form_fields[key]=str(eval('lForm.vars.'+key))
					
					company_form_fields['user_id']=session.user_id
					company_form_fields['company_id']=session.company_id
					company_form_fields['session_id']=session.session_id
					lResponseDict={}
					
					try:    						
						lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
						
						company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
						session.message+= str(lResponseDict['msg'])

					except Exception as e:
						session.message+=" error while adding company details (%s)" %e 
						session.flash=" error while adding company details (%s)" %e
									
					else:	# now for the contact
						
						for key in contact_form_fields.keys(): # update the entered data
							contact_form_fields[key]=eval('lForm.vars.'+key)
						contact_form_fields['company_key_id']=company_key_id		# add the extra data
						contact_form_fields['user_id']=session.user_id
						contact_form_fields['company_id']=session.company_id
						contact_form_fields['session_id']=session.session_id

						try:    
							lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
							
							contact_key_id= lResponseDict['lKeyId']
							session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:

							for key in leads_form_fields.keys(): # update the entered data
								leads_form_fields[key]=eval('lForm.vars.'+key)

							leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
							leads_form_fields['user_id']=session.user_id
							leads_form_fields['company_id']=session.company_id
							leads_form_fields['session_id']=session.session_id

							try:    
							
								lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
								session.message+= str(lResponseDict['msg'])							

							except Exception as e:
								session.message=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:
								done=1
								pass

							pass

						pass
					session.flash='condition 3'
					pass

#------------------------------------------------- contact was present but have to add the company and update the details of the contact
				
				elif company_key_id==0 and contact_key_id !=0: 
					 
					if len(lForm.vars.company_name)>0:

						# have to add the company and update the company_key_id
						session.message=""
						
						for key in company_form_fields.keys(): # update the entered data
							company_form_fields[key]=str(eval('lForm.vars.'+key))
						
						company_form_fields['user_id']=session.user_id
						company_form_fields['company_id']=session.company_id
						company_form_fields['session_id']=session.session_id
						lResponseDict={}
						
						try:    						
							lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
							
							company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
							session.message+= str(lResponseDict['msg'])

						except Exception as e:
							session.message+=" error while adding company details (%s)" %e 
							session.flash=" error while adding company details (%s)" %e
										
						else:	# now for the contact
							
							contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
							contact_form_fields['company_key_id']=company_key_id		# add the extra data
							contact_form_fields['user_id']=session.user_id
							contact_form_fields['company_id']=session.company_id

							try:    
								lResponseDict= contactserver.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the server
								
								session.message+= str(lResponseDict['msg'])
								
							except Exception as e:
								session.message+=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:

								for key in leads_form_fields.keys(): # update the entered data
									leads_form_fields[key]=eval('lForm.vars.'+key)

								leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
								leads_form_fields['user_id']=session.user_id
								leads_form_fields['company_id']=session.company_id
								leads_form_fields['session_id']=session.session_id

								try:    
								
									lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
									session.message+= str(lResponseDict['msg'])							

								except Exception as e:
									session.message=" error while adding contact details (%s)" %e
									session.flash=" error while adding conatact details (%s)" %e
								else:
									done=1
									pass

								pass

							pass


						session.flash='condition 41'
					
					else:
						# only leads
						for key in leads_form_fields.keys(): # update the entered data
							leads_form_fields[key]=eval('lForm.vars.'+key)

						leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
						
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass


							session.flash='condition 42'						
						pass
					
					
				if done ==1:
					redirect(URL('leads'))
					pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm,leads_form_fields=leads_form_fields,contact_form_fields=contact_form_fields,company_form_fields=company_form_fields)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_update():
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_edit():
	if session.active==1:
		done=0
	#------------------------------------------------- session is active, make the connection to api		
		leadserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)	# make the connection to the api server of lead
		contactserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)	# make the connection to the api server of contact
		companyserver=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Company/call/xmlrpc',allow_none=True)	# make the connection to the api server of company
		
		leads_form_fields=leadserver.leads_edit_ff()			# ask for the list of the field to make the form and store it into a dict
		contact_form_fields=contactserver.contact_add_ff()		
		company_form_fields=companyserver.company_add_ff()		

		fields=[] 		# a simple list to store the form fields
	#------------------------------------------------- add the form fields of leads into the list
		for key in sorted(leads_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if leads_form_fields[key][0]:
				widget=eval(leads_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			
			if leads_form_fields[key][1]:
				requires=eval(leads_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty	

			if leads_form_fields[key][2]:	
				fields.append(Field(key,widget=widget, requires=requires, defaul=leads_form_fields[key][2]))
			else:
				fields.append(Field(key,widget=widget, requires=requires))

	#------------------------------------------------- now add the form fields of company form
		# add the form fields of the company
		for key in sorted(company_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if company_form_fields[key][0]:
				widget=eval(company_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if company_form_fields[key][1]:
				requires=eval(company_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty
			fields.append(Field(key,widget=widget, requires=requires))

	#------------------------------------------------- add the fields of contact form
		# add the form fields of the contacts
		for key in sorted(contact_form_fields.keys()):			# take key one by one in a sequence and make the field list
			
			if contact_form_fields[key][0]:
				widget=eval(contact_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if contact_form_fields[key][1]:
				requires=eval(contact_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(key,widget=widget, requires=requires))
	#------------------------------------------------- make the sql form using the pointer to the list of fields

		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory
	#------------------------------------------------- add the place holder using the same dictionary
		for key in leads_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			leads_form_fields[key]=s						
			exec(place)

	#-------------------------------------------------
		for key in contact_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			contact_form_fields[key]=s						
			exec(place)
	#-------------------------------------------------
		for key in company_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			company_form_fields[key]=s			
			exec(place)
	#------------------------------------------------- if the form is accepted
		if lForm.process().accepted:
				company_key_id=int(request.vars.company_key_id)
				contact_key_id=int(request.vars.contact_key_id)
	#------------------------------------------------- contact and company is already in the db and we have the key ids of them
				if company_key_id != 0 and contact_key_id !=0: # only new leads
					
					for key in leads_form_fields.keys(): # update the entered data
						leads_form_fields[key]=eval('lForm.vars.'+key)

					leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
					leads_form_fields['user_id']=session.user_id
					leads_form_fields['company_id']=session.company_id
					leads_form_fields['session_id']=session.session_id

					try:    
					
						lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
						session.message+= str(lResponseDict['msg'])							

					except Exception as e:
						session.message=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:
						done=1
						pass

					session.flash='condition 1'+" "+str(company_key_id) +" "+str(type(company_key_id))
					pass
	#------------------------------------------------- have the company key id and new data in contact and its new lead

				elif company_key_id != 0 and contact_key_id ==0: # contant and leads
					session.message=''
					for key in contact_form_fields.keys(): # update the entered data
						contact_form_fields[key]=eval('lForm.vars.'+key)
					
					contact_form_fields['company_key_id']=company_key_id		# add the extra data
					contact_form_fields['user_id']=session.user_id
					contact_form_fields['company_id']=session.company_id
					contact_form_fields['session_id']=session.session_id

					try:    
						lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
						
						contact_key_id= lResponseDict['lKeyId']
						
						session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:

						for key in leads_form_fields.keys(): # update the entered data
							leads_form_fields[key]=eval('lForm.vars.'+key)

						leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
						
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass

						pass
					session.flash='condition 2'
					pass
	#------------------------------------------------- whole data is new

				elif company_key_id == 0 and contact_key_id ==0: #	all
					
					session.message=""
					for key in company_form_fields.keys(): # update the entered data
						company_form_fields[key]=str(eval('lForm.vars.'+key))
					
					company_form_fields['user_id']=session.user_id
					company_form_fields['company_id']=session.company_id
					company_form_fields['session_id']=session.session_id
					lResponseDict={}
					
					try:    						
						lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
						
						company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
						session.message+= str(lResponseDict['msg'])

					except Exception as e:
						session.message+=" error while adding company details (%s)" %e 
						session.flash=" error while adding company details (%s)" %e
									
					else:	# now for the contact
						
						for key in contact_form_fields.keys(): # update the entered data
							contact_form_fields[key]=eval('lForm.vars.'+key)
						contact_form_fields['company_key_id']=company_key_id		# add the extra data
						contact_form_fields['user_id']=session.user_id
						contact_form_fields['company_id']=session.company_id
						contact_form_fields['session_id']=session.session_id

						try:    
							lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
							
							contact_key_id= lResponseDict['lKeyId']
							session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:

							for key in leads_form_fields.keys(): # update the entered data
								leads_form_fields[key]=eval('lForm.vars.'+key)

							leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
							leads_form_fields['user_id']=session.user_id
							leads_form_fields['company_id']=session.company_id
							leads_form_fields['session_id']=session.session_id

							try:    
							
								lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
								session.message+= str(lResponseDict['msg'])							

							except Exception as e:
								session.message=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:
								done=1
								pass

							pass

						pass
					session.flash='condition 3'
					pass

	#------------------------------------------------- contact was present but have to add the company and update the details of the contact
				
				elif company_key_id==0 and contact_key_id !=0: 
					 
					if len(lForm.vars.company_name)>0:

						# have to add the company and update the company_key_id
						session.message=""
						
						for key in company_form_fields.keys(): # update the entered data
							company_form_fields[key]=str(eval('lForm.vars.'+key))
						
						company_form_fields['user_id']=session.user_id
						company_form_fields['company_id']=session.company_id
						company_form_fields['session_id']=session.session_id
						lResponseDict={}
						
						try:    						
							lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
							
							company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
							session.message+= str(lResponseDict['msg'])

						except Exception as e:
							session.message+=" error while adding company details (%s)" %e 
							session.flash=" error while adding company details (%s)" %e
										
						else:	# now for the contact
							
							contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
							contact_form_fields['company_key_id']=company_key_id		# add the extra data
							contact_form_fields['user_id']=session.user_id
							contact_form_fields['company_id']=session.company_id

							try:    
								lResponseDict= contactserver.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the server
								
								session.message+= str(lResponseDict['msg'])
								
							except Exception as e:
								session.message+=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:

								for key in leads_form_fields.keys(): # update the entered data
									leads_form_fields[key]=eval('lForm.vars.'+key)

								leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
								leads_form_fields['user_id']=session.user_id
								leads_form_fields['company_id']=session.company_id
								leads_form_fields['session_id']=session.session_id

								try:    
								
									lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
									session.message+= str(lResponseDict['msg'])							

								except Exception as e:
									session.message=" error while adding contact details (%s)" %e
									session.flash=" error while adding conatact details (%s)" %e
								else:
									done=1
									pass

								pass

							pass


						session.flash='condition 41'
					
					else:
						# only leads
						for key in leads_form_fields.keys(): # update the entered data
							leads_form_fields[key]=eval('lForm.vars.'+key)

						leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
						
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass


							session.flash='condition 42'						
						pass
					

				if done ==1:
					redirect(URL('leads'))
					pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm,leads_form_fields=leads_form_fields,contact_form_fields=contact_form_fields,company_form_fields=company_form_fields)


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
		
		data={}
		lContactList={}
		try:
			lContactList= server.get_contact(lLimit)		# get the data from the api
			data= lContactList
		except Exception as e:
			data=str(lContactList) + str(e)
		
		return dict(data=data)

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

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
				lResponseDict= server.add_contact(form_fields) 		# send the dictioinary to the server
				session.message= str(lResponseDict)
				session.flash= str(lResponseDict)
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
#AJAX request to get the company details on page "leads_add.html"
def company_selector():
	if not request.vars.company_name: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lCompanyList = server.ajax_company_list(request.vars.company_name,session.company_id)

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
def company_details():
	if not request.vars.contactId: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lCompanyDetails = server.ajax_company_details(request.vars.contactId)
			pass
		except Exception as e:
			return 'Error %s' %e
		else:
			return "setCompanyValue(%s);" % json.dumps(lCompanyDetails) 
			pass
		pass
	pass

#AJAX request to get the contact details on page "leads_add.html"
def contact_selector():
	if not request.vars.first_name: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		if request.vars.company_key_id == '0':
			# Company value is not entered
			try:
				lContactDetail = server.ajax_contact_list(request.vars.first_name,session.company_id)
				pass
			except Exception as e:
				return 'Error %s' %e
			else:
				return DIV(*[DIV(k['crm_contact_field_value']['field_value']+'-'+k['crm_company_field_value']['field_value'],
							data={'contact_id': "%s" % k['crm_contact_field_value']['contact_key_id'], 'company_id': "%s" % k['crm_contact_field_key']['company_key_id']},
							_onclick="set_contact_value(this)",
							_onmouseover="this.style.backgroundColor='yellow'",
                     		_onmouseout="this.style.backgroundColor='white'"
                     	) for k in lContactDetail])
				pass
			pass
		else:
			# Company value is entered
			try:
				lCompanyContactDetail = server.ajax_company_contact_list(request.vars.first_name,request.vars.company_key_id,session.company_id)
				pass
			except Exception as e:
				return 'Error %s' %e
			else:
				return DIV(*[DIV(
							k['crm_contact_field_value']['field_value']+'-'+k['crm_company_field_value']['field_value'],
							data={'contact_id': "%s" % k['crm_contact_field_value']['contact_key_id'], 'company_id': "%s" % k['crm_contact_field_key']['company_key_id']},
							_onclick="set_contact_value(this)",
							_onmouseover="this.style.backgroundColor='yellow'",
                     		_onmouseout="this.style.backgroundColor='white'"
						) for k in lCompanyContactDetail])
				pass
			pass
		pass
	pass

# Function to get the contact details on page "leads-add.html"
def contact_details():
	if not request.vars.contact_key_id: return ''
	try:
		server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Contact/call/xmlrpc',allow_none=True)
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lContactDetails = server.ajax_contact_details(request.vars.contact_key_id)
			pass
		except Exception as e:
			return 'Error %s' %e
		else:
			return "setContactValue(%s);" % json.dumps(lContactDetails) 
			pass
		pass
	pass