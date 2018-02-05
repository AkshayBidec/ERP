# this contr. contain all the dashbords, SA dashboard and general 

#==============================================================================
#function: dashboard_SA
#dis: it is the special dashboard for the SA and will include the special setting 
def dashboard():
	
	# if session is not active
	if session.active ==0:
		redirect(URL('../../LoginPage/login')) 

	# if session is active
	else:
		# taek the reqired data from the session
		# take the required data from the db


		pass
	return locals()
