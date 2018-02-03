# this page include all the login pages 
from datetime import datetime

#==============================================================================
#function: first_time_login_SA
#dis: for the first time login of the super admin, should run only once 
#	  and contain basic tutorial for the app setup
# will be sent to the dashboard from this
# this page will only be redirected from the registration page
def login():
	# check for the any active sessions on the machine
	if session.active==1:
		# redirect it to the current session dashboard
		redirect(URL('../../ERP/DashBoard/'))
	else:
		# a variable for the no of attempts
		if session.no_loging_attempts== None:
			session.no_loging_attempts=0 
			pass
		# flag for the succesfull login
		lSFlag=0
		# a flag to tell the dashboard that it is first time login or not
		session.first_time_login=0
		# take the list of available email_ids for the login check. @@@@
		lRegEmail= db.general_user.email_id
		# a form to get the user login data, this does not contain a inbuid validation
		lForm= SQLFORM.factory(
								Field('email_id', requires=[IS_NOT_EMPTY('Enter email id'),
															IS_EMAIL(error_message="Invalid Email ID !"),
															IS_IN_DB(db,lRegEmail,error_message='Invalid Email ID !')]),
								Field('password', requires=[IS_NOT_EMPTY('Enter password')],type='password')
								)
		# add the place holders in the form
		lForm.custom.widget.email_id.update(_placeholder='Email ID')
		lForm.custom.widget.password.update(_placeholder='Password')
		lForm.custom.update(_class='form')

		if lForm.process().accepted:
			session.flash='*accepted'
			# try if the pass matches or not
			try:
				if db((db.general_user.email_id == lForm.vars.email_id) & (db.general_user.password == lForm.vars.password)).isempty():
					# password is matched with the username in this if condition,
					# if they donot match, it will exhicute
					# increase the no of attempts 
					session.no_loging_attempts=+1
					session.flash='*Invalid username or password.*'
					lSFlag=0
					pass

				else:
					# password is correct, fetch the user detail row
					rows = db((db.general_user.email_id == lForm.vars.email_id) & (db.general_user.password == lForm.vars.password)).select()
					for row in rows:
						# fetch all the related data from session
						session_flag=db(db.general_session.user_id == row.id).select() 
						if len(session_flag)>0:
							# not a 1st time user
							if session_flag[-1].is_active ==1:
								# session is active at other place
								session.message=session.flash='already Logged in to other machine, Logout to continue'
								# redirect('logout')
								lSFlag=0
								pass
							else:
						 		# no active session
								try:
									#set the user session 
									# also take the session id while entering the data
									session.session_id=db.general_session.insert( 
										user_id=row.id,
										user_type="super_admin",
										login_time=lambda:datetime.now(),
										ip_address=request.env.remote_addr,  # to get the ip address of the user
										is_active=1 # .i.e the session is started for userid
										)
									session.company_id=row.company_id
									session.username=row.email_id
									session.name= row.first_name +" "+ row.last_name
									session.user_id=row.id
									session.login_time= row.last_login_time
									session.user_type='superadmin'
									session.flash='*succesful insert in session db'
									pass 

								except Exception as e:
									session.flash="*Errors while inserting session details (%s)" % e.message
									lSFlag=0
									pass

								else:
									try:
										row.update(
												last_login_time=lambda:datetime.now(),
												no_login_attempts= session.no_loging_attempts
												)
										# reset the no of attempts
										session.flash='* succesfull general_user'
										pass 

									except Exception as e:
										session.flash="*Errors while inserting session details (%s)" % e.message
										lSFlag=0
										pass

									else:
										lSFlag=1
										pass
									pass
								pass
							pass
						else:
				 			# a first time user
							session.first_time_login=1
							# the user is logging in for the 1st time

							try:
								#set the user session 
								# also take the session id while entering the data
								session.session_id=db.general_session.insert( 
									user_id=row.id,
									user_type="super_admin",
									login_time=lambda:datetime.now(),
									ip_address=request.env.remote_addr,  # to get the ip address of the user
									is_active=1 # .i.e the session is started for userid
									)
								session.company_id=row.company_id
								session.username=row.email_id
								session.name= row.first_name +" "+ row.last_name
								session.user_id=row.id
								session.login_time= row.last_login_time
								session.user_type='superadmin'
								session.flash='*succesful insert in session db'
								pass 

							except Exception as e:
								session.flash="*Errors while inserting session details (%s)" % e.message
								lSFlag=0
								pass

							else:
								try:
									row.update(
											last_login_time=lambda:datetime.now(),
											no_login_attempts= session.no_loging_attempts
											)
									# reset the no of attempts
									session.flash='* succesfull general_user'
									pass 

								except Exception as e:
									session.flash="*Errors while inserting session details (%s)" % e.message
									lSFlag=0
									pass

								else:
									lSFlag=1
									pass
								pass
							pass
						pass
					pass
				pass
			except Exception as e:
				session.flash='* error while checking the data %s' % e

				pass


			# if everything is correct redirect to the dashboard
			if lSFlag==1:
				session.no_loging_attempts=0
				redirect('../../ERP/DashBoard/dashboard')
				pass
			elif session.no_loging_attempts> 3 and lSFlag==0:
				session.flash='* forgot_password'
				# redirect('forgot_password')
				pass
			else:
				session.flash+=' *error in login '
				# redirect('first_time_login_SA')
				pass
	

	return dict(form=lForm)

