#update eds_building set house = CONCAT(house, '_-1') where JSON_EXTRACT(source,'$.RowType') = -1
#update eds_employee set deleted = 1 where deleted = -1

import pymysql
import json

company_id = 1
HOST = 'localhost' 
USER = 'root' 
PASSWORD = 'mymyvveR01' 
DATABASE = 'argon'
conns = pymysql.connect(host= HOST, user= USER, password= PASSWORD, database= DATABASE, autocommit=True, cursorclass=pymysql.cursors.DictCursor)
connd = pymysql.connect(host= 'localhost', user= 'root', password= 'mymyvveR01', database= 'bipro', autocommit=True, cursorclass=pymysql.cursors.DictCursor)

curs = conns.cursor()
curd = connd.cursor()


#curs.execute("""select * from auth_user""")
#rows = curs.fetchall()
#for row in rows:
#    curd.execute("""INSERT auth_user (external_id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
#  [row['id'],row['password'],row['last_login'],row['is_superuser'],row['username'],row['first_name'],row['last_name'],row['email'],row['is_staff'],row['is_active'],row['date_joined']])

#curs.execute("""select * from eds_street where is_used=1""")
#rows = curs.fetchall()
#for row in rows:
#    print(row)
#    curd.execute("INSERT dict_streetincompany (company_id,street_id) VALUES (%s,%s)",
#       [company_id, row['id']])

#curs.execute("""select * from eds_building""")
#rows = curs.fetchall()
#for row in rows:
#    print(row)
#    curd.execute("INSERT dict_building (name,house,channelid,square,flat_count,floor_count,company_id,location_id,street_id,external_id) VALUES(%s,%s,%s,0,0,0,%s,1,%s,%s)",
#       [row['name'],row['house'],row['channelid'], company_id, row['street_id'],row['id']])

#curs.execute("""select * from streets""")
#rows = curs.fetchall()
#for row in rows:
#    curd.execute("insert ignore eds_street (id,name,is_used,legal_name,c1_name,elevator_name) values (%s,%s,%s,%s,%s,%s)",
#        [row['ID'],row['Name'],row['InUse'],row['Name'],row['Name'],row['RowType']])
##==============EУЧАСТКИ======================
##{'ID': 698, 'RowType': 0, 'ModifierID': 1039, 'ModifyDate': datetime.datetime(2025, 1, 29, 16, 17, 34, 467000), 'CreateDate': datetime.datetime(2024, 3, 7, 8, 34, 38, 983000), 'CreatorID': 1039, 'Name': 'ООО "УК АТЛАНТ"', 'LegalName': 'ООО "УК АТЛАНТ"', 'Phone': '52-58-10', 'Director': 'Медведев Евгений Витальевич', 'CompanieID': None, 'parentid': None, 'Tariff': None, 'email': 'uk-atlant18@mail.ru', 'TypeID': None, 'ServiceArea': 8464.6, 'INN': '1831201043', 'CalcingByHouse': False, 'RateID': None, 'debt': None, 'ISTemporarilyOutOfService': True, 'CompantID': None, 'ContractTerminated': True, 'Kindergarten': False, 'every_day_orders': False, 'SchoolOrders': False}
#curs.execute("""select * from grps""")
#rows = curs.fetchall()
#for row in rows:
#    curd.execute("insert ignore eds_company (id,name,phone,email,legal_name,source) VALUES (%s,%s,%s,%s,%s,%s)",
#        [row['ID'],row['Name'],row['Phone'],None,row['LegalName'],json.dumps(row, indent=4, sort_keys=True, default=str)])
#
##curs.execute("""select * from houses""")
##rows = curs.fetchall()
##for row in rows:
##    curd.execute("""
##        INSERT ignore INTO eds_building (id,name,house,district_id,street_id,comment,company_id,description,source)
##        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
##        [row['ID'],row['Name'],row['House'],1,row['StreetID'],row['Comment'],row['GrpID'],row['Description'],json.dumps(row, indent=4, sort_keys=True, default=str)])
##
#curs.execute("""select * from employees""")
#rows = curs.fetchall()
#for row in rows:
#    curd.execute("""INSERT IGNORE INTO eds_employee (
#        id,name,comment,deleted,district_main_id, post)
#        VALUES (%s,%s,%s,%s,%s,%s)""",
#        [row['ID'],row['Name'],row['EmployeePost'],row['RowType'],1, 'worker'])
##
###==============================РАБОЧИЕ СИСТЕМЫ==================================#
#curs.execute("""select * from eds_worksystem""")
#rows = curs.fetchall()
#for row in rows:
#    curd.execute("""INSERT IGNORE INTO dict_worksystem (id,name,is_used) VALUES (%s,%s,%s)""",
#            [row['id'],row['name'],0])
##    except:
##        pass
##
###==============================СОСТОЯНИЕ ЗАЯВОК==================================#
#curs.execute("""select * from eds_orderstate""")
#rows = curs.fetchall()
#for row in rows:
#
#    curd.execute("""INSERT IGNORE INTO ads_orderstate (id,name,color,pos,сompleted) VALUES (%s,%s,%s,%s,%s)""",
#            [row['id'],row['name'],row['color'],row['pos'],row['сompleted'],])


