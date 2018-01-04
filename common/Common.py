#! /usr/bin/python
# -- coding: utf-8 --
from multiprocessing import Process
import docs.settings as settings
from urllib import request
from scrapy.selector import Selector
from common.MySQLHelper import MySQLHelper
from lxml import etree
import random
import string
import time
import re
import json
import os
class Common(object):
	"""docstring for Common"""
	def __init__(self):
		#super(Common, self).__init__()
		#self.arg = arg
		pass

	def main_spider(self):
		p = Process(target=self.zhipin)
		p.start()

		a = Process(target=self.cjol_list)
		a.start()

	#boss的爬取
	def zhipin(self):
		url_dict = [
			'https://www.zhipin.com/c101280600/h_101280600/?query=php', #php
			'https://www.zhipin.com/c101280600/h_101280600/?query=python' #python
		]
		for a in range(len(url_dict)):
			for x in range(1,999):
				page = '%s%s%s%s' % ('&page=',x,'&ka=page-',x)
				url = '%s%s' % (url_dict[a],page)
				print(url)
				f = request.urlopen(url)
				html = f.read()

				#检查页面page是否存在，如果不存在就跳出
				title = Selector(text=html).xpath('//*[@id="main"]/div[3]/div[2]/div[2]').extract()
				try:
					page = title[0]
				except Exception as e:
					break

				#读取当页面list
				page_list = Selector(text=html).xpath('//*[@id="main"]/div[3]/div[2]/ul/li').extract()
				vs = MySQLHelper()
				for b in range(len(page_list)):
					list_text = page_list[b]
					title = Selector(text=list_text).xpath('//div[1]/div[1]/h3/a/text()').extract()
					pay = Selector(text=list_text).xpath('//div[1]/div[1]/h3/a/span/text()').extract()
					url = Selector(text=list_text).xpath('//div[1]/div[1]/h3/a//@href').extract()
					area = Selector(text=list_text).xpath('//div[1]/div[1]/p/text()[1]').extract()
					company_title = Selector(text=list_text).xpath('//div[1]/div[2]/div/h3/a/text()').extract()
					company_url = Selector(text=list_text).xpath('//div[1]/div[2]/div/h3/a//@href').extract()
					page_time_text = Selector(text=list_text).xpath('//*[@class="time"]/text()').extract()
					#print(page_time_text)
					
					try:
						page_time_text = page_time_text[0]
					except Exception as e:
						page_time_text = ''
					current_time = time.gmtime(int(time.time()))
					page_time = '%s%s%s%s%s' % (current_time.tm_year,'-',current_time.tm_mon,'-',current_time.tm_mday)
					page_time = int(time.mktime(time.strptime(page_time, '%Y-%m-%d')))
					

					company_url = '%s%s' % ('https://www.zhipin.com',company_url[0])
					url = '%s%s' % ('https://www.zhipin.com',url[0])
					try:
						company_id = self.company_id(company_title[0],company_url,area[0]) #具体说明看方法备注
						#print(company[0])
					except Exception as e:
						print('break')
						continue
					data = {
						'web_type': 'zhipin',
						'url': url,
						'title': title[0],
						'company_id': company_id,
						'pay': pay[0],
						'time': page_time,
						'remark': page_time_text
					}
					
					#SELECT list.id FROM list WHERE list.company_id = 1 AND list.title = 'ssss' AND list.time = 2222 LIMIT 0, 1
					query = '%s%s%s%s%s%s%s%s%s' % ('SELECT list.id FROM list WHERE list.company_id = ',company_id,' AND list.title = "',title[0],'" AND list.time = ',page_time,' AND list.url = "',url,'" LIMIT 0, 1')
					#print(query)
					text = vs.queryAll(query)
					#print(len(text))
					if len(text) == 1:
						print('list_break')
						continue
					else:
						vs.insert('list',data)  #把信息写入数据库
						#print(data)
						vs.commit()
				vs.close()
				time.sleep(1)
			time.sleep(1)

	#cjol的列表读取
	def cjol_list(self):
		url_dict = [
			'http://s.cjol.com/service/joblistjson.aspx?KeyWord=php&Location=2008&SearchType=3&ListType=2', #php
			'http://s.cjol.com/service/joblistjson.aspx?KeyWord=python&Location=2008&SearchType=3&ListType=2' #python
		]

		for a in range(len(url_dict)):
			url = url_dict[a]
			f = request.urlopen(url)
			html = f.read() #取页返回json
			html1 = str(html, encoding = "utf-8") #转成str
			html2 = json.loads(html1) #转为字典
			print(url)
			self.cjol_list_tomysql(html2) #返回进来的json通过这个方法整理后写入数据库

			#print(down_url)
			#我们看到他们每页显示40个，这里如果超过40个就读取翻页
			if html2['RecordSum'] > 40:
				page_num = html2['RecordSum'] / 40
				page_num = int(page_num) + 2 #这里是为了让循环里面取到正确的页数，上面的除数转为整形的时候会去掉小数位
				
				for x in range(2,page_num):
					page_url = '%s%s%s' % (url,'&page=',x)
					f = request.urlopen(page_url)
					print(page_url)
					html = f.read() #取页返回json
					#print(html)
					html1 = str(html, encoding = "utf-8") #转成str
					html2 = json.loads(html1) #转为字典
					#print('down_page')
					self.cjol_list_tomysql(html2)
					time.sleep(1)
			time.sleep(1)

	#输入进来爬取到的json数据，整理后写入数据库
	def cjol_list_tomysql(self,html_str):
		job_list = Selector(text=html_str['JobListHtml']).xpath('//*[@id="searchlist"]/ul').extract()
		#print(len(job_list))
		vs = MySQLHelper()
		for a in range(len(job_list)):
			text = job_list[a]
			text = text.replace("<strong>","") #去掉高亮显示
			text = text.replace("</strong>","")
			title = Selector(text=text).xpath('//ul/li[2]/h3/a/text()').extract()
			pay = Selector(text=text).xpath('//ul/li[7]/text()').extract()
			url = Selector(text=text).xpath('//ul[1]/li[2]/h3/a//@href').extract()
			area = Selector(text=text).xpath('//ul[1]/li[4]/text()').extract()
			page_time = Selector(text=text).xpath('//ul[1]/li[8]/text()').extract()
			company_url = Selector(text=text).xpath('//ul[1]/li[3]/a//@href').extract()
			company = Selector(text=text).xpath('//ul[1]/li[3]/a/text()').extract()
			try:
				company_id = self.company_id(company[0],company_url[0],area[0]) #具体说明看方法备注
				#print(company[0])
			except Exception as e:
				print('break')
				continue
			#print(text)

			#时间转成unix时间戳
			current_time = time.gmtime(int(time.time()))
			page_time_split = page_time[0].split('-')
			
			if page_time_split[0] != '01':
				curr_year = '2017'
			else:
				curr_year = current_time.tm_year
			page_time = '%s%s%s' % (curr_year,'-',page_time[0])
			page_time = int(time.mktime(time.strptime(page_time, '%Y-%m-%d')))

			data = {
				'web_type': 'cjol',
				'url': url[0],
				'title': title[0],
				'company_id': company_id,
				'pay': pay[0],
				'time': page_time
			}
			
			#SELECT list.id FROM list WHERE list.company_id = 1 AND list.title = 'ssss' AND list.time = 2222 LIMIT 0, 1
			query = '%s%s%s%s%s%s%s%s%s' % ('SELECT list.id FROM list WHERE list.company_id = ',company_id,' AND list.title = "',title[0],'" AND list.time = ',page_time,' AND list.url = "',url[0],'" LIMIT 0, 1')
			text = vs.queryAll(query)
			if len(text) == 1:
				print('list_break')
			else:
				vs.insert('list',data)  #把信息写入数据库
				vs.commit()
		vs.close()

	#输入公司名称，url，和地区，如果有就返回id，如果没有就自动创建
	def company_id(self,company_name,company_url,area):
		area_id = self.area_id(area)
		vs = MySQLHelper()
		query = '%s%s%s%s%s%s%s' % ('SELECT company.id FROM company WHERE company.`area` = "',area_id,'" AND company.`name` = "',company_name,'" AND company.company_url = "',company_url,'" LIMIT 0, 1')
		text = vs.queryAll(query)
		
		if len(text) == 1:
			return text[0]['id']
		else:
			company_data = {
				'name': company_name,
				'area': area_id,
				'company_url': company_url
			}
			vs.insert('company',company_data)
			vs.commit()
			return_id = vs.getLastInsertId()
			vs.close()
			return return_id
		
	#输入地区名称，有就返回id，没有就自动创建并返回自增id
	def area_id(self,area):
		vs = MySQLHelper()
		query = '%s%s%s' % ('SELECT area.id FROM area WHERE area.`name` = "',area,'" LIMIT 0, 1;')
		text = vs.queryAll(query)
		if len(text) == 1:
			return text[0]['id']
		else:
			area_data = {
				'name': area
			}
			vs.insert('area',area_data)
			vs.commit()
			return_id = vs.getLastInsertId()
			vs.close()
			return return_id

