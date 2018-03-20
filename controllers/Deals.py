import _pickle as cPickle
import xmlrpc.client as xmlrpclib # import the rpc file
import json as json # JSON library
import ssl
import filters
from datetime import datetime
from dateutil import relativedelta
import calendar

context = ssl.SSLContext()
link=str(request.env.wsgi_url_scheme)+"://"+str(request.env.http_host)	

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

# it will contain all the views and the api call related to the deals section of general app
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def deals_filter_fields():	

	# get the field for the filter of the contact and company data from the api
	contactserver=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
	lFilterFields=contactserver.contact_filter_field()

	# now add the fields for the deals filtering
	field_names={'field':'value'}
	rows = db(db.general_deal_field.is_active==True).select(orderby=db.general_deal_field.sequence_no)
	lList=[]
	for row in rows:
		lList=[row.field_widget_attributes,row.field_requires_attributes]
		if row.field_name not in ('final_quotation','final_contract'):
			field_names.update({row.field_name:lList})

	# IS_IN_SET({1:"Reference"},zero="Type of contact")
	lList={}		# a dict to store the options of the deals status
	lListValues=db(db.general_deal_status_master).select(db.general_deal_status_master.deal_status,db.general_deal_status_master.id).as_dict(key='id')
	# for lListValue in lListValues:
	# 	lList[str(lListValue.id)]= lListValue.deal_status
	
	for key in sorted(lListValues.keys()):
		lList[str(key)]=lListValues[key]['deal_status']


	field_names['deal_status'][1]="IS_IN_SET("+str(lList)+",zero='Deal Status')"

	del field_names['field']
	lFilterFields['Deals']=field_names

	return lFilterFields

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def view():
	#this function will show the list of deals currently present in system

	if session_check():
		data=[]
		lFilterFlag=0
		lFilterData={}
		lFilterOutput={}
		if request.vars.lFilterFlag:
			# check the filter flag
			lFilterFlag=int( request.vars.lFilterFlag)
			lFilterOutput=eval(request.vars.lFilterOutput)
			pass
		lDealsList=[]
		lFilterData={
					'lFilterOutput':lFilterOutput,
					'company_id':session.company_id
				}
		if lFilterFlag==0: 		# no filter is applied 
			try:
				lDealsList= get_deals(session.company_id)		# get the data from the api
			except Exception as e:
				session.message=str(lDealsList) + str(e)
				return e
		elif lFilterFlag==1: 	# filter is applied and have to fetch the data from different function
			try:
				
				# lDealsList= get_deals(session.company_id)		# get the data from the api
				lDealsList= get_deals_with_filter(dict(lFilterData))		# get the data from the api
			except Exception as e:
				session.message=str(lDealsList) + str(e)

		lFilterFields=deals_filter_fields()
		
		return dict(data=lDealsList['data'],data_flag=lDealsList['data_flag'],filter_fields=lFilterFields,lFilterData=lFilterData)
		pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
		pass
	pass
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def get_deals(company_id):
	# company_id=25
	# this function will give the list of deals for particular company
	try:
		keys=db((db.general_deal_field_key.is_active == True) & (db.general_deal_field_key.company_id == company_id)).select(db.general_deal_field_key.id,orderby=~db.general_deal_field_key.id)
		i=0
		data_flag=0
		data={}
		for i in range(0,len(keys)):

			deal_data = db((db.general_deal_field_key.id == db.general_deal_field_value.deal_key_id) & (db.general_deal_field_value.field_id == db.general_deal_field.id) & (db.general_deal_field_value.is_active == True) & (db.general_deal_field_value.company_id == company_id) & (db.general_deal_field_key.id == keys[i].id)).select(db.general_deal_field.field_name, db.general_deal_field_value.field_value).as_dict(key='general_deal_field.field_name')

			contact_data = db((db.general_deal_field_key.contact_key_id == db.general_contact_field_value.contact_key_id) & 
				(db.general_contact_field_value.field_id == db.general_contact_field.id) & 
				(db.general_deal_field_key.id == keys[i].id) & 
				(db.general_contact_field_value.is_active == True) & 
				(db.general_contact_field_value.company_id == company_id)
				).select(
				db.general_contact_field.field_name, 
				db.general_contact_field_value.field_value
				).as_dict(key='general_contact_field.field_name')

			company_data = db(
				(db.general_deal_field_key.contact_key_id == db.general_contact_field_key.id) & 
				(db.general_contact_field_key.company_key_id == db.general_contact_company_field_value.company_key_id) & 
				(db.general_contact_company_field_value.field_id == db.general_contact_company_field.id) & 
				(db.general_contact_company_field_value.is_active == True) & 
				(db.general_deal_field_key.id == keys[i].id) & 
				(db.general_contact_company_field_value.company_id == company_id)
				).select(
				db.general_contact_company_field.field_name, 
				db.general_contact_company_field_value.field_value
				).as_dict(key='general_contact_company_field.field_name')

			deal_status = db((db.general_deal_status.deal_key_id == keys[i].id) & (db.general_deal_status.is_active == True) & (db.general_deal_status.deal_status_master_id == db.general_deal_status_master.id)).select(db.general_deal_status.deal_key_id,db.general_deal_status_master.deal_status, orderby=~db.general_deal_status.db_entry_time,limitby=(0,1)).as_dict(key='general_deal_status.deal_key_id')
			data[str(i)]={
				'Company': 'NA' if not company_data else company_data['company_name']['general_contact_company_field_value']['field_value'],
				'Contact Name':str(contact_data['first_name']['general_contact_field_value']['field_value'])+' '+str(contact_data['last_name']['general_contact_field_value']['field_value']),
				'Phone':'NA' if not company_data else str(company_data['phone_no']['general_contact_company_field_value']['field_value']),
				'Amount':deal_data['final_price']['general_deal_field_value']['field_value'],
				'Description':deal_data['description']['general_deal_field_value']['field_value'],
				'Status':'NA' if not deal_status else deal_status[keys[i].id]['general_deal_status_master']['deal_status'],
				# 'Closing Date':'NA' if not deal_data else deal_data['closing_date']['general_deal_field_value']['field_value'],
				'Deal Owner':'NA',
				'deal_key_id':keys[i].id
			}
			data_flag=1
			pass
		if len(data) == 0:
			data['0']={
				'Company': '',
				'Contact Name':'',
				'Phone':'',
				'Amount':'',
				'Description':'',
				'Status':'',
				'Closing Date':'',
				'Deal Owner':'',
				'deal_key_id':''
			}
			data_flag=0
			pass	
		pass
	except Exception as e:
		return 'error in getting data (%s)' %e
	else:
		return dict(data=data,data_flag=data_flag)
		pass
	pass
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def get_deals_with_filter(lFilterData):	# limit is a dict 
	

	#  ={'company_id':25,
	# 	'lFilterOutput':{
	# 	'Company': ['company_name.startswith("q")'],
	# 	 'Contact': [], 
	# 	 'Deals': []
	# 	 } }
	data_flag=0
	lFieldList={}
	 
	present=['company_name','deal_status','description','deal_source','phone_no','email_id']
	for condition in lFilterData['lFilterOutput'].keys():
		for data in lFilterData['lFilterOutput'][condition]:
			if data.split('.')[0] not in present:
				name=data.split('.')[0].title()
				name=name.replace('_',' ')
				# lFieldList.append(str('"'+name+'"'+' : '+'str('+condition.lower()+'_data['+'"'+data.split('.')[0]+'"'+']["general_'+condition.lower()+'_field_value"]["field_value"])'))
				lFieldList[name]=(str('str('+condition.lower()+'_data['+'"'+data.split('.')[0]+'"'+']["general_'+condition.lower()+'_field_value"]["field_value"])'))
		pass


	try:
		# get the filter fields to process the data
		lFilterField=deals_filter_fields()
		data={}
		lContactIdList=[]
		lCompanyIdList=[]
		lDealsIdList=[]
		
		#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
		if len(lFilterData['lFilterOutput']['Company'])>0: # have company data

			# have to select the contact id to get the contacts list for that
			lList=lFilterData['lFilterOutput']['Company']
			lFirstFlag=0

			for lCondition in lList:
				if lFirstFlag==0:

					rows=db(
							(db.general_contact_company_field.id==db.general_contact_company_field_value.field_id)&
							(db.general_contact_company_field.field_name == lCondition.split('.')[0]) &
							(eval('db.general_contact_company_field_value.field_value.'+lCondition.split('.')[1]))&
							(db.general_contact_company_field_key.is_active == True) & 
							(db.general_contact_company_field_key.company_id == lFilterData['company_id'])
							).select(
							db.general_contact_company_field_value.company_key_id
							)
					lCompanyIdList=[]
					for row in rows:
						lCompanyIdList.append(row.company_key_id)

					lFirstFlag=1
					pass
				elif lFirstFlag==1:
					rows=db(
							(db.general_contact_company_field.id==db.general_contact_company_field_value.field_id)&
							(db.general_contact_company_field.field_name == lCondition.split('.')[0]) &
							(eval('db.general_contact_company_field_value.field_value.'+lCondition.split('.')[1]))&
							(db.general_contact_company_field_value.company_key_id.belongs(lCompanyIdList))
							).select(
							db.general_contact_company_field_value.company_key_id
							)
					lCompanyIdList=[]
					for row in rows:
						lCompanyIdList.append(row.company_key_id)

					pass
			#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
			if len(lFilterData['lFilterOutput']['Contact'])>0:	# have contact data
				lList=lFilterData['lFilterOutput']['Contact']
				lFirstFlag=0

				for lCondition in lList:
					if lFirstFlag==0:
						rows=db(
								(db.general_contact_field.id==db.general_contact_field_value.field_id)&
								(db.general_contact_field_key.id==db.general_contact_field_value.contact_key_id)&
								(db.general_contact_field.field_name == lCondition.split('.')[0]) &
								(eval('db.general_contact_field_value.field_value.'+lCondition.split('.')[1]))&
								(db.general_contact_field_key.company_key_id.belongs(lCompanyIdList))&
								(db.general_contact_field_key.is_active == True) & 
								(db.general_contact_field_key.company_id == lFilterData['company_id'])
								).select(
								db.general_contact_field_value.contact_key_id
								)
						lContactIdList=[]
						for row in rows:
							lContactIdList.append(row.contact_key_id)

						lFirstFlag=1
						pass
					elif lFirstFlag==1:
						rows=db(
								(db.general_contact_field.id==db.general_contact_field_value.field_id)&
								(db.general_contact_field_key.id==db.general_contact_field_value.contact_key_id)&
								(db.general_contact_field.field_name == lCondition.split('.')[0]) &
								(eval('db.general_contact_field_value.field_value.'+lCondition.split('.')[1]))&
								(db.general_contact_field_value.contact_key_id.belongs(lContactIdList))
								).select(
								db.general_contact_field_value.contact_key_id
								)
						lContactIdList=[]
						for row in rows:
							lContactIdList.append(row.contact_key_id)
						test=lCompanyIdList
						pass

				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				if len(lFilterData['lFilterOutput']['Deals'])>0: # have deal data
					lList=lFilterData['lFilterOutput']['Deals']
					lFirstFlag=0

					for lCondition in lList:
						if lFirstFlag==0:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
									(db.general_deal_field_key.is_active == True) & 
									(db.general_deal_field_key.company_id == lFilterData['company_id'])
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

							lFirstFlag=1
							pass
						elif lFirstFlag==1:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_value.deal_key_id.belongs(lDealsIdList))
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

							pass
				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				else:	# no deals data
					lDealsIdList=[]
					rows=db((db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
							(db.general_deal_field_key.is_active == True) & 
							(db.general_deal_field_key.company_id == lFilterData['company_id'])
							).select(
							db.general_deal_field_key.id
							)
					for row in rows:
						lDealsIdList.append(row.id)
					pass
				pass
			
			#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
			else: 		# no contact data
				# in this we donot have a filter on the contact data, but we have for the company data
				lContactIdList=[]
				rows=db((db.general_contact_field_key.company_key_id.belongs(lCompanyIdList))&
						(db.general_contact_field_key.is_active == True) & 
						(db.general_contact_field_key.company_id == lFilterData['company_id'])
						).select(
						db.general_contact_field_key.id
						)
				for row in rows:
					lContactIdList.append(row.id)
				pass


				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				if len(lFilterData['lFilterOutput']['Deals'])>0: # have the deals data
					lList=lFilterData['lFilterOutput']['Deals']
					lFirstFlag=0

					for lCondition in lList:
						if lFirstFlag==0:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
									(db.general_deal_field_key.is_active == True) & 
									(db.general_deal_field_key.company_id == lFilterData['company_id'])
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

							lFirstFlag=1
							pass
						elif lFirstFlag==1:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_value.deal_key_id.belongs(lDealsIdList))
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

					pass
				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				else:		# no deals data
					lDealsIdList=[]
					rows=db((db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
							(db.general_deal_field_key.is_active == True) & 
							(db.general_deal_field_key.company_id == lFilterData['company_id'])
							).select(
							db.general_deal_field_key.id
							)
					for row in rows:
						lDealsIdList.append(row.id)
					
					pass
				pass
			
			pass
		
		#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
		else:		# no company data

			#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
			if len(lFilterData['lFilterOutput']['Contact'])>0:	# have contact data

				lList=lFilterData['lFilterOutput']['Contact']
				lFirstFlag=0
				for lCondition in lList:
					if lFirstFlag==0:
						rows=db(
								(db.general_contact_field.id==db.general_contact_field_value.field_id)&
								(db.general_contact_field_key.id==db.general_contact_field_value.contact_key_id)&
								(db.general_contact_field.field_name == lCondition.split('.')[0]) &
								(eval('db.general_contact_field_value.field_value.'+lCondition.split('.')[1]))&
								(db.general_contact_field_key.is_active == True) & 
								(db.general_contact_field_key.company_id == lFilterData['company_id'])
								).select(
								db.general_contact_field_value.contact_key_id
								)
						lContactIdList=[]
						for row in rows:
							lContactIdList.append(row.contact_key_id)

						lFirstFlag=1
						pass
					elif lFirstFlag==1:
						rows=db(
								(db.general_contact_field.id==db.general_contact_field_value.field_id)&
								(db.general_contact_field_key.id==db.general_contact_field_value.contact_key_id)&
								(db.general_contact_field.field_name == lCondition.split('.')[0]) &
								(eval('db.general_contact_field_value.field_value.'+lCondition.split('.')[1]))&
								(db.general_contact_field_value.contact_key_id.belongs(lContactIdList))
								).select(
								db.general_contact_field_value.contact_key_id
								)
						lCompanyIdList=[]
						for row in rows:
							lContactIdList.append(row.contact_key_id)

				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				if len(lFilterData['lFilterOutput']['Deals'])>0: # have deal data
					lList=lFilterData['lFilterOutput']['Deals']
					lFirstFlag=0

					for lCondition in lList:
						if lFirstFlag==0:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
									(db.general_deal_field_key.is_active == True) & 
									(db.general_deal_field_key.company_id == lFilterData['company_id'])
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

							lFirstFlag=1
							pass
						elif lFirstFlag==1:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_value.deal_key_id.belongs(lDealsIdList))
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)
					pass
				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				else:	# no deals data
					lDealsIdList=[]
					rows=db((db.general_deal_field_key.contact_key_id.belongs(lContactIdList))&
							(db.general_deal_field_key.is_active == True) & 
							(db.general_deal_field_key.company_id == lFilterData['company_id'])
							).select(
							db.general_deal_field_key.id
							)
					for row in rows:
						lDealsIdList.append(row.id)
					pass
				pass
			#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
			else: 		# no contact data
				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞
				if len(lFilterData['lFilterOutput']['Deals'])>0:		# have the deals data
					lList=lFilterData['lFilterOutput']['Deals']
					lFirstFlag=0

					for lCondition in lList:
						if lFirstFlag==0:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_key.is_active == True) & 
									(db.general_deal_field_key.company_id == lFilterData['company_id'])
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

							lFirstFlag=1
							pass
						elif lFirstFlag==1:
							rows=db(
									(db.general_deal_field.id==db.general_deal_field_value.field_id)&
									(db.general_deal_field_key.id==db.general_deal_field_value.deal_key_id)&
									(db.general_deal_field.field_name == lCondition.split('.')[0]) &
									(eval('db.general_deal_field_value.field_value.'+lCondition.split('.')[1]))&
									(db.general_deal_field_value.deal_key_id.belongs(lDealsIdList))
									).select(
									db.general_deal_field_value.deal_key_id
									)
							lDealsIdList=[]
							for row in rows:
								lDealsIdList.append(row.deal_key_id)

					pass
				#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞	
				else:		# no deals data
					# this condition is not posible as there is no filters, but still for safety
					rows=db((db.general_deal_field_key.is_active == True) & 
							(db.general_deal_field_key.company_id == lFilterData['company_id'])
							).select(
							db.general_deal_field_key.id,
							orderby=~db.general_deal_field_key.id
							)
					lDealsIdList=[]
					for row in rows:
						lDealsIdList.append(row.deal_key_id)
					
				pass

			pass

		# END #
		#∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞	
		i=0

		for  key in sorted(lDealsIdList):
			
			deal_data = db(
				(db.general_deal_field_key.id == db.general_deal_field_value.deal_key_id) & 
				(db.general_deal_field_value.field_id == db.general_deal_field.id) & 
				(db.general_deal_field_value.is_active == True) & 
				(db.general_deal_field_value.company_id == lFilterData['company_id']) & 
				(db.general_deal_field_key.id == key)
				).select(
				db.general_deal_field.field_name, 
				db.general_deal_field_value.field_value
				).as_dict(key='general_deal_field.field_name')
			
			contact_data = db(
				(db.general_deal_field_key.contact_key_id == db.general_contact_field_value.contact_key_id) & 
				(db.general_contact_field_value.field_id == db.general_contact_field.id) & 
				(db.general_deal_field_key.id == key) & 
				(db.general_contact_field_value.is_active == True) & 
				(db.general_contact_field_value.company_id == lFilterData['company_id'])
				).select(
				db.general_contact_field.field_name, 
				db.general_contact_field_value.field_value
				).as_dict(key='general_contact_field.field_name')

			company_data = db((db.general_deal_field_key.contact_key_id == db.general_contact_field_key.id) & (db.general_contact_field_key.company_key_id == db.general_contact_company_field_value.company_key_id) & (db.general_contact_company_field_value.field_id == db.general_contact_company_field.id) & (db.general_contact_company_field_value.is_active == True) & (db.general_deal_field_key.id == key) & (db.general_contact_company_field_value.company_id == lFilterData['company_id'])).select(db.general_contact_company_field.field_name, db.general_contact_company_field_value.field_value).as_dict(key='general_contact_company_field.field_name')
			
			deal_status = db((db.general_deal_status.deal_key_id == key) & (db.general_deal_status.is_active == True) & (db.general_deal_status.deal_status_master_id == db.general_deal_status_master.id)).select(db.general_deal_status.deal_key_id,db.general_deal_status_master.deal_status, orderby=~db.general_deal_status.db_entry_time,limitby=(0,1)).as_dict(key='general_deal_status.deal_key_id')
		
			data[str(i)]={
				'Company': 'NA' if not company_data else company_data['company_name']['general_contact_company_field_value']['field_value'],
				'Name':str(contact_data['first_name']['general_contact_field_value']['field_value'])+' '+str(contact_data['last_name']['general_contact_field_value']['field_value']),
				'Email':str(contact_data['email_id']['general_contact_field_value']['field_value']),
				'Phone':'NA' if not company_data else str(company_data['phone_no']['general_contact_company_field_value']['field_value']),
				'Deals Source':deal_data['deal_source']['general_deal_field_value']['field_value'],
				'Description':deal_data['description']['general_deal_field_value']['field_value'],
				'Status':'NA' if not deal_status else deal_status[key]['general_deal_status_master']['deal_status'],
				'deal_key_id':str(key)
			}
			# enter the extra requested data
			for key in lFieldList:
				data[str(i)][key]=eval(lFieldList[key])
				pass
			i+=1
			data_flag=1			
			pass
		
		if len(data)==0:
			data['0']={
				'Company': '',
				'Name':'',
				'Email':'',
				'Phone':'',
				'Deals Source':'',
				'Description':'',
				'Status':'',
				'deal_key_id':''
			}
			data_flag=0


		return dict(filter_field=lFilterField,data=data,data_flag=data_flag)

	except Exception as e:
		return 'Exception Raised : '+str(e)
	# else:
	# 	return locals()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$-- Deal Addition --$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#---------------------------- Deal addition form fields ---------------------------------------