#curs.execute("""select * from OrdersDescr""")
#rows = curs.fetchall()
#for row in rows:
####    #try:
#        print(row)
#        if row['WorkSystemID']:
#            curd.execute("""INSERT IGNORE INTO eds_standarddescription (
#                id,name,worksystem_id)
#                VALUES (%s,%s,%s)""",
#                [row['ID'],row['Name'],row['WorkSystemID']])
##    #except:
##    #    pass
#
#curs.execute("""select * from works where RowType=0""")
#rows = curs.fetchall()
#for row in rows:
#    print(row)
#    
#    curd.execute("""INSERT IGNORE INTO eds_work (
#            id, name, measure, price, worksystem_id, description)
#            VALUES (%s,%s,%s,%s,%s,%s)""",
#            [row['ID'], row['Name'], row['Measure'], row['Price'], row['WorkSystemID'], row['Comment']])
#
#
#
#curs.execute("""select * from OrderStates""")
#rows = curs.fetchall()
#for row in rows:
#    print(row)
#
#
#
#



curs.execute("""select * from eds_order """)
rows = curs.fetchall()
for row in rows:
    curd.execute('select id from auth_user where external_id = %s', [row['author_id'],])
    author_id = curd.fetchone()
    curs.execute('select name from eds_employee where id = %s', [row['master_id'],])
    master_text = curs.fetchone()

    curs.execute("select eds_employee.name from eds_order_employee left join eds_employee ON eds_order_employee.employee_id = eds_employee.id where eds_order_employee.order_id = %s", row['id'])
    empl_rows = curs.fetchall()
    worker_text = ''
    for empl in empl_rows:
        worker_text += empl['name']+';'

    print(author_id, master_text, worker_text)

    try:
        curd.execute("""INSERT ads_order (
          creation_date,
          modified_date,
          last_printed_date,
          number,
          order_date,
          ordertype,
          priority,
          sourcetype,
          citizen,
          phone,
          house,
          flat,
          entrance,
          floor,
          plan_date,
          plan_period,
          description,
          fact_date,
          fact_start_work_time,
          fact_description,
          orderid,
          summa,
          author_id,
          building_id,
          company_exec_id,
          company_owner_id,
          district_id,
          master_id,
          street_id,
          worksystem_id,
          state_id,
          master_text,
          plan_text,
          worker_text)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
          [row['creation_date'],
          row['modified_date'],
          row['last_printed_date'],
          row['number'],
          row['order_date'],
          row['ordertype'],
          row['priority'],
          row['sourcetype'],
          row['citizen'],
          row['phone'],
          row['house'],
          row['flat'],
          row['entrance'],
          row['floor'],
          row['plan_date'],
          row['plan_period'],
          row['description'],
          row['fact_date'],
          row['fact_start_work_time'],
          row['fact_description'],
          row['id'],
          row['summa'],
          author_id['id'],
          None,
          None,
          company_id,
          None,
          None,
          row['street_id'],
          row['worksystem_id'],
          row['state_id'],
          master_text['name'] if master_text else None,
          row['plan_text'],
          worker_text])
    except Exception as e:
        print(f'Ошибка: {e}')


