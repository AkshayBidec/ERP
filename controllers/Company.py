import ssl
from datetime import datetime
from gluon.tools import Service
service = Service(globals())
import _pickle as cPickle
from xmlrpc.server import SimpleXMLRPCServer

context = ssl.SSLContext()
link=str(request.env.wsgi_url_scheme)+"://"+str(request.env.http_host)	

# it will contain all the views and the api call related to the crm app
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# function to get the field names to show the form
@service.xmlrpc
def company_add_ff():
	field_names={'field':'value'}
	rows = db(db.general_contact_company_field.is_active==True).select()
	lList=[]
	for row in rows:

		lList=[row.field_widget_attributes,row.field_requires_attributes] 		# make a list of required details for the field

		field_names.update({row.field_name:lList})

	del field_names['field']
	return dict(field_names)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
@service.xmlrpc
def add_company(data):
	
	done=0
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	try:
		lKeyId=db.general_contact_company_field_key.insert(
				id=data['data']['company_key_id'],
				company_id=data['data']['company_id'] ,
				db_entry_time=lambda:datetime.now(),
				db_entered_by=data['data']['user_id'],
				session_id=data['data']['session_id']
			)
		lReturnDict['lKeyId']=int(lKeyId)
	except Exception as e:
		lReturnDict['msg']='error in adding company key (%s)' %e
		return lReturnDict
	else:
		rows=db(db.general_contact_company_field.field_name).select()
		for row in rows:
			if row.is_active== True:
				try:
					db.general_contact_company_field_value.insert(
						field_id=row.id ,
						company_key_id=lKeyId ,
						field_value=data['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id'],
						company_id=data['data']['company_id'],
						session_id=data['data']['session_id']
						)
					pass
				except Exception as e:
					lReturnDict['msg']='error in adding company data (%s)' %e
					return lReturnDict
				else:
					done=1
		pass

	if done==1:
		lReturnDict['msg']="company done"
		return lReturnDict

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def call(): return service() 


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def autocomplete():
	if not request.vars.data: return ''