def deal_add_ff():
	field_names={'field':'value'}
	rows = db(db.general_deal_field.is_active==True).select(orderby=db.general_deal_field.sequence_no)
	lList=[]
	for row in rows:
		lList=[row.field_widget_attributes,row.field_requires_attributes]

		field_names.update({row.field_name:lList})

	# IS_IN_SET({1:"Reference"},zero="Type of contact")
	lList={}		# a dict to store the options of the deals status
	lListValues=db(db.general_deal_status_master).select(db.general_deal_status_master.deal_status,db.general_deal_status_master.id).as_dict(key='id')
	# for lListValue in lListValues:
	# 	lList[str(lListValue.id)]= lListValue.deal_status
	
	for key in sorted(lListValues.keys()):
		lList[str(key)]=lListValues[key]['deal_status']


	field_names['deal_status'][1]="IS_IN_SET("+str(lList)+",zero='Deal Status')"

	del field_names['field']
	return dict(field_names)
	pass

# -------------- Deal addition function --------------------------------------------------------
def add_deal(data,lForm):
	
	done=0
	lReturnDict={'lKeyId':0,'msg':''}
	
	# have to enter the data into the key table first
	try:
		lKeyId=db.general_deal_field_key.insert(
				contact_key_id=data['data']['contact_key_id'],
				company_id=data['data']['company_id'] ,
				db_entry_time=lambda:datetime.now(),
				db_entered_by=data['data']['user_id'],
				session_id=data['data']['session_id']
			)
		lReturnDict['lKeyId']=int(lKeyId)
	except Exception as e:
		lReturnDict['msg']='error in adding Deal key (%s)' %e
		return lReturnDict
	else:
		
		try:
			rows=db(db.general_deal_field.field_name != None).select()
			for row in rows:
				if row.is_active== True: # and (row.field_name != 'final_quotation' and row.field_name != 'final_contract'):		
					db.general_deal_field_value.insert(
						field_id=row.id ,
						deal_key_id=lKeyId ,
						field_value=data['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id'],
						company_id=data['data']['company_id'],
						session_id=data['data']['session_id']
						)
				# elif row.is_active== True and (row.field_name == 'final_quotation' or row.field_name == 'final_contract')
				pass
			pass
		except Exception as e:
			lReturnDict['msg']=  'error in adding Deal data (%s) ' %e
			return lReturnDict

		else:
			# have to update the status also
			try:
				lStatusId=db.general_deal_status.insert(
				activity='Deal Created',
				session_id=data['data']['session_id'],
				company_id=data['data']['company_id'],
				deal_key_id=lKeyId,
				deal_status_master_id=data['data']['deal_status'],				#db(db.general_deal_status_master.deal_status=='Initiated').select()[0].id,
				db_entry_time=lambda:datetime.now(),
				db_entered_by=data['data']['user_id']
				)

			except Exception as e:
				lReturnDict['msg']= 'error in add the Deal status as  %s '%e
				return lReturnDict
			else:
				if len(data['data']['description'])>0:
					# the user have a description than add it to the notes as a update to that deal
					try:
						db.general_deal_updates.insert(
							session_id=data['data']['session_id'],
							company_id=data['data']['company_id'],
							deal_key_id=lKeyId,
							deal_status_id=data['data']['deal_status'],
							update_head='notes',
							update_data=data['data']['description'],
							db_entry_time=lambda:datetime.now(),
							db_entered_by=data['data']['user_id'],
							db_entered_by_name=data['data']['name']
							)
					except Exception as e:
						lReturnDict['msg']= 'error in adding the Deal update data %s' %e
						return lReturnDict
					pass
				
				if type(lForm.vars.final_contract) != bytes:
					# all the files related to the deal will be inserted into the deals update db
					try:
						lStorageContractFile = db.general_deal_updates.update_file.store(lForm.vars.final_contract.file, lForm.vars.final_contract.filename)
						lContractId = db.general_deal_updates.insert(
							session_id=data['data']['session_id'],
							company_id=data['data']['company_id'],
							deal_key_id=lKeyId,
							deal_status_id=data['data']['deal_status'],
							update_head='final_contract',
							update_file_name=lForm.vars.final_contract.filename,
							update_file=lStorageContractFile,
							# update_data=data['data']['description'],
							head_version=0,
							head_id=0,
							db_entry_time=lambda:datetime.now(),
							db_entered_by=data['data']['user_id'],
							db_entered_by_name=data['data']['name']
							)
					except Exception as e:
						lReturnDict['msg']= 'error in adding the Deal update data ' + str(e)
						return lReturnDict
					else:
						try:
							lFieldId = db(db.general_deal_field.field_name == 'final_contract').select(db.general_deal_field.id)[0].id
							db((db.general_deal_field_value.deal_key_id == lKeyId) &
								(db.general_deal_field_value.field_id == lFieldId)
							).update(field_value = lContractId)
							pass
						except Exception as e:
							lReturnDict['msg']= 'error in updating the Deal data %s' %e
							return lReturnDict
						pass
					pass
				
				if type(lForm.vars.final_quotation) != bytes:
					# all the files related to the deal will be inserted into the deals update db
					try:
						lStorageQuotationFile = db.general_deal_updates.update_file.store(lForm.vars.final_quotation.file, lForm.vars.final_quotation.filename)
						lQuotationId = db.general_deal_updates.insert(
							session_id=data['data']['session_id'],
							company_id=data['data']['company_id'],
							deal_key_id=lKeyId,
							deal_status_id=data['data']['deal_status'],
							update_head='final_quotation',
							update_file_name=lForm.vars.final_quotation.filename,
							update_file=lStorageQuotationFile,
							head_version=0,
							head_id=0,
							db_entry_time=lambda:datetime.now(),
							db_entered_by=data['data']['user_id'],
							db_entered_by_name=data['data']['name']
							)
					except Exception as e:
						lReturnDict['msg']= 'error in adding the Deal update data %s' %e
						return lReturnDict
					else:
						try:
							lFieldId = db(db.general_deal_field.field_name == 'final_quotation').select(db.general_deal_field.id)[0].id
							db((db.general_deal_field_value.deal_key_id == lKeyId) &
								(db.general_deal_field_value.field_id == lFieldId)
							).update(field_value = lQuotationId)
							pass
						except Exception as e:
							lReturnDict['msg']= 'error in updating the Deal data %s' %e
							return lReturnDict
						pass

					pass
				done=1
				pass


	if done==1:
		lReturnDict['msg']=' Deals done '
		return lReturnDict


