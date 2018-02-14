# this contr. contain all the dashbords, SA dashboard and general 

#==============================================================================
#function: dashboard_SA
#dis: it is the special dashboard for the SA and will include the special setting 
def dashboard():
	
	# if session is active
	if session.active ==1:
		pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

		pass
	return locals()
