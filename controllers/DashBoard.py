# this contr. contain all the dashbords, SA dashboard and general 


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def session_check():
	if session.active==1:
		if db(db.general_session.id== session.session_id).select(db.general_session.is_active)[0].is_active == 1:
			return True
			
		else:		# have to destroy the local session also
			session.session_id=0
			session.company_id=''
			session.username=''
			session.name=''
			session.user_id=''
			session.login_time= ''
			session.user_type=''
			session.active=0
			return False
	else:
		return False
#==============================================================================
#function: dashboard_SA
#dis: it is the special dashboard for the SA and will include the special setting 
def dashboard():
	
	# if session is active
	if session_check():
		pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

		pass
	return locals()
