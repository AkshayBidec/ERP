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
def contact_add_ff():
	field_names={'field':'value'}
	rows = db(db.general_contact_field.is_active==True).select()
	lList=[]
	for row in rows:

		lList=[row.field_widget_attributes,row.field_requires_attributes] 		# make a list of required details for the field

		field_names.update({row.field_name:lList})

	del field_names['field']
	return dict(field_names)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# function to get the field names to show the form
@service.xmlrpc
def add_contact(data):
	
	done=0
	
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	
	try:
		lKeyId=db.general_contact_field_key.insert(
				id=data['data']['contact_key_id'],
				company_key_id=data['data']['company_key_id'],
				company_id=data['data']['company_id'] ,
				db_entry_time=lambda:datetime.now(),
				db_entered_by=data['data']['user_id'],
				session_id=data['data']['session_id']
			)
	
		lReturnDict['lKeyId']=int(lKeyId)
	
	except Exception as e:
		lReturnDict['msg']='error in adding contact key (%s)' %e
		return lReturnDict	
	
	else:
		rows=db(db.general_contact_field.field_name != None).select()
		for row in rows:
			if row.is_active== True:
				try:
					db.general_contact_field_value.insert(
						field_id=row.id ,
						contact_key_id=lKeyId ,
						field_value=data['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id'],
						company_id=data['data']['company_id'],
						session_id=data['data']['session_id']
						)
					pass
				except Exception as e:
					lReturnDict['msg']='error in adding contact data (%s)' %e
					return lReturnDict	
				else:
					done=1

	if done==1:
		lReturnDict['msg']=' contact done '
	return lReturnDict	

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# function to update the company id for specific contact
@service.xmlrpc
def update_company_contact_key_id(data):
	done=0
	
	lReturnDict={'lKeyId':0,'msg':''}
	# have to enter the data into the key table first
	
	try:
		db(db.general_contact_field_key.id==data['data']['contact_key_id']).update(
				company_key_id=data['data']['company_key_id'],
				db_updated_by=data['data']['user_id'] ,
				db_update_time=lambda:datetime.now()
			)
		
	except Exception as e:
		lReturnDict['msg']='error in adding contact key (%s)' %e
		return lReturnDict	

	else:
		done=1


	if done==1:
		lReturnDict['msg']=' contact updated '
	return lReturnDict
	pass

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def call(): return service() 


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def autocomplete():
	if not request.vars.data: return ''