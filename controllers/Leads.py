# this page contains all the data about the leads
# from apploiERP.LoginPage import first_time_login_SA
def leads_add():
	form= SQLFORM.factory(
							Field('email_id', requires=[IS_NOT_EMPTY('Enter email id')]),
							Field('password', requires=[IS_NOT_EMPTY('Enter password')],type='password')
							)
	form.custom.widget.email_id.update(_placeholder='Email ID')
	form.custom.widget.password.update(_placeholder='Password')

	if form.process().accepted:
				redirect('../../ERP/DashBoard/dashboard_SA')
				pass

	return locals()

def leads_update():
	return dict()