#==============================================================================
# fucntion: logout
# check that all the data changes are commited or not 
# if not give it a warning 
# end the session and update the db

def logout():
	#clear all the session data
	redirect(URL('login'))
	return dict()

#==============================================================================
# function : login_with_active_session
# the user have its session active on other machines
# so to login properly it have to close all the other sessions of the user 

def login_with_active_session():
	# show a link to end all the sessions for the current user
	return locals()

# def test():

# 	if lForm.process().accepted :
# 		session.flash=' 1. '
# 		# have filed the login form now have to authenticate it with the db
# 		try:
# 			if db((db.general_user.email_id == lForm.vars.email_id) & (db.general_user.password == lForm.vars.password)).isempty():
# 				# password is matched with the username in this if condition,
# 				# if they donot match, it will exhicute
# 				# increase the no of attempts 
# 				session.no_loging_attempts=+1
# 				session.flash +='Invalid username or password'
# 				redirect(URL('first_time_login_SA'))
# 				pass

# 			# else the password and id are correct
# 			else:
# 				# take the row from the db into rows
# 				rows = db((db.general_user.email_id == lForm.vars.email_id) & (db.general_user.password == lForm.vars.password)).select()
# 				session.flash=' 2. '
# 				for row in rows:
# 					session.flash=' 3. '
# 					try:
# 						#set the user session 
# 						# also take the session id while entering the data
# 						session.session_id=db.general_session.insert( 
# 							user_id=lForm.vars.email_id,
# 							user_type="super_admin",
# 							login_time=lambda:datetime.now(),
# 							ip_address=current.request.client,
# 							)
# 						session.flash +='succesful insert in session db'
# 					except Exception as e:
# 						session.flash +="Errors while inserting session details (%s)" % e.message
# 						redirect(URL('company_reg_page'))
# 					else:
# 						try:
# 							db.general_user.insert(
# 								last_login_time=lambda:datetime.now(),
# 								no_login_attempts= session.no_loging_attempts
# 								)
# 							session.no_loging_attempts=0
# 							session.flash='succesfull general_user'
# 						except Exception as e:
# 							session.flash="Errors while inserting session details (%s)" % e.message
# 							redirect(URL('company_reg_page'))
# 						else:
# 							session.flash='successful login'
# 							# after the succesfull login redirect to the dash board
# 							redirect(URL('../../ERP/DashBoard/dashboard'))
# 						pass
# 		except Exception as e:
# 			session.flash="Errors while login process (%s)" % e.message
# 			redirect(URL('first_time_login_SA'))
# 		pass # for the accepted if condi.
# 	return