#encoding:utf-8
import pymysql
import docs.settings as settings
class MySQLHelper(object):

	def __init__(self):
		super(MySQLHelper, self).__init__()
		self.conn = pymysql.connect(host="127.0.0.1",user="username",password="password",db="job",port=3306,charset= 'utf8')
		self.cur = self.conn.cursor()
		'''
		cur.execute("select * from user")
		row_1 = cur.fetchone()
		#print(row_1)
		# 获取剩余结果前n行数据
		# row_2 = cursor.fetchmany(3)
		 
		# 获取剩余结果所有数据
		# row_3 = cursor.fetchall()
		db.commit()
		cur.close()
		db.close()

		self.conn=pyMySQL.connect(vs_config.configs['db']['host'],vs_config.configs['db']['user'],vs_config.configs['db']['password'])
		self.conn.set_character_set(vs_config.configs['db']['charset'])
		self.conn.select_db(vs_config.configs['db']['database'])
		self.cur=self.conn.cursor()
		'''

	def query(self,sql):
		try:
			 n=self.cur.execute(sql)
			 return n
		except pymysql.Error as e:
			 print("Mysql Error:%s\nSQL:%s" %(e,sql))

	def queryRow(self,sql):
		self.query(sql)
		result = self.cur.fetchone()
		return result

	def queryAll(self,sql):
		self.query(sql)
		result=self.cur.fetchall()
		desc =self.cur.description
		d = []
		for inv in result:
				 _d = {}
				 for i in range(0,len(inv)):
						 _d[desc[i][0]] = str(inv[i])
				 d.append(_d)
		return d

	def insert(self,p_table_name,p_data):
		for key in p_data:
				p_data[key] = "'"+str(p_data[key])+"'"
		key   = ','.join(p_data.keys())
		value = ','.join(p_data.values())
		real_sql = "INSERT INTO " + p_table_name + " (" + key + ") VALUES (" + value + ")"
		#print(real_sql)
		#self.query("set names 'utf8'")
		return self.query(real_sql)


	def getLastInsertId(self):
		return self.cur.lastrowid

	def rowcount(self):
		return self.cur.rowcount

	def commit(self):
		self.conn.commit()

	def close(self):
		self.cur.close()
		self.conn.close()
