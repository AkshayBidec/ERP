# this page is the company and superuser registration page for the 1st time app run
# this also include the custon registration page of normal user
from datetime import datetime


#=============================================================================
#this function should include a methord to check that it runs only for 1 time
#it can contain multiple view pages according to the need
def company_reg_page():
	# main registration form for the company and the super admin
	error_message=''
	# flag to represent the success of registration 0= fail
	lSFlag=0
	lForm = SQLFORM.factory(
					        Field('company_name', requires=[IS_NOT_EMPTY(error_message='**This field is mandatory'),
					        								IS_LENGTH(990,error_message='exeeds the length')]),
					        Field('company_identification', requires=IS_NOT_EMPTY('**This field is mandatory')),
					        Field('company_address_line1', requires=IS_NOT_EMPTY('**This field is mandatory')),
					        Field('company_address_line2',),
					        Field('country', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        						   IS_LENGTH(490,error_message='exeeds the length')]),
					        Field('states', requires=[IS_NOT_EMPTY('**This field is mandatory'),
			        								 IS_LENGTH(490,error_message='exeeds the length')]),
					        Field('city', requires=[IS_NOT_EMPTY('**This field is mandatory'),
			        								IS_LENGTH(490,error_message='exeeds the length')]),
					        Field('pincode', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        						   IS_MATCH('^\d{6}$',error_message='not a valid zip code')]),
					        Field('office_number', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        						   		 IS_DECIMAL_IN_RANGE(12,error_message='enter valid phone number')]),
					        #..............superadmin...........................
					        Field('first_name', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							  IS_LENGTH(240,error_message='exeeds the length')]),
					        Field('last_name', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							 IS_LENGTH(240,error_message='exeeds the length')]),
					        Field('email_id', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							IS_NOT_IN_DB(db,db.general_user.email_id,error_message='email id already registered'),
					        							IS_EMAIL(error_message="invalid email ID"),
					        							IS_LENGTH(490,error_message='exeeds the length')]),
					        Field('mobile_number', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        						   		 IS_MATCH('^[789]\d{9}$',error_message='enter a valid phone number')]),
					        Field('password', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							IS_ALPHANUMERIC(error_message='must be alphanumeric!'),
					        							IS_LENGTH(minsize=8)], type='password'),
					        Field('verify_password', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        								   IS_EQUAL_TO(request.vars.password,error_message='passwords do not match')]
					        								   ,type='password'),
					        Field('verification_code', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        									 IS_IN_DB(db,db.general_master_verification_details.verification_code,error_message='enter a valid code'),
					        									 IS_NOT_IN_DB(db,db.general_company_details.verification_code,error_message='code is alredy been used')])
					         )
	session.flash='hello '
	
	if lForm.process().accepted:
		session.flash+='* form accepted *'
		# check the code is valid or not
		if db(db.general_master_verification_details.verification_code == lForm.vars.verification_code).select()[0].is_active:
			session.flash+='* valid code *'
			try:
				lCompanyId = db.general_company_details.insert( 
					company_name=lForm.vars.company_name,
					company_identification=lForm.vars.company_identification,
					verification_code= lForm.vars.verification_code,
					company_address_line1=lForm.vars.company_address_line1,
					company_address_line2=lForm.vars.company_address_line2,
					country=lForm.vars.country,
					states=lForm.vars.states,
					city=lForm.vars.city,
					pincode=lForm.vars.pincode,
					office_number=lForm.vars.office_number,
					is_active=True,
					db_entry_time=lambda:datetime.now()
					)

				session.flash+='* enter in company details *'
				pass # for try

			except Exception as e:
				session.flash+=" * Errors while inserting company details (%s) *" % e.message
				lSFlag=0
				pass

			else:
				try:
					# insert the details for superadmin
					db.general_user.insert(
						company_id=lCompanyId,
						first_name=lForm.vars.first_name,
						last_name=lForm.vars.last_name,
						email_id=lForm.vars.email_id,
						mobile_number=lForm.vars.mobile_number,
						password=lForm.vars.password,
						ip_address=request.env.remote_addr,
						is_active=True,
						db_entry_time=lambda:datetime.now(),
						is_superadmin=1
						)
					session.flash+='* enter in user details *'					
					pass

				except Exception as e:
					session.flash+="* Errors while inserting vc details (%s) *" % e.message
					lSFlag=0
					pass

				else:
					try:
						#insert the details for superadmin
						db(db.general_master_verification_details.verification_code == lForm.vars.verification_code).update(
						is_active=False
						)
						session.flash+='* enter verification_code *'
						pass
					except Exception as e:
						session.flash+="* Errors while inserting vc details (%s) *" % e.message
						lSFlag=0
					else:
						# flash the massage of succes registration
						session.flash+='* registration successful *'
						lSFlag=1 # successful reg
					
					pass

				pass # try-else 1

		if lSFlag== 1: # registered
			redirect(URL('../../../ERP/LoginPage/first_time_login_SA'))
			pass
		# else:
		# 	session.flash+='not reg'
		# 	# redirect('company_reg_page')
			


	return dict(form=lForm)

