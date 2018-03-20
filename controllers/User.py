# this page include all the pages associated to User 
from datetime import datetime # library to use datetime functions

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
		session.flash=''
		if lForm.process().accepted:
			#****************Code to submit the details in DB***********************

			try:
				#insert user details in user table
				db.general_user.insert(
					company_id=session.company_id,
					first_name=lForm.vars.first_name,
					last_name=lForm.vars.last_name,
					email_id=lForm.vars.email_id,
					mobile_number=lForm.vars.mobile_number,
					password=lForm.vars.password,
					temp_password=lForm.vars.password,
					ip_address=request.env.remote_addr,
					is_active=True,
					db_entry_time=lambda:datetime.now(),
					is_superadmin=0
				)
				pass
			except Exception as e:
				session.flash+="* Errors while registering user (%s) *" % e.message
				lSFlag=0
				raise e
			else:
				# flash the massage of succes registration
				session.flash+='* registration successful *'
				lSFlag=1 # successful reg
				pass

			if lSFlag == 1:
				redirect(URL('../../User/add_user'))
				pass
			pass
		pass
	return dict(form=lForm)

#==============================================================================
#function: user
#dis: for view the user list and home page of user management
# will be sent to the view of user list
# this page will only can be view by directly clicking link of dashboard
def user():
	if session.active==1:
		return dict(data='')
		pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
		pass
	pass

#==============================================================================
#function: add_user
#dis: for adding or registering new user in the system
# will be sent to the view of user list
# this page will only can be view by directly clicking link of dashboard
def add_user_feature():

	# if session is not active
	if session.active ==0:
		redirect(URL('../../LoginPage/login')) 
		pass
	# if session is active
	else:
		return dict(form='a')
		pass
	pass
