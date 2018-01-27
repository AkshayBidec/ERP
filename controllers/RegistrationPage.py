# this page is the company and superuser registration page for the 1st time app run
# this also include the custon registration page of normal user


# this represents the s=succes or the e=error in the registration form
# lMassageFlag ='s'
# lErrorMassage=''
#=============================================================================
#this function should include a mothord to check that it runs only for 1 time
#it can contain multiple view pages according to the need
def company_reg_page():
	# show the error massages of the registration form
	if request.vars.lMassageFlag == 'e':
		# give out the error massage
		response.flash= request.vars.lErrorMassage
		# reset the error massage
		request.vars.lErrorMassage=''
		# reset the error flag
		request.vars.lMassageFlag='s'



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
		lErrorMassage = 'Institute name is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# address_line1	
	if not isinstance(lFormData.address_line1, basestring):
		# the field is empty
		lErrorMassage = 'address line1	is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# region
	if not isinstance(lFormData.region, basestring):
		# the field is empty
		lErrorMassage = 'region is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# city_state
	if not isinstance(lFormData.city_state, basestring):
		# the field is empty
		lErrorMassage = 'city state is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# country
	if not isinstance(lFormData.country, basestring):
		# the field is empty
		lErrorMassage = 'country is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))
	
	# pincode
	if not isinstance(lFormData.pincode, basestring):
		# the field is empty
		lErrorMassage = 'pincode is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))
	elif not lFormData.pincode.isdigit():
		# wrong input
		lErrorMassage='wrong pincode'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# first_name
	if not isinstance(lFormData.first_name, basestring):
		# the field is empty
		lErrorMassage = 'first name is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# last_name
	if not isinstance(lFormData.last_name, basestring):
		# the field is empty
		lErrorMassage = 'last name is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# designation
	if not isinstance(lFormData.designation, basestring):
		# the field is empty
		lErrorMassage = 'designation is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	# email_id
	if not isinstance(lFormData.email_id, basestring):
		# the field is empty
		lErrorMassage = 'email id is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))
	elif '@' and '.' not in lFormData.email_id:
		# wrong email id
		lErrorMassage='wrong email id' 
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))
	elif '@'== lFormData.email_id[-1] or '.'== lFormData.email_id[-1]:
		#wrong email id
		lErrorMassage=' wrong email id' 
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))


	# mob_no
	if not isinstance(lFormData.mob_no, basestring):
		# the field is empty
		lErrorMassage = 'mobile no is empty'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))
	elif not lFormData.pincode.isdigit():
		# wrong input
		lErrorMassage='wrong pincode'
		lMassageFlag = "e"
		redirect(URL('company_reg_page',vars={'lErrorMassage':lErrorMassage,'lMassageFlag':lMassageFlag}))

	if lMassageFlag = 's':
		# send the data to the model
		
		# redirect to the login page
		redirect(URL('login',vars={'massage'='registration succesfull'}))


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