#==============================================================================
# this function is only for the superuser registration 
# it gets redirected to the 1st time login and tutorial page
def superuser_reg_page():
    return locals()

#==============================================================================
# this page can be motified from the superuser
def general_reg_page():
    return locals()

#==============================================================================
from gluon import *
# this function is for testing only
def other():
	lPostData= request.post_vars
	if isinstance(lPostData.email_id, basestring):
		name= str(type(lPostData.email_id))
	else : name = lPostData.pincode 
	data= len("  ")
	lClient= current.request.client
	d=123
	string= lPostData.city_state + 'adsfa'

	if lForm.process().accepted:
		session.flash='* data accepted *'
		# check the status of the verification code
		if db(db.general_master_verification_details.verification_code == lForm.vars.verification_code).select()[0].is_active:
			# try to feed into the db
			session.flash+='* code corect *'
			try:
				# lCompanyId = db.general_company_details.insert( 
				# 	company_name=lForm.vars.company_name,
				# 	company_identification=lForm.vars.company_identification,
				# 	verification_code= lForm.vars.verification_code,
				# 	company_address_line1=lForm.vars.company_address_line1,
				# 	company_address_line2=lForm.vars.company_address_line2,
				# 	country=lForm.vars.country,
				# 	states=lForm.vars.states,
				# 	city=lForm.vars.city,
				# 	pincode=lForm.vars.pincode,
				# 	office_number=lForm.vars.office_number,
				# 	is_active=True,
				# 	db_entry_time=lambda:datetime.now()
				# 	)

				session.flash+='* enter in company details *'
				
			except Exception as e:
				session.flash+=" * Errors while inserting company details (%s) *" % e.message
				lSFlag=0
			else:
				try:
				# 	#insert the details for superadmin
				# 	db.general_user.insert(
				# 	company_id=lCompanyId,
				# 	first_name=lForm.vars.first_name,
				# 	last_name=lForm.vars.last_name,
				# 	email_id=lForm.vars.email_id,
				# 	mobile_number=lForm.vars.mobile_number,
				# 	password=lForm.vars.password,
				# 	ip_address=request.env.remote_addr,
				# 	is_active=True,
				# 	db_entry_time=lambda:datetime.now()
				# 	)
					session.flash+='* enter in user details *'
				# 	pass


				except Exception as e:
					session.flash+=" * Errors while inserting user details (%s) *" % e.message
				# 	lSFlag=0
				else:
					# try:
				# 		#insert the details for superadmin
				# 		db(db.general_master_verification_details.verification_code == lForm.vars.verification_code).update(
				# 		is_active=False
				# 		)
				# 		pass
				# 	except Exception as e:
				# 		session.flash="Errors while inserting vc details (%s)" % e.message
				# 		redirect(URL('company_reg_page'))
				# 	else:
				# 		# flash the massage of succes registration
					session.flash='registration successful'
				# 		lSFlag=1 # successful reg
					pass
				pass

		else:
			session.flash+='* verification code alredy used *'
			lSFlag=0
			# 
			pass
		pass

	return locals()



