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
	# show the error Messages of the registration form
	if request.vars.lMessageFlag == 'e':
		# give out the error Message
		response.flash= request.vars.lErrorMessage
		# reset the error Message
		request.vars.lErrorMessage=''
		# reset the error flag
		request.vars.lMessageFlag='s'



	# show the registration page

	return locals()


#==============================================================================
# for the form input check
def company_reg_page_check():

	# recieve all the data from the from
	lFormData= request.post_vars

	# Institute name 
	if not isinstance(lFormData.institute_name, basestring):
		# the field is empty
		lErrorMessage = 'Institute name is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# address_line1	
	if not isinstance(lFormData.address_line1, basestring):
		# the field is empty
		lErrorMessage = 'address line1	is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# region
	if not isinstance(lFormData.region, basestring):
		# the field is empty
		lErrorMessage = 'region is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# city_state
	if not isinstance(lFormData.city_state, basestring):
		# the field is empty
		lErrorMessage = 'city state is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# country
	if not isinstance(lFormData.country, basestring):
		# the field is empty
		lErrorMessage = 'country is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
	
	# pincode
	if not isinstance(lFormData.pincode, basestring):
		# the field is empty
		lErrorMessage = 'pincode is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
	elif not lFormData.pincode.isdigit():
		# wrong input
		lErrorMessage='wrong pincode'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# first_name
	if not isinstance(lFormData.first_name, basestring):
		# the field is empty
		lErrorMessage = 'first name is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# last_name
	if not isinstance(lFormData.last_name, basestring):
		# the field is empty
		lErrorMessage = 'last name is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# designation
	if not isinstance(lFormData.designation, basestring):
		# the field is empty
		lErrorMessage = 'designation is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

	# email_id
	if not isinstance(lFormData.email_id, basestring):
		# the field is empty
		lErrorMessage = 'email id is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
	elif '@' and '.' not in lFormData.email_id:
		# wrong email id
		lErrorMessage='wrong email id' 
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
	elif '@'== lFormData.email_id[-1] or '.'== lFormData.email_id[-1]:
		#wrong email id
		lErrorMessage=' wrong email id' 
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))


	# mob_no
	if not isinstance(lFormData.mob_no, basestring):
		# the field is empty
		lErrorMessage = 'mobile no is empty'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))
	elif not lFormData.pincode.isdigit():
		# wrong input
		lErrorMessage='wrong pincode'
		lMessageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMessage':lErrorMessage,'lMessageFlag':lMessageFlag}))

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
		
		# redirect to the login page
		redirect(URL('login',vars={'message':'registration succesfull'}))


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
	if isinstance(lPostData.city_state, basestring):
		name= True
	else : name = lPostData.pincode 
	lData= request.vars
	lClient= current.request.client
	d=123
	string= lPostData.city_state + 'adsfa'
	return locals()