# -------------- Form Addition Function --------------------------------------------------------

def add():
	if session_check():
		done=0
		#------------------------------------------------- session is active, make the connection to api
		contactserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Contacts','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyserver=xmlrpclib.ServerProxy(link+str(URL('ERP','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		contactCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Contact','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of contact
		companyCRMServer=xmlrpclib.ServerProxy(link+str(URL('CRM','Company','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of company
		
		fields=[] 		# a simple list to store the form fields
		deal_form_fields=deal_add_ff()
		contact_form_fields=contactserver.contact_add_ff()
		company_form_fields=companyserver.company_add_ff()		

		#------------------------------------------------- add the form fields of deals into the list
		for key in sorted(deal_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if deal_form_fields[key][0]:
				widget=eval(deal_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			
			if deal_form_fields[key][1]:
				requires=eval(deal_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(key,widget=widget, requires=requires))

		#------------------------------------------------- add the fields of contact form
		# add the form fields of the contacts
		for key in sorted(contact_form_fields.keys()):			# take key one by one in a sequence and make the field list
			name=key
			if contact_form_fields[key][0]:
				widget=eval(contact_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if contact_form_fields[key][1]:
				requires=eval(contact_form_fields[key][1])

				# if 'IS_IN_SET' in contact_form_fields[key][1]:
				# 	name= str(key)+'*'
			else:
				requires=[] 		# it is a list and can be empty		
			fields.append(Field(name,widget=widget, requires=requires))

		#------------------------------------------------- now add the form fields of company form
		# # add the form fields of the company
		for key in sorted(company_form_fields.keys()):			# take key one by one in a sequence and make the field list
			if company_form_fields[key][0]:
				widget=eval(company_form_fields[key][0])
			else:
				widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
			if company_form_fields[key][1]:
				requires=eval(company_form_fields[key][1])
			else:
				requires=[] 		# it is a list and can be empty
			fields.append(Field(key,widget=widget, requires=requires))

		#------------------------------------------------- make the sql form using the pointer to the list of fields
		fields.append(Field('company_key_id','string'))
		fields.append(Field('contact_key_id','string'))
		lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory

		#------------------------------------------------- add the place holder using the same dictionary
		for key in deal_form_fields.keys():
			place=''
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in deal_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			elif 'options' in deal_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			# else:
			# 	place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
			# 	pass
			
			if 'IS_IN_SET' in deal_form_fields[key][1] or 'IS_NOT_EMPTY' in deal_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass
			deal_form_fields[key]=s						
			exec(place)
			exec(require)

		#-------------------------------------------------
		for key in contact_form_fields.keys():
			place=''
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in contact_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			elif 'options' in contact_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			# else:
			# 	place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
			# 	pass

			if 'IS_IN_SET' in contact_form_fields[key][1] or 'IS_NOT_EMPTY' in contact_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass

			contact_form_fields[key]=s						
			exec(place)
			exec(require)

		#-------------------------------------------------
		for key in company_form_fields.keys():
			place=''
			if '_' in key:
				s= key.replace('_',' ')
				s=s.title()
			else:
				s= key
				s=s.title()
			if 'text' in company_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
				pass
			elif 'options' in company_form_fields[key][0]:
				place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
				pass
			# else:
			# 	place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
			# 	pass
			if 'IS_IN_SET' in company_form_fields[key][1] or 'IS_NOT_EMPTY' in company_form_fields[key][1]:
				require='lForm.custom.widget.'+str(key)+'["_required"]= " "'
				pass

			company_form_fields[key]=s			
			exec(place)
			exec(require)

		if lForm.process().accepted:
			company_key_id=int(request.vars.company_key_id)
			contact_key_id=int(request.vars.contact_key_id)
			#------------------------------------------------- contact and company is already in the db and we have the key ids of them
			if company_key_id != 0 and contact_key_id !=0: # only new deals
				
				for key in deal_form_fields.keys(): # update the entered data
					deal_form_fields[key]=eval('lForm.vars.'+key)

				deal_form_fields['contact_key_id']=contact_key_id		# add the extra data
				deal_form_fields['user_id']=session.user_id
				deal_form_fields['name']=session.name
				deal_form_fields['company_id']=session.company_id
				deal_form_fields['session_id']=session.session_id
				
				# return locals()
				try:    
					
					lResponseDict= add_deal(dict(data=deal_form_fields),lForm) 		# send the dictioinary to the server
					session.message+= str(lResponseDict['msg'])							

				except Exception as e:
					session.message=" error while adding deal details (%s)" %e
					session.flash=" error while adding deal details (%s)" %e
				else:
					done=1
					pass

				session.flash='condition 1'+" "+str(company_key_id) +" "+str(type(company_key_id))
				pass
			#------------------------------------------------- have the company key id and new data in contact and its new deal

			elif company_key_id != 0 and contact_key_id ==0: # contant and deals
				session.message=''
				for key in contact_form_fields.keys(): # update the entered data
					contact_form_fields[key]=eval('lForm.vars.'+key)
				
				contact_form_fields['company_key_id']=company_key_id		# add the extra data
				contact_form_fields['user_id']=session.user_id
				contact_form_fields['company_id']=session.company_id
				contact_form_fields['session_id']=session.session_id

				try:    
					lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
					contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 

					lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictionary to the ERP server
					# contact_form_fields['contact_key_id']=lResponseDict['lKeyId']						
					# lResponseErpDict = add_erp_contact(dict(data=contact_form_fields))

					contact_key_id= lResponseDict['lKeyId']
					
					# session.message+= str(lResponseDict['msg'])
					
				except Exception as e:
					session.message+=" error while adding contact details (%s)" %e
					session.flash=" error while adding conatact details (%s)" %e
				else:

					for key in deal_form_fields.keys(): # update the entered data
						deal_form_fields[key]=eval('lForm.vars.'+key)

					deal_form_fields['contact_key_id']=contact_key_id		# add the extra data
					deal_form_fields['user_id']=session.user_id
					deal_form_fields['deal_key_id']=session.name
					deal_form_fields['company_id']=session.company_id
					deal_form_fields['session_id']=session.session_id
					if 'FieldStorage' in str(type( deal_form_fields['final_quotation'])):
						deal_form_fields['final_quotation_filename']=lForm.vars.final_quotation.filename
					if 'FieldStorage' in str(type( deal_form_fields['final_contract'])):
						deal_form_fields['final_contract_filename']=lForm.vars.final_contract.filename

					try:    
					
						lResponseDict= add_deal(dict(data=deal_form_fields),lForm) 		# send the dictioinary to the server
						# session.message+= str(lResponseDict['msg'])							

					except Exception as e:
						session.message=" error while adding deal details (%s)" %e
						session.flash=" error while adding deal details (%s)" %e
					else:
						done=1
						pass

					pass
				session.flash='condition 2'
				pass
			#------------------------------------------------- whole data is new

			elif company_key_id == 0 and contact_key_id ==0: #	all
				
				session.message=""
				for key in company_form_fields.keys(): # update the entered data
					company_form_fields[key]=str(eval('lForm.vars.'+key))
				
				company_form_fields['user_id']=session.user_id
				company_form_fields['company_id']=session.company_id
				company_form_fields['session_id']=session.session_id
				lResponseDict={}
				
				try:    						
					lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
					company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
					
					lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server

					company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
					session.message+= str(lResponseDict['msg'])

				except Exception as e:
					session.message+=" error while adding company details (%s)" %e 
					session.flash=" error while adding company details (%s)" %e
					return e		
				else:	# now for the contact
					
					for key in contact_form_fields.keys(): # update the entered data
						contact_form_fields[key]=eval('lForm.vars.'+key)
					contact_form_fields['company_key_id']=company_key_id		# add the extra data
					contact_form_fields['user_id']=session.user_id
					contact_form_fields['company_id']=session.company_id
					contact_form_fields['session_id']=session.session_id

					try:    
						lResponseCRMDict= contactCRMServer.add_contact(dict(data=contact_form_fields)) # send the dictionary to the CRM server
						contact_form_fields['contact_key_id']=lResponseCRMDict['lKeyId'] 

						lResponseDict= contactserver.add_contact(dict(data=contact_form_fields)) 		# send the dictioinary to the server
						
						contact_key_id= lResponseDict['lKeyId']
						# session.message+= str(lResponseDict['msg'])
						
					except Exception as e:
						# session.message=str(lResponseDict['msg'])
						session.message+=" error while adding contact details (%s)" %e
						session.flash=" error while adding conatact details (%s)" %e
						return e
					else:

						for key in deal_form_fields.keys(): # update the entered data
							deal_form_fields[key]=eval('lForm.vars.'+key)

						deal_form_fields['contact_key_id']=contact_key_id		# add the extra data
						deal_form_fields['user_id']=session.user_id
						deal_form_fields['deal_key_id']=session.name
						deal_form_fields['company_id']=session.company_id
						deal_form_fields['session_id']=session.session_id
						if 'FieldStorage' in str(type( deal_form_fields['final_quotation'])):
							deal_form_fields['final_quotation_filename']=lForm.vars.final_quotation.filename
						if 'FieldStorage' in str(type( deal_form_fields['final_contract'])):
							deal_form_fields['final_contract_filename']=lForm.vars.final_contract.filename

						try:    
						
							lResponseDict= add_deal(dict(data=deal_form_fields),lForm) 		# send the dictioinary to the server
							session.message+= str(lResponseDict['msg'])							

						except Exception as e:
							session.message=" error while adding deal details (%s)" %e
							session.flash=" error while adding deal details (%s)" %e
							return e
						else:
							done=1
							pass

						pass

					pass
				session.flash='condition 3'
				pass

			#------------------------------------------------- contact was present but have to add the company and update the details of the contact
			
			elif company_key_id==0 and contact_key_id !=0: 
				 
				if len(lForm.vars.company_name)>0:

					# have to add the company and update the company_key_id
					session.message=""
					
					for key in company_form_fields.keys(): # update the entered data
						company_form_fields[key]=str(eval('lForm.vars.'+key))
					
					company_form_fields['user_id']=session.user_id
					company_form_fields['company_id']=session.company_id
					company_form_fields['session_id']=session.session_id
					lResponseDict={}
					
					try:    						
						lResponseCRMDict = companyCRMServer.add_company(dict(data=company_form_fields))
						company_form_fields['company_key_id'] = lResponseCRMDict['lKeyId']
						
						lResponseDict= companyserver.add_company(dict(data=company_form_fields)) 		# send the dictioinary to the server
						company_key_id= lResponseDict['lKeyId'] 	# the new id from the api
						# session.message+= str(lResponseDict['msg'])

					except Exception as e:
						session.message+=" error while adding company details (%s)" %e 
						session.flash=" error while adding company details (%s)" %e
									
					else:	# now for the contact
						
						contact_form_fields['contact_key_id']=contact_key_id		# add the extra data
						contact_form_fields['company_key_id']=company_key_id		# add the extra data
						contact_form_fields['user_id']=session.user_id
						contact_form_fields['company_id']=session.company_id

						try:    
							lResponseDict= contactserver.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the ERP server
							lResponseCRMDict= contactCRMServer.add_contact_company_key_id(dict(data=contact_form_fields)) 		# send the dictioinary to the CRM server
							
							# session.message+= str(lResponseDict['msg'])
							
						except Exception as e:
							session.message+=" error while adding contact details (%s)" %e
							session.flash=" error while adding conatact details (%s)" %e
						else:

							for key in deal_form_fields.keys(): # update the entered data
								deal_form_fields[key]=eval('lForm.vars.'+key)

							deal_form_fields['contact_key_id']=contact_key_id		# add the extra data
							deal_form_fields['user_id']=session.user_id
							deal_form_fields['name']=session.name
							deal_form_fields['company_id']=session.company_id
							deal_form_fields['session_id']=session.session_id
							if 'FieldStorage' in str(type( deal_form_fields['final_quotation'])):
								deal_form_fields['final_quotation_filename']=lForm.vars.final_quotation.filename
							if 'FieldStorage' in str(type( deal_form_fields['final_contract'])):
								deal_form_fields['final_contract_filename']=lForm.vars.final_contract.filename

							try:    
							
								lResponseDict= add_deal(dict(data=deal_form_fields),lForm) 		# send the dictioinary to the server
								# session.message+= str(lResponseDict['msg'])							

							except Exception as e:
								session.message=" error while adding deal details (%s)" %e
								session.flash=" error while adding deal details (%s)" %e
							else:
								done=1
								pass

							pass

						pass


					session.flash='condition 41'
				
				else:
					# only deals
					for key in deal_form_fields.keys(): # update the entered data
						deal_form_fields[key]=eval('lForm.vars.'+key)

					deal_form_fields['contact_key_id']=contact_key_id		# add the extra data
					deal_form_fields['user_id']=session.user_id
					deal_form_fields['name']=session.name
					deal_form_fields['company_id']=session.company_id
					deal_form_fields['session_id']=session.session_id
					if 'FieldStorage' in str(type( deal_form_fields['final_quotation'])):
						deal_form_fields['final_quotation_filename']=lForm.vars.final_quotation.filename
					if 'FieldStorage' in str(type( deal_form_fields['final_contract'])):
						deal_form_fields['final_contract_filename']=lForm.vars.final_contract.filename

					try:    
						lResponseDict= add_deal(dict(data=deal_form_fields),lForm) 		# send the dictioinary to the server
						# session.message+= str(lResponseDict['msg'])							

					except Exception as e:
						session.message=" error while adding deal details (%s)" %e
						session.flash=" error while adding deal details (%s)" %e
					else:
						done=1
						pass


						session.flash='condition 42'						
					pass
			if done ==1:
				redirect(URL('view'))
				pass
			pass
		pass
	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

	return dict(form=lForm,deal_form_fields=deal_form_fields,contact_form_fields=contact_form_fields,company_form_fields=company_form_fields)
	pass

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Deal Edit $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def deal_edit_ff(deal_key_id):
	# deal_key_id=16
	field_names={'field':'value'}
	rows = db(db.general_deal_field_value.field_id == db.general_deal_field.id)(db.general_deal_field_value.deal_key_id == deal_key_id).select(
		db.general_deal_field_value.field_value,
		db.general_deal_field.field_widget_attributes,
		db.general_deal_field.field_requires_attributes,
		db.general_deal_field.field_name
		)
	lList=[]
	for row in rows:

		lList=[row.general_deal_field.field_widget_attributes,row.general_deal_field.field_requires_attributes,row.general_deal_field_value.field_value]

		field_names.update({row.general_deal_field.field_name:lList})

	# IS_IN_SET({1:"Reference"},zero="Type of contact")
	lList={}		# a dict to store the options of the deals status
	lListValues=db(db.general_deal_status_master).select(db.general_deal_status_master.deal_status,db.general_deal_status_master.id).as_dict(key='id')
	# for lListValue in lListValues:
	# 	lList[str(lListValue.id)]= lListValue.deal_status
	
	for key in sorted(lListValues.keys()):
		lList[str(key)]=lListValues[key]['deal_status']


	field_names['deal_status'][1]="IS_IN_SET("+str(lList)+",zero='Deal Status')"

	del field_names['field']
	return dict(field_names)
	pass

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Deal Edit $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def edit():
	# this page is only to edit the deals details 
	# if the user wants to edit the contact details he will be redirected to that page from deals update page
	if session_check():
		if len(request.args)>0:
			done=0
			deal_key_id= request.args[0]
			# deal_key_id= 16

			#------------------------------------------------- session is active, make the connection to api		
			
			deal_form_fields=deal_edit_ff(deal_key_id)			# ask for the list of the field to make the form and store it into a dict
			
			fields=[] 		# a simple list to store the form fields
			#------------------------------------------------- add the form fields of deals into the list
			for key in sorted(deal_form_fields.keys()):			# take key one by one in a sequence and make the field list
				if deal_form_fields[key][0]:
					widget=eval(deal_form_fields[key][0])
				else:
					widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
				
				if deal_form_fields[key][1]:
					requires=eval(deal_form_fields[key][1])
				else:
					requires=[] 		# it is a list and can be empty	

				fields.append(Field(key,widget=widget, requires=requires, default=deal_form_fields[key][2]))


		
			#------------------------------------------------- make the sql form using the pointer to the list of fields

			lForm= SQLFORM.factory(*fields)			# make the sql form using the form factory
			#------------------------------------------------- add the place holder using the same dictionary
			for key in deal_form_fields.keys():
				place=''
				if '_' in key:
					s= key.replace('_',' ')
					s=s.title()
				else:
					s= key
					s=s.title()
				if 'text' in deal_form_fields[key][0]:
					place='lForm.custom.widget.'+str(key)+'.update(_class=\'materialize-textarea\')'+"\n"
					pass
				elif 'options' in deal_form_fields[key][0]:
					place='lForm.custom.widget.'+str(key)+'.update(_class=\'validate\')'+"\n"
					pass
				#place='lForm.custom.widget.'+str(key)+'.update(_placeholder=\''+s+'\')'+"\n"
				deal_form_fields[key]=s						
				exec(place)

			lForm.custom.widget.deal_status['_required']=''
			lForm.custom.widget.deal_source['_required']=''
			lForm.custom.widget.deal_owner['_required']=''



			if lForm.process().accepted:
				
				session.message=''					
				for key in deal_form_fields.keys(): # update the entered data
					deal_form_fields[key]=eval('lForm.vars.'+key)
				
				deal_form_fields['deal_key_id']=deal_key_id		# add the extra data, take the deal id to specify the update
				deal_form_fields['user_id']=session.user_id
				deal_form_fields['name']=session.name
				deal_form_fields['session_id']=session.session_id
				deal_form_fields['company_id']=session.session_id

				try:    
					lResponseDict= dealserver.edit_deals(dict(data=deal_form_fields)) 		# send the dictioinary to the server
					session.message+= str(lResponseDict['msg'])							

				except Exception as e:
					session.message=" error while editing deals details (%s)" %e
					session.flash=" error while editing deals details (%s)" %e
				else:
					done=1
					pass
				if done==1:
					redirect(URL('deals_update',args=[deal_key_id]))
				pass
			return dict(form=lForm,deal_form_fields=deal_form_fields)

		else:
			redirect(URL('deals'))
			session.flash="select a Deal to edit"

	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Leads to Deal $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def lead_to_deal():
	data={}
	data['data']= eval(dict(request.vars)['data'])
	upload_form = FORM(
		INPUT(_name='description',_type='text'),
		INPUT(_name='final_contract',_type='file'),
		INPUT(_name='final_quotation',_type='file'),
		INPUT(_name='final_price',_type='string'),
		)


	if upload_form.accepts(request.vars,formname='upload_form'):
		# strore the form data into the dict for processing
		data['data']['description']=upload_form.vars.description
		data['data']['final_price']=upload_form.vars.final_price
		data['data']['final_contract']=upload_form.vars.final_contract
		data['data']['final_quotation']=upload_form.vars.final_quotation
		# store the new deal
		if type(upload_form.vars.final_contract) != bytes and type(upload_form.vars.final_quotation) != bytes:
			done=0

			# have to enter the data into the key table first
			try:
				lKeyId=db.general_deal_field_key.insert(
						contact_key_id=data['data']['contact_key_id'],
						lead_key_id=data['data']['lead_key_id'],
						company_id=data['data']['company_id'] ,
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id'],
						session_id=data['data']['session_id']
					)
			except Exception as e:
				session.message='error in adding Deal key (%s)' %e
				return e
			else:
				# enter the data into the deals data
				try:
					rows=db(db.general_deal_field.field_name != None).select()
					for row in rows:
						if row.is_active== True: # and (row.field_name != 'final_quotation' and row.field_name != 'final_contract'):		
							db.general_deal_field_value.insert(
								field_id=row.id ,
								deal_key_id=lKeyId ,
								field_value=data['data'][row.field_name] ,  # to insert the data take the respective data from the dictionary
								db_entry_time=lambda:datetime.now(),
								db_entered_by=data['data']['user_id'],
								company_id=data['data']['company_id'],
								session_id=data['data']['session_id']
								)
						# elif row.is_active== True and (row.field_name == 'final_quotation' or row.field_name == 'final_contract')
						pass
					pass
				except Exception as e:
					session.message=  'error in adding Deal data (%s) ' %e
					return e

				else:
					# have to update the status also
					try:
						lStatusId=db.general_deal_status.insert(
						activity='Deal Created From Lead',
						session_id=data['data']['session_id'],
						company_id=data['data']['company_id'],
						deal_key_id=lKeyId,
						deal_status_master_id=data['data']['deal_status'],				#db(db.general_deal_status_master.deal_status=='Initiated').select()[0].id,
						db_entry_time=lambda:datetime.now(),
						db_entered_by=data['data']['user_id']
						)

					except Exception as e:
						session.message= 'error in add the Deal status as  %s '%e
						return e
					else:
						# section to insert the data into the deal update table
						if len(data['data']['description'])>0:
							# the user have a description than add it to the notes as a update to that deal
							try:
								db.general_deal_updates.insert(
									session_id=data['data']['session_id'],
									company_id=data['data']['company_id'],
									deal_key_id=lKeyId,
									deal_status_id=data['data']['deal_status'],
									update_head='notes',
									update_data=data['data']['description'],
									db_entry_time=lambda:datetime.now(),
									db_entered_by=data['data']['user_id'],
									db_entered_by_name=data['data']['user_name']
									)
							except Exception as e:
								session.message= 'error in adding the Deal update data %s' %e
								return e
							pass
						
						if type(upload_form.vars.final_contract) != bytes:
							# all the files related to the deal will be inserted into the deals update db
							try:
								lStorageContractFile = db.general_deal_updates.update_file.store(upload_form.vars.final_contract.file, upload_form.vars.final_contract.filename)
								lContractId = db.general_deal_updates.insert(
									session_id=data['data']['session_id'],
									company_id=data['data']['company_id'],
									deal_key_id=lKeyId,
									deal_status_id=data['data']['deal_status'],
									update_head='final_contract',
									update_file_name=upload_form.vars.final_contract.filename,
									update_file=lStorageContractFile,
									# update_data=data['data']['description'],
									head_version=0,
									head_id=0,
									db_entry_time=lambda:datetime.now(),
									db_entered_by=data['data']['user_id'],
									db_entered_by_name=data['data']['user_name']
									)
							except Exception as e:
								session.message= 'error in adding the Deal update data ' + str(e)
								return e
							else:
								try:
									lFieldId = db(db.general_deal_field.field_name == 'final_contract').select(db.general_deal_field.id)[0].id
									db((db.general_deal_field_value.deal_key_id == lKeyId) &
										(db.general_deal_field_value.field_id == lFieldId)
									).update(field_value = lContractId)
									pass
								except Exception as e:
									session.message= 'error in updating the Deal data %s' %e
									return e
								pass
							pass
						
						if type(upload_form.vars.final_quotation) != bytes:
							# all the files related to the deal will be inserted into the deals update db
							try:
								lStorageQuotationFile = db.general_deal_updates.update_file.store(upload_form.vars.final_quotation.file, upload_form.vars.final_quotation.filename)
								lQuotationId = db.general_deal_updates.insert(
									session_id=data['data']['session_id'],
									company_id=data['data']['company_id'],
									deal_key_id=lKeyId,
									deal_status_id=data['data']['deal_status'],
									update_head='final_quotation',
									update_file_name=upload_form.vars.final_quotation.filename,
									update_file=lStorageQuotationFile,
									head_version=0,
									head_id=0,
									db_entry_time=lambda:datetime.now(),
									db_entered_by=data['data']['user_id'],
									db_entered_by_name=data['data']['user_name']
									)
							except Exception as e:
								session.message= 'error in adding the Deal update data %s' %e
								return e
							else:
								try:
									lFieldId = db(db.general_deal_field.field_name == 'final_quotation').select(db.general_deal_field.id)[0].id
									db((db.general_deal_field_value.deal_key_id == lKeyId) &
										(db.general_deal_field_value.field_id == lFieldId)
									).update(field_value = lQuotationId)
									pass
								except Exception as e:
									session.message= 'error in updating the Deal data %s' %e
									return e
								pass

							pass
						done=1
						pass


			if done==1:
				session.message=' Deals done '
				
		
		else:
			return 'File was not uploaded properly'

		# update the status of the lead also
		server = xmlrpclib.ServerProxy(link+str(URL('CRM','Leads','call/xmlrpc')),allow_none=True,context=context)	# make the connection to the api server of lead

		lRequestData={
		'request_type': 'add',		# get and add
		'lead_key_id': data['data']['lead_key_id'],
		'user_id': data['data']['user_id'],				##############
		'company_id':data['data']['company_id'],		##############
		'session_id':data['data']['session_id'],		##############
		'response':0,
		'activity':'Lead Converted',
		'lead_status_master_id':11,
		'current_stage':2,
		'db_entered_by':data['data']['user_id'],
		'db_entered_by_name':data['data']['user_name']
		}

		lLeadsList= server.add_lead_status_details(dict(data=lRequestData))

		redirect(URL('Deals','view',extension=False),client_side=True)
		
	return locals()


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def fetch_deal_basic_details(lRequestData):
	
	# lRequestData={
	# 	'deal_key_id':22,
	# 	'user_id': 2,
	# 	'company_id':25,
	# 	'update_head': "notes"
	# }


	data = {}
	data['deal_details'] = db(
		(db.general_deal_field_key.id == db.general_deal_field_value.deal_key_id) & 
		(db.general_deal_field_value.field_id == db.general_deal_field.id) & 
		(db.general_deal_field_value.is_active == True) & 
		(db.general_deal_field_value.company_id == lRequestData['company_id']) & 
		(db.general_deal_field_key.id == lRequestData['deal_key_id'])
		).select(
		db.general_deal_field.field_name, 
		db.general_deal_field_value.field_value
		).as_list()

	data['contact_details'] = db(
		(db.general_deal_field_key.contact_key_id == db.general_contact_field_value.contact_key_id) & 
		(db.general_contact_field_value.field_id == db.general_contact_field.id) & 
		(db.general_deal_field_key.id == lRequestData['deal_key_id']) & 
		(db.general_contact_field_value.is_active == True) & 
		(db.general_contact_field_value.company_id == lRequestData['company_id'])
		).select(
		db.general_contact_field.field_name, 
		db.general_contact_field_value.field_value
		).as_list()

	data['company_details'] = db(
		(db.general_deal_field_key.contact_key_id == db.general_contact_field_key.id) & 
		(db.general_contact_field_key.company_key_id == db.general_contact_company_field_value.company_key_id) & 
		(db.general_contact_company_field_value.field_id == db.general_contact_company_field.id) & 
		(db.general_contact_company_field_value.is_active == True) & 
		(db.general_deal_field_key.id == lRequestData['deal_key_id']) & 
		(db.general_contact_company_field_value.company_id == lRequestData['company_id'])
		).select(
		db.general_contact_company_field.field_name, 
		db.general_contact_company_field_value.field_value
		).as_list()
	

	deal_status=db(db.general_deal_status_master.id==int(data['deal_details'][1]['general_deal_field_value']['field_value'])
		).select(db.general_deal_status_master.deal_status)

	data['deal_details'][1]['general_deal_field_value']['field_value']=deal_status[0].deal_status+'.'+data['deal_details'][1]['general_deal_field_value']['field_value']
	
	# make a basic default dictionary for the contact donot have the comapny details
	if len(data['company_details'])<=0:
		data['company_details']=[
		{'general_contact_company_field'	:	{'field_name'	:	'company_name'},
		'general_contact_company_field_value'	:	{'field_value'	:	'- Company Name -'}
		},
		
		{'general_contact_company_field'	:	{'field_name'	:	'type_of_industry'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'website'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},


		{'general_contact_company_field'	:	{'field_name'	:	'phone_no'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'fax_no'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'street'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'state'},
		'general_contact_company_field_value'	:{	'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'city'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'
		}},

		{'general_contact_company_field'	:	{'field_name'	:	'pincode'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		},

		{'general_contact_company_field'	:	{'field_name'	:	'country'},
		'general_contact_company_field_value'	:	{'field_value'	:	'NA'}
		}
		]
	test=data['company_details'][0]

	return data
	pass
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def update():
	# this is the func to only load the update page for the 1st time remaining will be done by ajax
	done=0 		# a flag to represent the succes
	# check the user is loged in or not
	
	if session_check():
		if len(request.args)>0:
			
			lData={} # A dict to store the response of the server

				# session_details={'comapny_id':session.company_id,
	   #                 'user_id':session.user_id,
	   #                 'deal_key_id':request.args[0],

	   #                 }

			# take the deals key id from the page we have been redirected to get the data
			lRequestData={
				'deal_key_id':request.args[0],
				'user_id': session.user_id,
				'company_id':session.company_id
			}

			# try to fetch the required data from the api
			try:
				lData = fetch_deal_basic_details(lRequestData)
			except Exception as e:
				session.message=" error in geting the deals update %s" %e
			else:
				done=1
				pass

			if done==1:
				return dict(data=lData, deal_key_id=lRequestData['deal_key_id'],session_details=lRequestData)
			else:
				session.message=' Envalid deal selected '

		else:
			redirect(URL('deals'))
			session.flash="select a deal to continue"


	else:
		redirect(URL('../../../ERP/LoginPage/login'))
		session.flash="login to continue"
	pass

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def fetch_deal_update_details(lRequestData):
	
	# # following data is only for the testing
	
	# ={
	# 'request_type': 'get',		# get and add
	# 'lead_key_id': '49',
	# 'user_id': 2,				##############
	# 'company_id':25,		##############
	# 'update_head': 'notes',
	# 'update_data': 'hiiiiii53642795632987',
	# 'lead_status_id':1,					#request.vars.status_id,
	# 'session_id':0		##############
	# #'lead_update_id':request.vars.lead_update_id
	# }
	# get the data rewuired from the db
	try:
		i=0
		lData={}
		rows = db((db.general_deal_updates.update_head == lRequestData['update_head']) & (db.general_deal_updates.deal_status_id == db.general_deal_status_master.id) & (db.general_deal_updates.deal_key_id == lRequestData['deal_key_id']) & (db.general_deal_updates.is_active == True) & (db.general_deal_updates.company_id == lRequestData['company_id'])
			).select(
			db.general_deal_updates.company_id, 
			db.general_deal_updates.deal_key_id, 
			db.general_deal_updates.deal_status_id, 
			db.general_deal_updates.update_head, 
			db.general_deal_updates.update_data, 
			db.general_deal_updates.update_file, 
			db.general_deal_updates.head_id, 
			db.general_deal_updates.title, 
			db.general_deal_updates.update_file_name, 
			db.general_deal_updates.head_version, 
			db.general_deal_updates.db_entry_time,
			db.general_deal_updates.db_entered_by_name, 
			orderby=~db.general_deal_updates.db_entry_time
			).as_list()	
	except Exception as e:
		return e

	else:
		for row in rows:
			lData[str(i)]=row
			time=datetime.now()
			lDuration=relativedelta.relativedelta(time, lData[str(i)]['db_entry_time'])
			if lDuration.years==0:
				if lDuration.months==0:
					if lDuration.days==0:
						if lDuration.hours==0:
							if lDuration.minutes==0:
								lData[str(i)]['db_entry_time']=str(lDuration.seconds)+" sec  ago"
							else:
								lData[str(i)]['db_entry_time']=str(lDuration.minutes)+" minutes  ago"
								
						else:
							lData[str(i)]['db_entry_time']=str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
					else:
						lData[str(i)]['db_entry_time']=str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
				else:
					lData[str(i)]['db_entry_time']=str(lDuration.months)+" months "+str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
			else:
				lData[str(i)]['db_entry_time']=str(lDuration.years)+" years "+str(lDuration.months)+" months "+str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"


			# lData[str(i)]['db_entry_time']=str(lDuration.months)+"M "+str(lDuration.days)+"D "+str(lDuration.hours)+"h "+str(lDuration.minutes)+"m "+str(lDuration.seconds)+"s **"
			i+=1

	return lData

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

def download(): return response.download(request,db)

def get_versions():
	return locals()

def water_test_form():
	lFields=[]
	rows = db(db.general_water_test_field.is_active==True).select()
	for row in rows:
		if row.field_widget_attributes:
			widget=eval(row.field_widget_attributes)
		else:
			widget=eval('SQLFORM.widgets.string.widget') 		# a default value for a field if the widget not given
		if row.field_requires_attributes:
			requires=eval(row.field_requires_attributes)
		else:
			requires=[] 		# it is a list and can be empty		
		lFields.append(Field('f_'+str(row.id),widget=widget, requires=requires))

	form =SQLFORM.factory(*lFields)
	return form

def deal_upload():

	session_data= request.vars

	fields=[]

	lWaterTestField=db(db.general_water_test_field.is_active==True).select()
	for row in lWaterTestField:
		fields.append(eval('INPUT(_name="f_'+str(row.id)+'",_type="string")'))
		pass
	
	water_form=FORM(*fields)

	upload_form = FORM(
		INPUT(_name='description',_type='text'),
		INPUT(_name='update_file',_type='file'),
		INPUT(_name='version',_type='string'),
		INPUT(_name='head_id',_type='string'),
		INPUT(_name='title',_type='string')
		)
	done=0
	e=''
	if upload_form.accepts(request.vars,formname='upload_form'):
		if type(upload_form.vars.update_file) != bytes:
			try:
				lStorageFile = db.general_deal_updates.update_file.store(upload_form.vars.update_file.file, upload_form.vars.update_file.filename)
				db.general_deal_updates.insert(
							session_id=session_data['session_id'],
							company_id=session_data['company_id'],
							deal_key_id=session_data['deal_key_id'],
							deal_status_id=session_data['deal_status_id'],
							update_head=session_data['update_head'],
							update_data=upload_form.vars.description,
							title=upload_form.vars.title,
							head_id=upload_form.vars.head_id,
							update_file_name= upload_form.vars.update_file.filename,
							update_file= lStorageFile,
							head_version=upload_form.vars.version or 0,
							db_entry_time=lambda:datetime.now(),
							db_entered_by=session_data['user_id'],
							db_entered_by_name=session_data['user_name']
							)
			except Exception as e:
				return e

			else:
				# have to update the status also
				try:
					db((db.general_deal_status.deal_key_id==session_data['deal_key_id'])&
						(db.general_deal_status.is_active==True)).update(is_active=False)
					db.general_deal_status.insert(
							activity=session_data['update_head'].title().replace('_',' ')+' added',
							session_id=session_data['session_id'],
							company_id=session_data['company_id'],
							deal_key_id=session_data['deal_key_id'],
							current_stage='1',
							deal_status_master_id=session_data['deal_status_id'],
							db_entry_time=lambda:datetime.now(),
							db_entered_by=session_data['user_id'],
							db_entered_by_name=session_data['user_name']
							)
					pass
				except Exception as e:
					return 'error in adding the deal status' + str(e)
					pass
				else:
					done=1
		else:
			try:
				db.general_deal_updates.insert(
							session_id=session_data['session_id'],
							company_id=session_data['company_id'],
							deal_key_id=session_data['deal_key_id'],
							deal_status_id=session_data['deal_status_id'],
							update_head=session_data['update_head'],
							update_data=str(upload_form.vars.description)+' *No file included * ',
							title=upload_form.vars.title,
							head_id=upload_form.vars.head_id,
							update_file_name='No file attached',
							update_file= 'NA',
							head_version=upload_form.vars.version or 0,
							db_entry_time=lambda:datetime.now(),
							db_entered_by=session_data['user_id'],
							db_entered_by_name=session_data['user_name']
							)
			except Exception as e:
				return e
			else:
				# have to update the status also
				try:
					db((db.general_deal_status.deal_key_id==session_data['deal_key_id'])&
						(db.general_deal_status.is_active==True)).update(is_active=False)
					db.general_deal_status.insert(
							activity=session_data['update_head'].title().replace('_',' ')+' added',
							session_id=session_data['session_id'],
							company_id=session_data['company_id'],
							deal_key_id=session_data['deal_key_id'],
							current_stage='1',
							deal_status_master_id=session_data['deal_status_id'],
							db_entry_time=lambda:datetime.now(),
							db_entered_by=session_data['user_id'],
							db_entered_by_name=session_data['user_name']
							)
					pass
				except Exception as e:
					return 'error in adding the deal status' + str(e)
					pass
				else:
					done=1
	
	if water_form.accepts(request.vars,formname='water_test'):
		
		# add the deals status update and than take that key to store the water test
		try:
			Id=db.general_deal_updates.insert(
						session_id=session_data['session_id'],
						company_id=session_data['company_id'],
						deal_key_id=session_data['deal_key_id'],
						deal_status_id=session_data['deal_status_id'],
						update_head=session_data['update_head'],
						update_data='Water Test data added',
						title='Water Test Data',
						head_id='1',
						update_file_name='No file attached',
						update_file= 'NA',
						head_version='0',
						db_entry_time=lambda:datetime.now(),
						db_entered_by=session_data['user_id'],
						db_entered_by_name=session_data['user_name']
						)
		except Exception as e:
			return e
		else:
			# have to update the status also
			try:
				db((db.general_deal_status.deal_key_id==session_data['deal_key_id'])&
					(db.general_deal_status.is_active==True)).update(is_active=False)
				db.general_deal_status.insert(
						activity=session_data['update_head'].title().replace('_',' ')+' added',
						session_id=session_data['session_id'],
						company_id=session_data['company_id'],
						deal_key_id=session_data['deal_key_id'],
						current_stage='1',
						deal_status_master_id=session_data['deal_status_id'],
						db_entry_time=lambda:datetime.now(),
						db_entered_by=session_data['user_id'],
						db_entered_by_name=session_data['user_name']
						)
				pass
			except Exception as e:
				return 'error in adding the deal status' + str(e)
				pass
			else:
				for row in lWaterTestField:
					db.general_water_test_field_value.insert(
						field_id=row.id,
						key_id=session_data['deal_key_id'],
						key_reference='general_deal_fiedl_key',
						update_key=Id,
						update_referece='general_deal_updates',
						test_title=row.field_name,
						test_value=eval('water_form.vars.f_'+str(row.id)),
						company_id=session_data['company_id'],
						session_id=session_data['session_id'],
						db_entry_time=lambda:datetime.now(),
						db_entered_by=session_data['user_id'],
					)
				done=1
	

		

	data=[]
	lRequestData={
	'request_type': 'get',		# get and add
	'deal_key_id': session_data['deal_key_id'],
	'user_id': session_data['user_id'],				##############
	'company_id':session_data['company_id'],		##############
	'update_head': session_data['update_head'],
	'update_data': '',
	'deal_status_id':session_data['deal_status_id'],					
	'session_id':session_data['session_id']		##############
	}
	data=fetch_deal_update_details(lRequestData)
	# return dict(data=data)

	return locals()


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def fetch_deal_status_details(lRequestData):
	
	# ={
	# 'request_type': 'get',		# get and add
	# 'deal_key_id': '49',
	# 'user_id': 2,				##############
	# 'company_id':25,		##############
	# 'update_head': '',
	# 'update_data': 'yes',
	# 'deal_status_id':1,					#request.vars.status_id,
	# 'session_id':0,		##############
	# 'respose':1
	# }

	lData={}
	
	i=0
	lData={}
	rows = db((db.general_deal_status.deal_key_id==lRequestData['deal_key_id'])&
		(db.general_deal_status.company_id==lRequestData['company_id'])&
		(db.general_deal_status.deal_status_master_id==db.general_deal_status_master.id)
			).select(
			db.general_deal_status.deal_status_master_id,
			db.general_deal_status_master.progress,
			db.general_deal_status_master.deal_status,
			db.general_deal_status.activity,
			db.general_deal_status.db_entry_time,
			db.general_deal_status.db_entered_by,
			db.general_deal_status.db_entered_by_name,
			).as_list()

	for row in rows:
		lData[str(i)]=row
		time=datetime.now()
		lDuration=relativedelta.relativedelta(time, lData[str(i)]['general_deal_status']['db_entry_time'])
		if lDuration.years==0:
			if lDuration.months==0:
				if lDuration.days==0:
					if lDuration.hours==0:
						if lDuration.minutes==0:
							lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.seconds)+" sec  ago"
						else:
							lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.minutes)+" minutes  ago"
							
					else:
						lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
				else:
					lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
			else:
				lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.months)+" months "+str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"
		else:
			lData[str(i)]['general_deal_status']['db_entry_time']=str(lDuration.years)+" years "+str(lDuration.months)+" months "+str(lDuration.days)+" days "+str(lDuration.hours)+" hours "+str(lDuration.minutes)+" minutes  ago"

		i+=1
	
	

	return lData

def deal_status():
	session_data= request.vars
	# form_data={}
	form = FORM(
		INPUT(_name='field_name',_type='string'),
		INPUT(_name='deal_status_master_id',_type='string'),
		INPUT(_name='deal_key_id',_type='string'),
		INPUT(_name='',_type='string'),
		)
	if form.accepts(request.vars,formname='status_form'):
		db((db.general_deal_status.deal_key_id == form.vars.deal_key_id )&
			(db.general_deal_status.is_active == True)
			).update(is_active=False)
		db.general_deal_status.insert(
			activity='Status update at '+ str(form.vars.field_name),
			session_id=session_data['session_id'],
			company_id=session_data['company_id'],
			deal_key_id=form.vars.deal_key_id,
			deal_status_master_id=form.vars.deal_status_master_id,
			current_stage=form.vars.deal_status_stage_value,
			db_entry_time=lambda:datetime.now(),
			db_entered_by=session_data['user_id'],
			db_entered_by_name=session_data['user_name']
			)
		# form_data=form.vars
		pass
	lRequestData={
	'request_type': 'get',		# get and add
	'deal_key_id': session_data['deal_key_id'],
	'user_id': 2,				##############
	'company_id':25,		##############
	'update_head': '',
	'update_data': 'yes',
	'deal_status_id':session_data['deal_status_id'],					#request.vars.status_id,
	'session_id':0,		##############
	'respose':1
	}
	data=fetch_deal_status_details(lRequestData)
	lStatusData={}
	rows= db(db.general_deal_status_master).select()
	for row in rows:
		lStatus=db((db.general_deal_status.deal_status_master_id==row.id)&
			(db.general_deal_status.deal_key_id== session_data['deal_key_id'])
			).select(db.general_deal_status.current_stage,orderby=~db.general_deal_status.db_entry_time,limitby=[0,1])
		if len(lStatus)>0:
			lStatusData[str(row.deal_status)]=[lStatus[0].current_stage if lStatus[0].current_stage !=None else 0,row.id]
		else:
			lStatusData[str(row.deal_status)]=[0,row.id]

		pass
	return locals()
