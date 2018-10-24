# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import xmlrpclib

username = 'admin' #the user
pwd = '123'      #the password of the user
dbname = 'odoo11e_T8069'    #the database

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://10.10.2.108:8069:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)

#replace 10.10.2.108:8069 with the address of the server
sock = xmlrpclib.ServerProxy('http://10.10.2.108:8069:8069/xmlrpc/object')



models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
models.execute_kw(db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'], {'raise_exception': False})