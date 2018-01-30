# this page is the company and superuser registration page for the 1st time app run
# this also include the custon registration page of normal user
from datetime import datetime


#=============================================================================
#this function should include a methord to check that it runs only for 1 time
#it can contain multiple view pages according to the need
def company_reg_page():
	# main registration form for the company and the super admin
	lForm = SQLFORM.factory(
					        Field('company_name', requires=[IS_NOT_EMPTY('**This field is mandatory'),
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
					        						   		 IS_DECIMAL_IN_RANGE(10,12,error_message='enter valid phone number')]),
					        #..............superadmin...........................
					        Field('first_name', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							  IS_LENGTH(240,error_message='exeeds the length')]),
					        Field('last_name', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							 IS_LENGTH(240,error_message='exeeds the length')]),
					        Field('email_id', requires=[IS_NOT_EMPTY('**This field is mandatory'),
					        							IS_NOT_IN_DB(db,db.general_superadmin_details.email_id,error_message='email id already registered'),
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
					        									 IS_IN_DB(db,db.general_master_verification_details.verification_code,error_message='enter a valid code')]),
					        )

	if lForm.process().accepted:
		
		# try to feed into the db
		try:
			lCompanyId = db.general_company_details.insert( 
				company_name=lForm.company_name,
				company_identification=lForm.company_identification,
				company_address_line1=lForm.company_address_line1,
				company_address_line2=lForm.company_address_line2,
				country=lForm.country,
				states=lForm.states,
				city=lForm.city,
				pincode=lForm.pincode,
				office_number=lForm.office_number,
				is_active=True,
				db_entry_time=lambda:datetime.now()
				)
	
		# if fails to feed the db give out the error massage
		except Exception as e:
			lErrorMessage="Errors while inserting company details (%s)" % e.message
			lMessageFlag = "e"
			redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
		else:
			try:
				#insert the details for superadmin
				db.general_superadmin_details.insert(
				company_id=lCompanyId,
				first_name=lForm.first_name,
				last_name=lForm.last_name,
				email_id=lForm.email_id,
				mobile_number=lForm.mobile_number,
				password=lForm.password,
				verification_code=lForm.verification_code,
				ip_address=current.request.client,
				# locations=
				is_active=True,
				db_entry_time=lambda:datetime.now()
				)
				pass
			except Exception as e:
				lErrorMessage="Errors while inserting superadmin details (%s)" % e.message
				lMessageFlag = "e"
				#delete the record inserted in company table as well
				redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
			else:
				# flash the massage of succes registration
				session.flash='registration successful'

				pass



	return dict(form=lForm)


#==============================================================================
# for the form input check
def company_reg_page_check():

	if lMessageFlag == 's':
		# send the data to the model
		try:
			db.general_company_details.insert(
				company_name=lForm.institute_name,
				company_identification=lForm.legal_reg_no,
				company_address_line1=lForm.address_line1,
				company_address_line2=lForm.address_line2,
				country=lForm.country,
				states=lForm.city_state,
				city=lForm.city,
				pincode=lForm.pincode,
				office_number=lForm.work_no,
				is_active=True,
				db_entry_time=lambda:datetime.now()
			)
		except Exception as e:
			lErrorMessage="Errors while inserting company details (%s)" % e.message
			lMessageFlag = "e"
			redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
		else:
			try:
				#insert the details for superadmin
				pass
			except Exception as e:
				lErrorMessage="Errors while inserting superadmin details (%s)" % e.message
				lMessageFlag = "e"
				#delete the record inserted in company table as well
				redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
			else:
				pass
		
		# redirect to the 1st time login page of the super admin
		redirect(URL('LoginPage/first_time_login_SA',vars={'message':'registration succesfull'}))


	return 


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
	return locals()



