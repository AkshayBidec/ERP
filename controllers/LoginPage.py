# this page include all the login pages 

#==============================================================================
#function: first_time_login_SA
#dis: for the first time login of the super admin, should run only once 
#	  and contain basic tutorial for the app setup
# will be sent to the dashboard from this
# this page will only be redirected from the registration page
def first_time_login_SA():

	

	return locals()

#==============================================================================
#function: login_SA
#dis:for the general login of the super ardmin
# will be sent to the dashboard from this
def login_SA():
	return locals()

#==============================================================================
# function: sa_authentication
def sa_authentication():
	# take the data from the request form and check it in data base
	redirect(URL('DashBoard/sa', vars={'message':" login succesfull"}))


	return

#==============================================================================
#function: first_time_login
#dis: for the first time login of the general user, should run only once 
#	  and contain basic tutorial for the app and will only appear after the SA validation
# will be sent to the dashboard from this
def first_time_login():
	return locals()

#==============================================================================
#function: login
#dis:for the general user login
# will be sent to the dashboard from this
def login():
	return locals()