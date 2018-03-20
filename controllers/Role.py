# this page include all the pages associated to Role 

#==============================================================================
#function: add_user
#dis: for adding or registering new user in the system
# will be sent to the view of user list
# this page will only can be view by directly clicking link of dashboard
def add_user():
	
	# if session is not active
	if session.active ==0:
		redirect(URL('../../LoginPage/login')) 

	# if session is active
	else:
		# take the reqired data from the session
		# take the required data from the db
		lSFlag = 0
		lForm = SQLFORM.factory(
			Field('first_name', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_LENGTH(240,error_message='exeeds the length')]),
	        Field('last_name', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_LENGTH(240,error_message='exeeds the length')]),
	        Field('email_id', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_NOT_IN_DB(db,db.general_user.email_id,error_message='email id already registered'), IS_EMAIL(error_message="invalid email ID"), IS_LENGTH(490,error_message='exeeds the length')]),
	        Field('mobile_number', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_MATCH('^[789]\d{9}$',error_message='enter a valid phone number')]),
	        Field('password', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_ALPHANUMERIC(error_message='must be alphanumeric!'), IS_LENGTH(minsize=8)], type='password'),
	        Field('verify_password', requires=[IS_NOT_EMPTY('**This field is mandatory'), IS_EQUAL_TO(request.vars.password,error_message='passwords do not match')] ,type='password')
		)

		if lForm.process().accepted:
			#****************Code to submit the details in DB***********************
			if lSFlag == 1:
				redirect(URL('../../UserRoleMgmnt/add_user'))
				pass
			pass
		pass
	return dict(form=lForm)
