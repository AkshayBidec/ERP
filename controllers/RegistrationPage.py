# this page is the company and superuser registration page for the 1st time app run
# this also include the custon registration page of normal user
from datetime import datetime

# this represents the s=succes or the e=error in the registration form
# lMessageFlag ='s'
# lErrorMessage=''
#=============================================================================
#this function should include a mothord to check that it runs only for 1 time
#it can contain multiple view pages according to the need
def company_reg_page():
	
	#======================================================
	# # show the error Messages of the registration form
	# if request.vars.lMessageFlag == 'e':
	# 	# give out the error Message
	# 	response.flash= request.vars.lErrorMessage
	# 	# reset the error Message
	# 	request.vars.lErrorMessage=''
	# 	# reset the error flag
	# 	request.vars.lMessageFlag='s'

	#======================================================
	# way 2nd using SQLFORM
	form = SQLFORM.factory(
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
					        							IS_EMAIL("invalid email ID"),
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

	if form.process().accepted:
		# flash the massage of succes registration
		session.flash='registration succesfull'


	return locals()


#==============================================================================
# for the form input check
def company_reg_page_check():
	
	if lMessageFlag == 's':
		# send the data to the model
		try:
			db.general_company_details.insert(
				company_name=lFormData.institute_name,
				company_identification=lFormData.legal_reg_no,
				company_address_line1=lFormData.address_line1,
				company_address_line2=lFormData.address_line2,
				country=lFormData.country,
				states=lFormData.city_state,
				city=lFormData.city,
				pincode=lFormData.pincode,
				office_number=lFormData.work_no,
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



