import _pickle as cPickle
import xmlrpc.client as xmlrpclib # import the rpc file
import json as json # JSON library
import ssl
import filters
context = ssl.SSLContext()
link=str(request.env.wsgi_url_scheme)+"://"+str(request.env.http_host)	

# it will contain all the views and the api call related to the crm app
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def session_check():
	if session.active==1:
		if db(db.general_session.id== session.session_id).select(db.general_session.is_active)[0].is_active == 1:
			return True
			
		else:		# have to destroy the local session also
			session.session_id=0
			session.company_id=''
			session.username=''
			session.name=''
			session.user_id=''
			session.login_time= ''
			session.user_type=''
			session.active=0
			return False
	else:
		return False

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CRM--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def crm():
	if session_check():
		return locals()
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--LEADS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads():
	# this function is responsible for the main leads dahboard
	# by default it will contain 10 leads per page
	
	if session_check():
		server = xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
		

		data=[]
		lFilterFlag=0
		lFilterData={}
		lFilterOutput={}
		if request.vars.lFilterFlag:
			# check the filter flag
			lFilterFlag=int( request.vars.lFilterFlag)
			lFilterOutput=eval(request.vars.lFilterOutput)
			pass
		lLeadsList=[]
		lFilterData={
					'lFilterOutput':lFilterOutput,
					'company_id':session.company_id
				}

		if lFilterFlag==0: 		# no filter is applied 
			try:
				lLeadsList= server.get_leads(session.company_id)		# get the data from the api
			except Exception as e:
				session.message=str(lLeadsList) + str(e)
		elif lFilterFlag==1: 	# filter is applied and have to fetch the data from different function
			try:
				
				# lLeadsList= server.get_leads(session.company_id)		# get the data from the api
				lLeadsList= server.get_leads_with_filter(dict(lFilterData))		# get the data from the api
			except Exception as e:
				session.message=str(lLeadsList) + str(e)

		return dict(data=lLeadsList['data'],filter_field=lLeadsList['filter_field'],data_flag=lLeadsList['data_flag'],lFilterData=lFilterData)

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
		
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def delete_lead(lead_key_id):
		leadserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
		lReturnData=leadserver.lead_delete(lead_key_id)	

		if lReturnData=='done':
			return 'done'
		else:
			session.flash='data not deleted'
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_add():
	if session_check():
		done=0
	#------------------------------------------------- session is active, make the connection to api
		leadserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
		contactserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Contacts','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the ERP api server of contact
		companyserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the ERP api server of company
		contactCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		
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
			name=key
			if contact_form_fields[key][0]:
				widget=eval(contact_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if contact_form_fields[key][1]:
				requires=eval(contact_form_fields[key][1])

				# if 'IS_IN_SET' in contact_form_fields[key][1]:
				# 	name= str(key)+'*'
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(name,widget=widget, requires=requires))
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
			if 'text' in leads_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			
			if 'IS_IN_SET' in leads_form_fields[key][1] or 'IS_NOT_EMPTY' in leads_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass
			leads_form_fields[key]=s						
			exec(place)
			exec(require)


	#-------------------------------------------------
		for key in contact_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in contact_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass

			if 'IS_IN_SET' in contact_form_fields[key][1] or 'IS_NOT_EMPTY' in contact_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass

			contact_form_fields[key]=s						
			exec(place)
			exec(require)
	#-------------------------------------------------
		for key in company_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in company_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			if 'IS_IN_SET' in company_form_fields[key][1] or 'IS_NOT_EMPTY' in company_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass

			company_form_fields[key]=s			
			exec(place)
			exec(require)
	#------------------------------------------------- if the form is accepted

		if lForm.process().accepted:
				company_key_id=int(request.vars.company_key_id)
				contact_key_id=int(request.vars.contact_key_id)
				#------------------------------------------------- contact and company is already in the db and we have the key ids of them
				if company_key_id != 0 and contact_key_id !=0: # only new leads
					
					for key in leads_form_fields.keys(): # update the entered data
						leads_form_fields[key]=eval('lForm.vars.'+key)

					leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
					leads_form_fields['name']=session.name
					leads_form_fields['user_id']=session.user_id
					leads_form_fields['company_id']=session.company_id
					leads_form_fields['session_id']=session.session_id

					try:    
					
						lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
						session.message+= str(lResponseDict['msg'])							

					except Exception as e:
						session.message=" error while adding lead details (%s)" %e
						session.flash=" error while adding lead details (%s)" %e
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
						lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
						contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 
						
						lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server

						contact_key_id= lResponseDict['lKeyId']
						
						# session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:

						for key in leads_form_fields.keys(): # update the entered data
							leads_form_fields[key]=eval('lForm.vars.'+key)

						leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
						leads_form_fields['name']=session.name
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
						
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							# session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding leads details (%s)" %e
							session.flash=" error while adding leads details (%s)" %e
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
						lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
						company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
						
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
							lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
							contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 
							
							lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server
							
							contact_key_id= lResponseDict['lKeyId']
							# session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							# session.message=str(lResponseDict['msg'])
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:

							for key in leads_form_fields.keys(): # update the entered data
								leads_form_fields[key]=eval('lForm.vars.'+key)

							leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
							leads_form_fields['name']=session.name
							leads_form_fields['user_id']=session.user_id
							leads_form_fields['company_id']=session.company_id
							leads_form_fields['session_id']=session.session_id

							try:    
							
								lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
								# session.message+= str(lResponseDict['msg'])							

							except Exception as e:
								session.message=" error while adding leads details (%s)" %e
								session.flash=" error while adding leads details (%s)" %e
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
							lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
							company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
							
							lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
							company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
							# session.message+= str(lResponseDict['msg'])

						except Exception as e:
							session.message+=" error while adding company details (%s)" %e 
							session.flash=" error while adding company details (%s)" %e
										
						else:	# now for the contact
							
							contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
							contact_form_fields['company_key_id']=company_key_id		# add the extra data
							contact_form_fields['user_id']=session.user_id
							contact_form_fields['company_id']=session.company_id

							try:    
								lResponseDict= contactserver.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server
								lResponseCRMDict= contactCRMServer.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the CRM server
								
								# session.message+= str(lResponseDict['msg'])
								
							except Exception as e:
								session.message+=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:

								for key in leads_form_fields.keys(): # update the entered data
									leads_form_fields[key]=eval('lForm.vars.'+key)

								leads_form_fields['contact_key_id']=contact_key_id		# add the extra data
								leads_form_fields['name']=session.name
								leads_form_fields['user_id']=session.user_id
								leads_form_fields['company_id']=session.company_id
								leads_form_fields['session_id']=session.session_id

								try:    
								
									lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
									# session.message+= str(lResponseDict['msg'])							

								except Exception as e:
									session.message=" error while adding leads details (%s)" %e
									session.flash=" error while adding leads details (%s)" %e
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
						leads_form_fields['name']=session.name
						leads_form_fields['user_id']=session.user_id
						leads_form_fields['company_id']=session.company_id
						leads_form_fields['session_id']=session.session_id

						try:    
							lResponseDict= leadserver.add_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
							# session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding leads details (%s)" %e
							session.flash=" error while adding leads details (%s)" %e
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
	# this is the func to only load the update page for the 1st time remaining will be done by ajax
	done=0 		# a flag to represent the succes
	# check the user is loged in or not
	if session_check():
		if len(request.args)>0:
			leadserver = xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
			lData={} # A dict to store the response of the server

				# session_details={'comapny_id':session.company_id,
	   #                 'user_id':session.user_id,
	   #                 'lead_key_id':request.args[0],

	   #                 }

			# take the leads key id from the page we have been redirected to get the data
			lRequestData={
				'lead_key_id':request.args[0],
				'user_id': session.user_id,
				'company_id':session.company_id
			}

			# try to fetch the required data from the api
			try:
				lData = leadserver.fetch_lead_basic_details(lRequestData)
			except Exception as e:
				session.message=" error in geting the leads update %s" %e
			else:
				done=1
				pass

			if done==1:
				return dict(data=lData, lead_key_id=lRequestData['lead_key_id'],session_details=lRequestData)
			else:
				session.message=' Envalid lead selected '

		else:
			redirect(URL('leads'))
			session.flash="select a lead to continue"


	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_edit():
	# this page is only to edit the leads details 
	# if the user wants to edit the contact details he will be redirected to that page from leads update page
	if session_check():
		if len(request.args)>0:
			done=0
			lead_key_id= request.args[0]
			# lead_key_id= 16

			#------------------------------------------------- session is active, make the connection to api		
			leadserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
			
			leads_form_fields=leadserver.leads_edit_ff(lead_key_id)			# ask for the list of the field to make the form and store it into a dict
			
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

				fields.append(Field(key,widget=widget, requires=requires, default=leads_form_fields[key][2]))


		
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
				if 'text' in leads_form_fields[key][0]:
					place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
					pass
				else:
					place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
					pass
				#place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
				leads_form_fields[key]=s						
				exec(place)

			lForm.custom.widget.lead_status['_required']=''
			lForm.custom.widget.lead_source['_required']=''
			lForm.custom.widget.lead_owner['_required']=''



			if lForm.process().accepted:
				
				session.message=''					
				for key in leads_form_fields.keys(): # update the entered data
					leads_form_fields[key]=eval('lForm.vars.'+key)
				
				leads_form_fields['lead_key_id']=lead_key_id		# add the extra data, take the lead id to specify the update
				leads_form_fields['name']=session.name
				leads_form_fields['user_id']=session.user_id
				leads_form_fields['session_id']=session.session_id
				leads_form_fields['company_id']=session.session_id

				try:    
					lResponseDict= leadserver.edit_leads(dict(data=leads_form_fields)) 		# send the dictioinary to the server
					session.message+= str(lResponseDict['msg'])							

				except Exception as e:
					session.message=" error while editing leads details (%s)" %e
					session.flash=" error while editing leads details (%s)" %e
				else:
					done=1
					pass
				if done==1:
					redirect(URL('leads_update',args=[lead_key_id]))
				pass
			return dict(form=lForm,leads_form_fields=leads_form_fields)

		else:
			redirect(URL('leads'))
			session.flash="select a lead to edit"

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CONTACTS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts():
	# this function is responcible for the main contact dahboard
	# by default it will contain 10 contact per page
	
	if session_check():

		server=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact

		data=[]
		lFilterFlag=0
		lFilterData={}
		lFilterOutput={}
		if request.vars.lFilterFlag:
			# check the filter flag
			lFilterFlag=int( request.vars.lFilterFlag)
			lFilterOutput=eval(request.vars.lFilterOutput)
			pass
		lContactsList=[]
		lFilterData={
					'lFilterOutput':lFilterOutput,
					'company_id':session.company_id
				}

		if lFilterFlag==0: 		# no filter is applied 
			try:
				lContactsList= server.get_contact(session.company_id)		# get the data from the api
			except Exception as e:
				session.message=str(lContactsList) + str(e)
				return e
		elif lFilterFlag==1: 	# filter is applied and have to fetch the data from different function
			try:
				
				# lContactsList= server.get_contact(session.company_id)		# get the data from the api
				lContactsList= server.get_contacts_with_filter(dict(lFilterData))		# get the data from the api
				pass
			except Exception as e:
				session.message=str(lContactsList) + str(e)
				return e
		# return locals()
		return dict(data=lContactsList['data'],data_flag=lContactsList['data_flag'],filter_field=lContactsList['filter_field'],lFilterData=lFilterData)

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_add():
	if session_check():
		done=0
	#------------------------------------------------- session is active, make the connection to api		
		contactserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Contacts','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		contactCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		
		contact_form_fields=contactserver.contact_add_ff()		
		company_form_fields=companyserver.company_add_ff()		

		fields=[] 		# a simple list to store the form fields
	
	
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
	
	#-------------------------------------------------
		for key in contact_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in contact_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
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
			if 'text' in company_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			company_form_fields[key]=s			
			exec(place)
	

		lForm.custom.widget.company_name['_required']=''
		lForm.custom.widget.company_name['_required']=''
		lForm.custom.widget.first_name['_required']=''
		lForm.custom.widget.type_of_contact['_required']=''


	#------------------------------------------------- if the form is accepted
		if lForm.process().accepted:
				company_key_id=int(request.vars.company_key_id)
	# 			contact_key_id=int(request.vars.contact_key_id)
	

	# #------------------------------------------------- have the company key id and new data in contact 

				if company_key_id != 0: # contant 
					
					session.message=''
					for key in contact_form_fields.keys(): # update the entered data
						contact_form_fields[key]=eval('lForm.vars.'+key)
					
					contact_form_fields['company_key_id']=company_key_id		# add the extra data
					contact_form_fields['user_id']=session.user_id
					contact_form_fields['company_id']=session.company_id
					contact_form_fields['session_id']=session.session_id

					try:    
						lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
						contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 
						
						lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server
						
						contact_key_id= lResponseDict['lKeyId']
						
						session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:
						done=1
						pass

						
					session.flash='condition 2'
					pass

	#------------------------------------------------- company is not selected from suggetions
				
				elif company_key_id==0 : 
					 
					if len(lForm.vars.company_name)>0: 	# have given the company data also

						session.message=""
						
						for key in company_form_fields.keys(): # update the entered data
							company_form_fields[key]=str(eval('lForm.vars.'+key))
						
						company_form_fields['user_id']=session.user_id
						company_form_fields['company_id']=session.company_id
						company_form_fields['session_id']=session.session_id
						lResponseDict={}
						
						try:    						
							lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
							company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
							
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
								lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
								contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 
								
								lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server
								
								contact_key_id= lResponseDict['lKeyId']
								
								session.message+= str(lResponseDict['msg'])
								
							except Exception as e:
								session.message+=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:
								done=1
								pass
								
							pass

						session.flash='condition 41'
					

					else: 		# donot have the comapny data only the persion details
						
						session.message=''
						for key in contact_form_fields.keys(): # update the entered data
							contact_form_fields[key]=eval('lForm.vars.'+key)
						
						contact_form_fields['company_key_id']=0		# add the extra data
						contact_form_fields['user_id']=session.user_id
						contact_form_fields['company_id']=session.company_id
						contact_form_fields['session_id']=session.session_id

						try:    
							lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
							contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 

							lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
							contact_key_id= lResponseDict['lKeyId']
							
							session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass

						session.flash='condition 42'						
						pass
					
					
				if done ==1:
					redirect(URL('contacts'))
					pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm,contact_form_fields=contact_form_fields,company_form_fields=company_form_fields)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_edit():
	if session_check():
		done=0
	#------------------------------------------------- session is active, make the connection to api		
		contactserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		
		
		# in this we have to provide the contact key id and get the respective company key id for company details
		# contact_key_id=request.vars.company_key_id 		# uncomment to connet to other page
		contact_key_id=request.args[0]
		contact_form_fields=contactserver.contact_edit_ff(contact_key_id)		

		company_key_id=contact_form_fields['company_key_id']
		company_form_fields=companyserver.company_edit_ff(company_key_id)		

		contact_form_fields = contact_form_fields['field_names']

		fields=[] 		# a simple list to store the form fields
	
	
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
			fields.append(Field(key,widget=widget, requires=requires, default=company_form_fields[key][2]))

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
			fields.append(Field(key,widget=widget, requires=requires, default=contact_form_fields[key][2]))
	#------------------------------------------------- make the sql form using the pointer to the list of fields

		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory
	
	#-------------------------------------------------
		for key in contact_form_fields.keys():
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in contact_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			#place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
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
			if 'text' in company_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			else:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			#place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
			company_form_fields[key]=s			
			exec(place)
	
	#------------------------------------------------- if the form is accepted
		if lForm.process().accepted:

				if int(request.vars.company_key_id) !=0:
					company_key_id=int(request.vars.company_key_id)
		
	# #------------------------------------------------- have the company key id and new data in contact 

				if company_key_id != 0: # contant 
					
					# session.message=''
					for key in contact_form_fields.keys(): # update the entered data
						contact_form_fields[key]=eval('lForm.vars.'+key)
					
					contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
					contact_form_fields['company_key_id']=company_key_id	
					contact_form_fields['user_id']=session.user_id
					contact_form_fields['session_id']=session.session_id
					contact_form_fields['company_id']=session.company_id

					try:    
						lResponseDict= contactserver.edit_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
						
						# contact_key_id= lResponseDict['lKeyId']
						
						# session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
					else:
						done=1
						pass
						
					session.flash='condition 2'
					pass

	# #------------------------------------------------- company is not selected from suggetions
				
				elif company_key_id==0 : 
					 # session.message+='2'
					if len(lForm.vars.company_name)>0: 	# have given the company data also

						# session.message=""
						
						for key in company_form_fields.keys(): # update the entered data
							company_form_fields[key]=str(eval('lForm.vars.'+key))
						
						company_form_fields['user_id']=session.user_id
						company_form_fields['company_id']=session.company_id
						company_form_fields['session_id']=session.session_id
						
						lResponseDict={}
						
						try:    						
							lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
							company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
							
							lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
							company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
							session.message+= str(lResponseDict['msg'])

						except Exception as e:
							session.message+=" error while adding company details (%s)" %e 
							session.flash=" error while adding company details (%s)" %e
										
						else:	# now for the contact
							
							for key in contact_form_fields.keys(): # update the entered data
								contact_form_fields[key]=eval('lForm.vars.'+key)
							
							contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
							contact_form_fields['company_key_id']=company_key_id		
							contact_form_fields['user_id']=session.user_id
							contact_form_fields['session_id']=session.session_id
							contact_form_fields['company_id']=session.company_id

							try:    
								lResponseDict= contactserver.edit_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
																
								session.message+= str(lResponseDict['msg'])
								
							except Exception as e:
								session.message+=" error while adding contact details (%s)" %e
								session.flash=" error while adding conatact details (%s)" %e
							else:
								done=1
								pass
								
							pass

						session.flash='condition 41'
					

					else: 		# donot have the comapny data only the persion details
						# session.message+='2'
						session.message=''
						for key in contact_form_fields.keys(): # update the entered data
							contact_form_fields[key]=eval('lForm.vars.'+key)
						
						contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
						contact_form_fields['company_key_id']=0		
						contact_form_fields['user_id']=session.user_id
						contact_form_fields['session_id']=session.session_id
						contact_form_fields['company_id']=session.company_id
						
						try:    
							lResponseDict= contactserver.edit_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
							
							
							# contact_key_id= lResponseDict['lKeyId']
							
							# session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:
							done=1
							pass

						session.message='condition 42'						
						pass
					
					
				if done ==1:
					redirect(URL('contacts_view',args=[contact_key_id]))
					pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm,contact_form_fields=contact_form_fields,company_form_fields=company_form_fields)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_view():
	# this is the func to only load the update page for the 1st time remaining will be done by ajax
	done=0
	# check the user is loged in or not
	if session_check():

		if len(request.args)>0:
			
			leadserver = xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
			
			lData={} # A dict to store the response of the server

			# take the leads key id from the page we have been redirected to get the data
			lRequestData={
				'contact_key_id':request.args[0],
				'user_id': session.user_id,
				'company_id':session.company_id
			}

			# try to fetch the required data from the api
			try:
				lData = leadserver.fetch_contact_basic_details(lRequestData)
			except Exception as e:
				session.message=" error in geting the leads update %s" %e
			else:
				session.message=""
				done=1
				pass


			if done==1:
				return dict(data=lData, contact_key_id=lRequestData['contact_key_id'])

		else:
			redirect(URL('contacts'))
			session.flash="select a contact to continue"

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$-- AJAX request --$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#AJAX request to get the company details on page "leads_add.html"
def company_selector():
	if not request.vars.company_name: return ''
	try:
		server=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		pass
	except Exception as e:
		return DIV('Either you have lost connectivity with CRM application or it is not yet installed')
	else:
		try:
			lCompanyList = server.ajax_company_list(request.vars.company_name,session.company_id)			#,session.company_id

			pass
		except Exception as e:
			return 'Error %s' %e
		else:
			return DIV(*[DIV (k[1],
					 data={'id': "%s" % k[0]},
                     _onclick="set_company_value(this)",
                     _onmouseover="this.style.backgroundColor='lightblue'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in lCompanyList.items() ] )
			pass
		pass


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#Function to get the details of particular contact id
def company_details():
	if not request.vars.contactId: return ''
	try:
		server=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
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


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#AJAX request to get the contact details on page "leads_add.html"
def contact_selector():
	if not request.vars.first_name: return ''
	try:
		server=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
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
							_onmouseover="this.style.backgroundColor='lightblue'",
                     		_onmouseout="this.style.backgroundColor='white'",
                     		_style="cursor: pointer;"
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


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Function to get the contact details on page "leads-add.html"
def contact_details():
	if not request.vars.contact_key_id: return ''
	try:
		server=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
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

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ajax for lead update $$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ 
def update_leads_ajax():
	session.message=" "
	# store all the required data into a single dict and send it to the api
	done=0

	lRequestData={
	'request_type':request.vars.request_type,		# get and add
	'lead_key_id':request.vars.leads_key_id,
	'user_id': session.user_id,				##############
	'company_id':session.company_id,		##############
	'update_head': request.vars.update_head,
	'update_data': request.vars.update_data,
	'lead_status_id':1,					#request.vars.status_id,
	'session_id':session.session_id,		##############
	'lead_update_id':request.vars.lead_update_id
	}
	# lRequestData={
	# 'request_type': 'get',		# get and add
	# 'lead_key_id': '16',
	# 'user_id': 2,				##############
	# 'company_id':25,		##############
	# 'update_head': 'notes',
	# 'update_data': 'yes',
	# 'lead_status_id':1,					#request.vars.status_id,
	# 'session_id':0		##############
	# #'lead_update_id':request.vars.lead_update_id
	# }

	if lRequestData['request_type']=='get': 		# we just have to send the table
		
		# make the connection to the desired server
		leadserver = xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead


		lData={}		# a dict to store the respose data
		try:		# try to get the data
			lData = leadserver.fetch_lead_update_details(lRequestData)			#	dict(data=lRequestData)
			pass
		except Exception as e:
			session.message=" error in geting the leads update %s" %e
			 
		else:
			for key in lData.keys():
				user_id=lData[key]['db_entered_by']
				name=db(db.general_user.id==user_id).select(db.general_user.first_name,db.general_user.last_name)
				lData[key]['db_entered_by']=str(name[0].first_name).title()+" "+str(name[0].last_name).title()
	
			done=1
			pass

	elif lRequestData['request_type']=='add': 		# we have to add the data into the db and send the table
		# make the connection to the desired server
		leadserver = xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead


		lData={}		# a dict to store the respose data

		try:		# try to get the data
			lData = leadserver.add_lead_update_details(lRequestData)
		except Exception as e:
			session.message=" error in geting the leads update %s" %e
		else:
			for key in lData.keys():
				user_id=lData[key]['db_entered_by']
				name=db(db.general_user.id==user_id).select(db.general_user.first_name,db.general_user.last_name)
				lData[key]['db_entered_by']=str(name[0].first_name).title()+" "+str(name[0].last_name).title()
	
			done=1
			pass


	# elif lRequestData['request_type']=='edit':		# we have to update the data
	# 	# make the connection to the desired server
	# 	leadserver = xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/Leads/call/xmlrpc',allow_none=True)	# make the connection to the api server of lead

	# 	lData={}		# a dict to store the respose data

	# 	try:		# try to get the data
	# 		lData = leadserver.edit_lead_update_details(lRequestData)
	# 	except Exception as e:
	# 		session.message=" error in geting the leads update %s" %e
	# 	else:
	# 		pass

	if done==1:
		return json.dumps(lData)
	

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def lead_status_ajax():
	

	# lRequestData={
	# 'request_type':request.vars.request_type,		# get and add
	# 'lead_key_id':request.vars.leads_key_id,
	# 'user_id': session.user_id,
	# 'session_id':session.session_id,
	# 'lead_status_master_id':request.vars.lead_status_master_id,
	# 'company_id':session.company_id,
	# 'status_id':request.vars.status_id,
	# 'response':1
	# }

	lRequestData={
	'request_type': 'get',		# get and add
	'lead_key_id': '16',
	'user_id': 2,				##############
	'company_id':25,		##############
	'update_head': 'notes',
	'update_data': 'yes',
	'lead_status_id':1,					#request.vars.status_id,
	'session_id':0,		##############
	'respose':1
	}

	if lRequestData['request_type']=='get': 		# we just have to send the table
		# make the connection to the desired server
		leadserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
		
		lData={}		# a dict to store the respose data

		try:			# try to get the data
			lData = leadserver.fetch_lead_status_details(lRequestData)
		except Exception as e:
			session.message=" error in geting the leads update %s" %e
		else:
			pass

	elif lRequestData['request_type']=='add': 		# we have to add the data into the db and send the table
		# make the connection to the desired server
		leadserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead
		
		lData={}		# a dict to store the respose data

		try:		# try to get the data
			lData = leadserver.add_lead_status_details(lRequestData)
		except Exception as e:
			session.message=" error in geting the leads update %s" %e
		else:
			pass


	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def datatable():
	data= dict(request.vars['data'])
	data_flag=request.vars['data_flag']
	if len(data)>0:
		lFields=data['0'].keys()
	else:
		lFields='No Data Available'
	lRedirectKey=request.vars['lRedirectKey'] or ' '
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def load_filter():
	filter_field=eval(request.vars['filter_field'])
	filter_value=eval(request.vars['filter_value'])
	# lForm=F.filter_form(dict(filter_field))
	fields=[]

	field_value={}
	for key in filter_value.keys():
		if len(filter_value[key])>0:
			for data in filter_value[key]:
				field_value[data.split('.')[0]]=[data.split('.')[1].split('(')[0],data.split('.')[1].split('(')[1].split('"')[1]]



	for category in list(filter_field.keys()):

		for key in sorted(filter_field[category].keys()):			# take key one by one in a sequence and make the field list
			
			fields.append(Field(key,'boolean'))



			if filter_field[category][key][0]: 	# we have a give field type
				

				if 'options' in filter_field[category][key][0]:		# it have a predeffind data set so have to give a data list
					lRequires1=eval('request.post_vars.'+key) 		# local variable to strore the output of the eval
					lConditionString=filter_field[category][key][1]
					
					# make a new is in set list with multiple= true
					if '{' in lConditionString:
						lConditionString = lConditionString.split('{')[1].split('}')[0]
						lConditionString='IS_IN_SET({'+lConditionString+'},multiple=True)'
					elif '[' in lConditionString:
						lConditionString = lConditionString.split('[')[1].split(']')[0]
						lConditionString='IS_IN_SET(['+lConditionString+'],multiple=True)'
					
					fields.append(Field(key+'_option',widget=eval(filter_field[category][key][0]), requires=eval(lConditionString)))
					fields.append(Field(key+'_option_data','hidden'))
					pass
				
				else: 		# for the rest of the data types in which user have entered the data
					if 'text' in filter_field[category][key][0]:
						filter_field[category][key][0]='SQLFORM.widgets.string.widget'

					fields.append(Field(key+'_condition',widget=SQLFORM.widgets.options.widget,requires=IS_IN_SET({'startswith':'Starts With','endswith':'Ends With','contains':'Contains'},multiple=True),))
					fields.append(Field(key+'_condition_data',widget=eval(filter_field[category][key][0]), requires=IS_NOT_EMPTY() if eval('request.post_vars.'+key) else None ))
					pass
			

			else: # take the field type of string by default ,, not gona happen but for the precautions
				
					fields.append(Field(key+'_condition',widget=SQLFORM.widgets.options.widget,requires=IS_IN_SET({'startswith':'Starts With','endswith':'Ends With','contains':'Contains'},multiple=True)))
					fields.append(Field(key+'_condition_data',widget=eval(filter_field[category][key][0]), requires=IS_NOT_EMPTY() if eval('request.post_vars.'+key) else None ))
	


	lForm= SQLFORM.factory(*fields)

	# for key in field_value.keys():
	# 	lForm.element('option',_value='contains')['_selected']=''


	lFilterOutput={}		# a dict to store the final output of the filter and send it to the orignal page
	lList=[] 		# a local list to store the data while processing
		
	if lForm.process().accepted:
		# if the filters are acceptedconvert them accordingly
		for condition in filter_field.keys():
			for key in filter_field[condition].keys(): 		# select a perticular key for a condition like 
				if eval('lForm.vars.'+key):		 # if the check box was selected
					
					if eval('lForm.vars.'+key+'_condition'):
						lConditionString = eval('lForm.vars.'+key+'_condition')		# final output=> city.endswith('value')
						lValue=eval('lForm.vars.'+key+'_condition_data')
						lList.append(str(key)+'.'+str(lConditionString[0])+'("'+str(lValue)+'")')
					else :
						lConditionString = 'contains'	# final output=> city.endswith('value')
						lValue=eval('lForm.vars.'+key+'_option')
						lList.append(str(key)+'.'+str(lConditionString)+'("'+str(lValue[0])+'")')
					
					pass
				pass

			lFilterOutput[condition]=lList
			lList=[]
			pass

		# the data id succesfully converted and now have to make a dict and send it to the source page
		lFilterFlag=1		# 1 =true and  0= false
		redirect(URL(request.env.http_referer.split('/')[-3],request.env.http_referer.split('/')[-2],request.env.http_referer.split('/')[-1].split('?')[0],extension=False,vars={'lFilterFlag':lFilterFlag,'lFilterOutput':lFilterOutput}), client_side=True)
		pass
	form=lForm
	# return dict(form=lForm,filter_field=filter_field,filter_value=filter_value)
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--- Contacts and Company details storing for ERP----$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def add_erp_contact(lContactData):
	done=0
	
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	
	try:
		lKeyId=db.general_contact_field_key.insert(
				id=lContactData['data']['contact_key_id'],
				company_key_id=lContactData['data']['company_key_id'],
				company_id=lContactData['data']['company_id'] ,
				db_entry_time=lambda:datetime.now(),
				db_entered_by=lContactData['data']['user_id'],
				session_id=lContactData['data']['session_id']
			)
	
		lReturnDict['lKeyId']=int(lKeyId)
	
	except Exception as e:
		lReturnDict['msg']='error in adding contact key (%s)' %e
		return lReturnDict	
	
	else:
		rows=db(db.general_contact_field.field_name != None).select()
		for row in rows:
			if row.is_active== True:
				try:
					db.general_contact_field_value.insert(
						field_id=row.id ,
						contact_key_id=lKeyId ,
						field_value=lContactData['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
						db_entry_time=lambda:datetime.now(),
						db_entered_by=lContactData['data']['user_id'],
						company_id=lContactData['data']['company_id'],
						session_id=lContactData['data']['session_id']
						)
					pass
				except Exception as e:
					lReturnDict['msg']='error in adding contact data (%s)' %e
					return lReturnDict	
				else:
					done=1

	if done==1:
		lReturnDict['msg']=' contact done '
	return lReturnDict
	pass

def update_company_contact_key_id(data):
	done=0
	
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	
	try:
		db(db.general_contact_field_key.id==data['data']['contact_key_id']).update(
				company_key_id=data['data']['company_key_id'],
				db_updated_by=data['data']['user_id'] ,
				db_update_time=lambda:datetime.now()
			)
		
	except Exception as e:
		lReturnDict['msg']='error in adding contact key (%s)' %e
		return lReturnDict	

	else:
		done=1


	if done==1:
		lReturnDict['msg']=' contact updated '
	return lReturnDict
	pass

def add_contact_company_erp(data):
	done=0
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	try:
		lKeyId=db.general_contact_company_field_key.insert(
				id=data['data']['company_key_id'],
				company_id=data['data']['company_id'],
				db_entry_time=lambda:datetime.now(),
				db_entered_by=data['data']['user_id'],
				session_id=data['data']['session_id']
			)
		lReturnDict['lKeyId']=int(lKeyId)
	except Exception as e:
		lReturnDict['msg']='error in adding company key (%s)' %e
		return lReturnDict
	else:
		rows=db(db.crm_company_field.field_name).select()
		for row in rows:
			if row.is_active== True:
				try:
					db.general_contact_company_field_value.insert(
						field_id=row.id ,
						company_key_id=lKeyId ,
						field_value=data['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id'],
						company_id=data['data']['company_id'],
						session_id=data['data']['session_id']
						)
					pass
				except Exception as e:
					lReturnDict['msg']='error in adding company data (%s)' %e
					return lReturnDict
				else:
					done=1
		pass

	if done==1:
		lReturnDict['msg']="company done"
		return lReturnDict
	pass
