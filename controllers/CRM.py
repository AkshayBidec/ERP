# it will contain all the views and the api call related to the crm app
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CRM--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def crm():

	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--LEADS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


def leads():
	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_add():
 	import xmlrpclib # for xml rpc
 	# establish the cponnection with the server
	server=xmlrpclib.ServerProxy('http://127.0.0.1:8000/CRM/test/call/xmlrpc')

	if session.is_active==0:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	else:
		lForm= SQLFORM.factory(
	                         Field('company', requires=[IS_NOT_EMPTY('Enter company name')]),
	                         Field('lead_owner', requires=[IS_NOT_EMPTY('Enter lead_owner')]),
	                         Field('first_name', requires=[IS_NOT_EMPTY('Enter first_name')]),
	                         Field('last_name', requires=[IS_NOT_EMPTY('Enter last_name')]),
	                         Field('title', requires=[IS_NOT_EMPTY('Enter title')]),
	                         Field('email_id', requires=[IS_NOT_EMPTY('Enter email_id')]),
	                         Field('phone', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('fax', requires=[]),
	                         Field('mobile', requires=[]),
	                         Field('website', requires=[]),
	                         Field('lead_source', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('lead_status', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('street', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('city', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('state', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('pincode', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('country', requires=[IS_NOT_EMPTY('Enter data')]),
		                 	 Field('description', requires=[IS_NOT_EMPTY('Enter data')])
		                 )
		lForm.custom.widget.company.update(_placeholder='Company')
		lForm.custom.widget.lead_owner.update(_placeholder='Lead Owner')
		lForm.custom.widget.first_name.update(_placeholder='First Name')
		lForm.custom.widget.last_name.update(_placeholder='Last Name')
		lForm.custom.widget.title.update(_placeholder='Title')
		lForm.custom.widget.email_id.update(_placeholder='Email ID')
		lForm.custom.widget.phone.update(_placeholder='Phone')
		lForm.custom.widget.fax.update(_placeholder='Fax')
		lForm.custom.widget.mobile.update(_placeholder='Mobile')
		lForm.custom.widget.website.update(_placeholder='Website')
		lForm.custom.widget.lead_source.update(_placeholder='Lead Source')
		lForm.custom.widget.lead_status.update(_placeholder='Lead Status')
		lForm.custom.widget.street.update(_placeholder='Street')
		lForm.custom.widget.city.update(_placeholder='City')
		lForm.custom.widget.state.update(_placeholder='State')
		lForm.custom.widget.pincode.update(_placeholder='Pincode')
		lForm.custom.widget.country.update(_placeholder='Country')
		lForm.custom.widget.description.update(_placeholder='Description')

		if lForm.process().accepted:
	     	session.flash='form accepted'

		     pass

		# populate the db

	return dict(form=lForm)
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def leads_edit():if session.is_active==0:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	else:
		lForm= SQLFORM.factory(
	                         Field('company', requires=[IS_NOT_EMPTY('Enter company name')]),
	                         Field('lead_owner', requires=[IS_NOT_EMPTY('Enter lead_owner')]),
	                         Field('first_name', requires=[IS_NOT_EMPTY('Enter first_name')]),
	                         Field('last_name', requires=[IS_NOT_EMPTY('Enter last_name')]),
	                         Field('title', requires=[IS_NOT_EMPTY('Enter title')]),
	                         Field('email_id', requires=[IS_NOT_EMPTY('Enter email_id')]),
	                         Field('phone', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('fax', requires=[]),
	                         Field('mobile', requires=[]),
	                         Field('website', requires=[]),
	                         Field('lead_source', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('lead_status', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('street', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('city', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('state', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('pincode', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('country', requires=[IS_NOT_EMPTY('Enter data')]),
		                 	 Field('description', requires=[IS_NOT_EMPTY('Enter data')])
		                 )
		lForm.custom.widget.company.update(_placeholder='Company')
		lForm.custom.widget.lead_owner.update(_placeholder='Lead Owner')
		lForm.custom.widget.first_name.update(_placeholder='First Name')
		lForm.custom.widget.last_name.update(_placeholder='Last Name')
		lForm.custom.widget.title.update(_placeholder='Title')
		lForm.custom.widget.email_id.update(_placeholder='Email ID')
		lForm.custom.widget.phone.update(_placeholder='Phone')
		lForm.custom.widget.fax.update(_placeholder='Fax')
		lForm.custom.widget.mobile.update(_placeholder='Mobile')
		lForm.custom.widget.website.update(_placeholder='Website')
		lForm.custom.widget.lead_source.update(_placeholder='Lead Source')
		lForm.custom.widget.lead_status.update(_placeholder='Lead Status')
		lForm.custom.widget.street.update(_placeholder='Street')
		lForm.custom.widget.city.update(_placeholder='City')
		lForm.custom.widget.state.update(_placeholder='State')
		lForm.custom.widget.pincode.update(_placeholder='Pincode')
		lForm.custom.widget.country.update(_placeholder='Country')
		lForm.custom.widget.description.update(_placeholder='Description')

		if lForm.process().accepted:
		     session.flash='form accepted'
		     redirect('contacts')
		     pass

		# populate the db
	return dict(form=lForm)


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$--CONTACTS--$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts():
	return locals()


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_add():
	if session.is_active==0:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	else:
		lForm= SQLFORM.factory(
	                         Field('company', requires=[IS_NOT_EMPTY('Enter company name')]),
	                         Field('lead_owner', requires=[IS_NOT_EMPTY('Enter lead_owner')]),
	                         Field('first_name', requires=[IS_NOT_EMPTY('Enter first_name')]),
	                         Field('last_name', requires=[IS_NOT_EMPTY('Enter last_name')]),
	                         Field('title', requires=[IS_NOT_EMPTY('Enter title')]),
	                         Field('email_id', requires=[IS_NOT_EMPTY('Enter email_id')]),
	                         Field('phone', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('fax', requires=[]),
	                         Field('mobile', requires=[]),
	                         Field('website', requires=[]),
	                         Field('lead_source', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('lead_status', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('street', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('city', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('state', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('pincode', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('country', requires=[IS_NOT_EMPTY('Enter data')]),
		                 	 Field('description', requires=[IS_NOT_EMPTY('Enter data')])
		                 )
		lForm.custom.widget.company.update(_placeholder='Company')
		lForm.custom.widget.lead_owner.update(_placeholder='Lead Owner')
		lForm.custom.widget.first_name.update(_placeholder='First Name')
		lForm.custom.widget.last_name.update(_placeholder='Last Name')
		lForm.custom.widget.title.update(_placeholder='Title')
		lForm.custom.widget.email_id.update(_placeholder='Email ID')
		lForm.custom.widget.phone.update(_placeholder='Phone')
		lForm.custom.widget.fax.update(_placeholder='Fax')
		lForm.custom.widget.mobile.update(_placeholder='Mobile')
		lForm.custom.widget.website.update(_placeholder='Website')
		lForm.custom.widget.lead_source.update(_placeholder='Lead Source')
		lForm.custom.widget.lead_status.update(_placeholder='Lead Status')
		lForm.custom.widget.street.update(_placeholder='Street')
		lForm.custom.widget.city.update(_placeholder='City')
		lForm.custom.widget.state.update(_placeholder='State')
		lForm.custom.widget.pincode.update(_placeholder='Pincode')
		lForm.custom.widget.country.update(_placeholder='Country')
		lForm.custom.widget.description.update(_placeholder='Description')

		if lForm.process().accepted:
		     session.flash='form accepted'
		     redirect('contacts')
		     pass

		# populate the db
	return dict(form=lForm)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def contacts_edit():
	if session.is_active==0:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	else:
		lForm= SQLFORM.factory(
	                         Field('company', requires=[IS_NOT_EMPTY('Enter company name')]),
	                         Field('lead_owner', requires=[IS_NOT_EMPTY('Enter lead_owner')]),
	                         Field('first_name', requires=[IS_NOT_EMPTY('Enter first_name')]),
	                         Field('last_name', requires=[IS_NOT_EMPTY('Enter last_name')]),
	                         Field('title', requires=[IS_NOT_EMPTY('Enter title')]),
	                         Field('email_id', requires=[IS_NOT_EMPTY('Enter email_id')]),
	                         Field('phone', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('fax', requires=[]),
	                         Field('mobile', requires=[]),
	                         Field('website', requires=[]),
	                         Field('lead_source', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('lead_status', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('street', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('city', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('state', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('pincode', requires=[IS_NOT_EMPTY('Enter data')]),
	                         Field('country', requires=[IS_NOT_EMPTY('Enter data')]),
		                 	 Field('description', requires=[IS_NOT_EMPTY('Enter data')])
		                 )
		lForm.custom.widget.company.update(_placeholder='Company')
		lForm.custom.widget.lead_owner.update(_placeholder='Lead Owner')
		lForm.custom.widget.first_name.update(_placeholder='First Name')
		lForm.custom.widget.last_name.update(_placeholder='Last Name')
		lForm.custom.widget.title.update(_placeholder='Title')
		lForm.custom.widget.email_id.update(_placeholder='Email ID')
		lForm.custom.widget.phone.update(_placeholder='Phone')
		lForm.custom.widget.fax.update(_placeholder='Fax')
		lForm.custom.widget.mobile.update(_placeholder='Mobile')
		lForm.custom.widget.website.update(_placeholder='Website')
		lForm.custom.widget.lead_source.update(_placeholder='Lead Source')
		lForm.custom.widget.lead_status.update(_placeholder='Lead Status')
		lForm.custom.widget.street.update(_placeholder='Street')
		lForm.custom.widget.city.update(_placeholder='City')
		lForm.custom.widget.state.update(_placeholder='State')
		lForm.custom.widget.pincode.update(_placeholder='Pincode')
		lForm.custom.widget.country.update(_placeholder='Country')
		lForm.custom.widget.description.update(_placeholder='Description')

		if lForm.process().accepted:
		     session.flash='form accepted'
		     redirect('contacts')
		     pass

		# populate the db
	return dict(form=lForm)


