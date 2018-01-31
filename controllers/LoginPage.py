# this page include all the login pages 
from datetime import datetime

#==============================================================================
#function: first_time_login_SA
#dis: for the first time login of the super admin, should run only once 
#	  and contain basic tutorial for the app setup
# will be sent to the dashboard from this
# this page will only be redirected from the registration page
def first_time_login_SA():
	session.no_loging_attempts=0
	lSFlag=0
	# a form to get the user login data, this does not contain a inbuid validation
	lRegEmail= db.general_superadmin_details.email_id
	lForm= SQLFORM.factory(
							Field('email_id', requires=[IS_NOT_EMPTY('Enter email id'),
														IS_EMAIL(error_message="Invalid Email ID !"),
														IS_IN_DB(db,lRegEmail,error_message='Invalid Email ID !')]),
							Field('password', requires=[IS_NOT_EMPTY('Enter password')],type='password')
							)
	# add the place holders in the form
	lForm.custom.widget.email_id.update(_placeholder='Email ID')
	lForm.custom.widget.password.update(_placeholder='Password')

	session.flash='current input'

	if lForm.process().accepted:
		session.flash='*accepted'
		# try if the pass matches or not
		try:
			if db((db.general_superadmin_details.email_id == lForm.vars.email_id) & (db.general_superadmin_details.password == lForm.vars.password)).isempty():
				# password is matched with the username in this if condition,
				# if they donot match, it will exhicute
				# increase the no of attempts 
				session.no_loging_attempts=+1
				session.flash='*Invalid username or password.*'
				lSFlag=0
				pass

			else:
				try:
					#set the user session 
					# also take the session id while entering the data
					session.session_id=db.general_session.insert( 
						user_id=db((db.general_superadmin_details.email_id == lForm.vars.email_id) & (db.general_superadmin_details.password == lForm.vars.password)).select()[0].id,
						user_type="super_admin",
						login_time=lambda:datetime.now(),
						ip_address=request.env.remote_addr,  # to get the ip address of the user
						)
					session.flash='*succesful insert in session db'
					pass 

				except Exception as e:
					session.flash="*Errors while inserting session details (%s)" % e.message
					lSFlag=0
					pass

				else:
					try:
						db((db.general_superadmin_details.email_id == lForm.vars.email_id) & (db.general_superadmin_details.password == lForm.vars.password)).update(
								last_login_time=lambda:datetime.now(),
								no_login_attempts= session.no_loging_attempts
								)
						# reset the no of attempts
						session.no_loging_attempts=0
						session.flash='* succesfull general_superadmin_details'
						pass 

					except Exception as e:
						session.flash +="*Errors while inserting session details (%s)" % e.message
						lSFlag=0
						pass

					else:
						lSFlag=1
						pass

		except Exception as e:
			session.flash='* error while checking the data %s' % e

			pass

		# if everything is correct redirect to the dashboard
		if lSFlag==1:
			redirect('../../ERP/DashBoard/dashboard_SA')
			pass
		else:
			session.flash= 'error in login '
			redirect('first_time_login_SA')
		pass
	

	return dict(form=lForm)

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




def test():

	if lForm.process().accepted :
		session.flash=' 1. '
		# have filed the login form now have to authenticate it with the db
		try:
			if db((db.general_superadmin_details.email_id == lForm.vars.email_id) & (db.general_superadmin_details.password == lForm.vars.password)).isempty():
				# password is matched with the username in this if condition,
				# if they donot match, it will exhicute
				# increase the no of attempts 
				session.no_loging_attempts=+1
				session.flash +='Invalid username or password'
				redirect(URL('first_time_login_SA'))
				pass

			# else the password and id are correct
			else:
				# take the row from the db into rows
				rows = db((db.general_superadmin_details.email_id == lForm.vars.email_id) & (db.general_superadmin_details.password == lForm.vars.password)).select()
				session.flash=' 2. '
				for row in rows:
					session.flash=' 3. '
					try:
						#set the user session 
						# also take the session id while entering the data
						session.session_id=db.general_session.insert( 
							user_id=lForm.vars.email_id,
							user_type="super_admin",
							login_time=lambda:datetime.now(),
							ip_address=current.request.client,
							)
						session.flash +='succesful insert in session db'
					except Exception as e:
						session.flash +="Errors while inserting session details (%s)" % e.message
						redirect(URL('company_reg_page'))
					else:
						try:
							db.general_superadmin_details.insert(
								last_login_time=lambda:datetime.now(),
								no_login_attempts= session.no_loging_attempts
								)
							session.no_loging_attempts=0
							session.flash='succesfull general_superadmin_details'
						except Exception as e:
							session.flash="Errors while inserting session details (%s)" % e.message
							redirect(URL('company_reg_page'))
						else:
							session.flash='successful login'
							# after the succesfull login redirect to the dash board
							redirect(URL('../../ERP/DashBoard/dashboard_SA'))
						pass
		except Exception as e:
			session.flash="Errors while login process (%s)" % e.message
			redirect(URL('first_time_login_SA'))
		pass # for the accepted if condi.
	return