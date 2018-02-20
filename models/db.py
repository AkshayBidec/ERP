# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    #db = DAL(configuration.get('db.uri'),
             # pool_size=configuration.get('db.pool_size'),
             # migrate_enabled=configuration.get('db.migrate'),
             # check_reserved=['all'])
    db = DAL('mysql://root:@localhost/erp_general_db',migrate=True,migrate_enabled=configuration.get('db.migrate'),check_reserved=['all'])

else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('mysql://root:meranam@localhost/erp_general_db')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
# if request.is_local and not configuration.get('app.production'):
response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configure.get('heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------
db.define_table('general_master_verification_details',
    Field('verification_code', type='string', length=5000, required=True, notnull=True),
    Field('is_active', type='boolean', default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime', required=True, notnull=True),
    Field('db_update_time', type='datetime', notnull=False),
    Field('remarks', type='string', length=2000, notnull=False)
)

db.define_table(
    'general_company_details',
    Field('company_name',type='string',length=1000, required=True, notnull=True),
    Field('company_identification',type='string',length=2000, required=True, notnull=True),
    Field('verification_code',type='string', length=5000, required=True, notnull=True),
    Field('company_address_line1',type='string',length=5000, required=True, notnull=True),
    Field('company_address_line2',type='string',length=5000, required=False, notnull=False),
    Field('country',type='string',length=500, required=True, notnull=True),
    Field('states',type='string',length=500, required=True, notnull=True),
    Field('city',type='string',length=500, required=True, notnull=True),
    Field('pincode',type='integer', required=True, notnull=True),
    Field('office_number',type='integer', required=True, notnull=True),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_update_time', type='datetime', notnull=False)
)

# db.define_table(
#     'general_superadmin_details',
#     # Field('company_id',db.general_company_details),
#     # Field('first_name',type='string',length=250, required=True, notnull=True),
#     # Field('last_name',type='string',length=250, required=False, notnull=False),
#     # Field('email_id',type='string',length=500, required=False, notnull=True),
#     # Field('mobile_number',type='integer', required=True, notnull=True),
#     # Field('password',type='password', required=True, notnull=True),
#     # Field('temp_password',type='password', required=False, notnull=False),
#     # # Field('verification_code',type='string', length=5000, required=True, notnull=True),
#     Field('forgot_password_verification',type='string',length=2000,required=False,notnull=False),
#     Field('ip_address',type='string',length=500, required=True, notnull=True),
#     Field('mac_address',type='string',length=500, required=False, notnull=False),
#     Field('locations',type='string',length=500, required=False, notnull=False),
#     Field('is_active',type='boolean',default=True, required=True, notnull=True),
#     Field('db_entry_time', type='datetime',  required=True, notnull=True),
#     Field('db_update_time', type='datetime', notnull=False),
#     Field('no_login_attempts', type='integer', notnull=False),
#     Field('last_login_time', type='datetime', notnull=False),
#     Field('last_logout_time', type='datetime', notnull=False)
# )

# db.general_superadmin_details.password.filter_in = lambda data: CRYPT('encrypt', data, iv_random=False)
# db.general_superadmin_details.password.filter_out = lambda data: CRYPT('decrypt', data, iv_random=False)

db.define_table(
    'general_session',
    Field('user_id',type='integer',required=True,notnull=True),
    Field('is_active',type='integer',default=0,required=True,notnull=True),
    Field('user_type',type='string',length=250,required=True,notnull=True),
    Field('login_time',type='datetime',required=False,notnull=False),
    Field('logout_time',type='datetime',required=False,notnull=False),
    Field('duration',type='string', length=200,required=False, notnull=False),
    Field('ip_address',type='string',length=500, required=True, notnull=True),
    Field('mac_address',type='string',length=500, required=False, notnull=False),
    Field('locations',type='string',length=500, required=False, notnull=False)
)

db.define_table(
    'general_user',
    Field('company_id',db.general_company_details),
    Field('first_name',type='string',length=250, required=True, notnull=True),
    Field('last_name',type='string',length=250, required=False, notnull=False),
    Field('email_id',type='string',length=500, required=False, notnull=True, unique=True),
    Field('mobile_number',type='integer', required=True, notnull=True),
    Field('password',type='password', required=True, notnull=True),
    Field('temp_password',type='password', required=False, notnull=False),
    Field('forgot_password_verification',type='string',length=2000,required=False,notnull=False),
    Field('ip_address',type='string',length=500, required=True, notnull=True),
    Field('mac_address',type='string',length=500, required=False, notnull=False),
    Field('locations',type='string',length=500, required=False, notnull=False),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_update_time', type='datetime', notnull=False),
    Field('no_login_attempts', type='integer', notnull=False),
    Field('last_login_time', type='datetime', notnull=False),
    Field('last_logout_time', type='datetime', notnull=False),
    Field('is_superadmin', type= 'integer',notnull=True)
)

db.define_table(
    'general_master_features_category',
    Field('category_code',type='string',length=250,required=True,notnull=True),
    Field('category_name',type='string',length=250,required=True,notnull=True),
    Field('company_id',db.general_company_details),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime', default=request.now, required=True, notnull=True),
    Field('db_update_time', type='datetime', notnull=False)
)



db.define_table(
    'general_master_features',
    Field('company_id',db.general_company_details),
    Field('feature_name',type='string',length=500,required=True,notnull=True),
    Field('category',type='string',length=500,required=False,notnull=False),
    Field('sub_category',type='string',length=500,required=False,notnull=False),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',default=request.now, required=True, notnull=True),
    Field('db_update_time', type='datetime', notnull=False)
)


db.define_table(
    'general_user_features',
    Field('user_id',db.general_user),
    Field('feature_id',db.general_master_features),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_entered_by', type='integer',required=False,notnull=False),
    Field('db_update_time', type='datetime', notnull=False),
    Field('db_updated_by',type='integer',required=False,notnull=False),
    Field('session_id',db.general_session)
)

db.define_table(
    'general_role',
    Field('company_id',db.general_company_details),
    Field('role_name',type='string',length=250,required=True,notnull=True),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_entered_by', type='integer',required=False,notnull=False),
    Field('db_update_time', type='datetime', notnull=False),
    Field('db_updated_by',type='integer',required=False,notnull=False),
    Field('session_id',db.general_session)
)

db.define_table(
    'general_user_role',
    Field('user_id',db.general_user),
    Field('role_id',db.general_role),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_entered_by', type='integer',required=False,notnull=False),
    Field('db_update_time', type='datetime', notnull=False),
    Field('db_updated_by',type='integer',required=False,notnull=False),
    Field('session_id',db.general_session)
)

db.define_table(
    'general_role_features',
    Field('role_id',db.general_role),
    Field('feature_id',db.general_master_features),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_entered_by', type='integer',required=False,notnull=False),
    Field('db_update_time', type='datetime', notnull=False),
    Field('db_updated_by',type='integer',required=False,notnull=False),
    Field('session_id',db.general_session)
)

db.define_table(
    'general_role_hrchy',
    Field('role_id',db.general_role),
    Field('upper_role_id',db.general_role),
    Field('is_active',type='boolean',default=True, required=True, notnull=True),
    Field('db_entry_time', type='datetime',  required=True, notnull=True),
    Field('db_entered_by', type='integer',required=False,notnull=False),
    Field('db_update_time', type='datetime', notnull=False),
    Field('db_updated_by',type='integer',required=False,notnull=False),
    Field('session_id',db.general_session)
)
# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)

