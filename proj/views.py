from django.shortcuts import render

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

import MySQLdb
import pandas as pd
import json
import itertools
import decimal
from .models import current

#Database setup
mysqlhost = "djangomysqltest.ckeqhtrt4wyd.us-west-2.rds.amazonaws.com"
mysqluser = "morrisons"
mysqlpw = "morrisons"
mysqldb = "usf"

# date handler to convert mysql dates into json readable dates
def date_handler(obj):
	if hasattr(obj, 'isoformat'):
		return obj.isoformat()
	elif isinstance(obj, decimal.Decimal):
		return float(obj)
	else: 
		return obj

#included for views that need login
from django.contrib.auth.decorators import login_required

@login_required
def welcome(request):
	return render_to_response('welcome.html')


#from .models import Marketing
@login_required
## HD- describe in a few words what this function does?
def campaign_send(request):
	#Currently using the sql lite to store information about which campaign is selected
	#we wipe this data at the beginning of each session
	if len(current.objects.all()) > 0:
		current.objects.all()[0].delete()

	#accessing the campaign_information table in mysql
	db = MySQLdb.connect(host = mysqlhost,
		user = mysqluser,
		passwd = mysqlpw,
		db = mysqldb)

	cur = db.cursor()



	#############using sqllite
	## HD- does save_current save the information entered on the webpage? and how? 
	save_current = current(campaign_id="",vendor_id="",clientname="",clientnum="",offer_id="")
	save_current.save()

	cur.execute("select a.* , count(b.precimaVendorID) as counter " + \
				"from campaign_information a left join vendor_info b " + \
				"on a.precimaCampaignID=b.precimaCampaignID " + \
				"group by 1,2,3,4,5,6")

	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	data = [dict(itertools.izip(column_names, row)) for row in result]
	campaign_info = json.dumps(data,default=date_handler)

	#grabbing all the different type of campaigns and their descriptive names
	# HD- camapign_list is being refered from which table?
	cur.execute("SELECT * FROM CAMPAIGN_LIST;")  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	data = [dict(itertools.izip(column_names, row)) for row in result]
	campaign_list = json.dumps(data,default=date_handler)

	#making a list of the unique campaign ids to make a list of all the existing campaigns 
	campaigns = []
	for item in result:
    		campaigns.append(item[0])
	
	db.close

	return render_to_response('campaign.html', {"campaign_info": campaign_info, 
												"campaigns":campaigns, 
												"campaign_list": campaign_list}, 
												context_instance=RequestContext(request))



from django.core.urlresolvers import reverse

#the ajax calls in campaign.html call this function
# HD- give a high level deifiniton to this function. eg- this funciton saves data entered 
# in the campaign page to the campaign table
@login_required
def campaign_receive(request):

	if request.method == 'POST':

		#reads the data in
		data = request.body
		print data
		#reads/loads the data, grabs it as a dictionary
		read_data = json.loads(data)
		selected_camp = read_data['selected']
		
		#working through the different conditions
		#first condition is if selected_camp isn't "none"
				#also means that no data was sent to be uploaded
		if (selected_camp!="none"): 
			if (len(current.objects.all())!=0):
				target = current.objects.all()[0]
				target.campaign_id = selected_camp
				target.vendor_id = ""
				target.offer_id = ""
				target.save()



		#second condition is that the data isn't empty and has information to  be loaded
		if (len(read_data['data'])!=0):
			db = MySQLdb.connect(host = mysqlhost,
				user = mysqluser,
				passwd = mysqlpw,
				db = mysqldb)
			cur = db.cursor()
	
			data_to_load = read_data['data']
				
				
			df = pd.read_json(json.dumps(data_to_load))
			column_names =  df.columns.values.tolist()
			column_names.remove('counter')
			column_names = str(column_names)
			column_names = column_names.replace("[","(")
			column_names = column_names.replace("]",")")
			column_names = column_names.replace("u\'","")
			column_names = column_names.replace("\'","")
			del df['counter']
		
			print column_names
			
			#angular/HTML inputs include "T00:00:00" at the end of dates, need to remove them
			df['endDate']=df['endDate'].str.replace("T00:00:00","")
			df['startDate']=df['startDate'].str.replace("T00:00:00","")
			print df
	
			insert_np = df.as_matrix()
			print insert_np
	
			for line in insert_np:

				insert_sql = "INSERT INTO campaign_information " + column_names + " values (" \
						+ "'" + line[0] \
						+ "','" + line[1] \
						+ "','" + line[2] \
						+ "','" + line[3] \
						+ "','" + line[4] \
						+ "')"
				print insert_sql
				cur.execute(insert_sql)
	
			db.commit()
		if (selected_camp=="none"):
			return campaign_send(request)
		else:
			return vendor_send(request)

		
@login_required
# HD- provide high level definition. is this similar to campaign_send
def vendor_send(request):

	db = MySQLdb.connect(host = mysqlhost,
		user = mysqluser,
		passwd = mysqlpw,
		db = mysqldb)

	cur = db.cursor()

	#HD - what is this if statement for? eg: If there is no selection for vendor object, or if there is not session data passed alongside the function call etc. 
	
	if (len(current.objects.all())!=0):
			target = current.objects.all()[0]
			selected_camp = target.campaign_id
			target.vendor_id = ""
			target.offer_id = ""
			target.save()
			

# HD- what is this sql doing? similar to campaign_send 
	vendor_sql = "select a.* , count(b.precimaofferID) as counter " \
				+ "from vendor_info a left join offer_info b " \
				+ "on a.precimaVendorID=b.precimaVendorID " \
				+ "where a.precimacampaignid= '" + selected_camp + "' " \
				+ "group by 1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19"
	
	cur.execute(vendor_sql)  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	vendor_data = [dict(itertools.izip(column_names, row)) for row in result]

	vendor_list = []
	for item in result:
    		vendor_list.append(item[14])


   	#generating list of all suppliers 
	clients_sql = "SELECT DISTINCT parent_supl_num, parent_supl_name FROM clients"
	cur.execute(clients_sql)  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	client_data = [dict(itertools.izip(column_names, row)) for row in result]

	db.close

	vendor_info = json.dumps(vendor_data,default=date_handler)
	client_info = json.dumps(client_data)

	if selected_camp=="":
		return render_to_response('error.html', {}, 
												context_instance=RequestContext(request))

	else:
		selected_camp = "\'" + selected_camp + "\'"

		return render_to_response('vendor.html', {"vendor_info": vendor_info, 
												"vendor_list": vendor_list, 
												"client_info":client_info, 
												"selected_camp":selected_camp}, 
												context_instance=RequestContext(request))

@login_required
#HD- high levl definition for this function. Similar to campaign_receive??
def vendor_receive(request):

	if request.method == 'POST':

		data = request.body
		print data
		read_data = json.loads(data)
		delete_list = read_data['delete_list']
		selected_vendor = read_data['selected_vendor']
		clientnum = read_data['clientnum']
		clientname = read_data['clientname']


		if (selected_vendor!="none"): 
			if (len(current.objects.all())!=0):
				target = current.objects.all()[0]
				target.vendor_id = selected_vendor
				target.clientname = clientname
				target.clientnum = clientnum
				target.offer_id = ""
				target.offernum = ""
				target.product_id = ""
				target.save()



		if (len(read_data['data'])!=0):
			#the front end passes back three lists to the backend 
			#insert, delete and update. These lists contain precimaVendorIDs
			insert_list = read_data['insert_list']
			update_list = read_data['update_list']
			

			db = MySQLdb.connect(host = mysqlhost,
				user = mysqluser,
				passwd = mysqlpw,
				db = mysqldb)
			cur = db.cursor()
	
			data_to_load = read_data['data']
			df = pd.read_json(json.dumps(data_to_load))
			df.fillna("")
			column_names =  df.columns.values.tolist()
			column_names.remove('$$hashKey')
			column_names.remove('id')
			column_names.remove('counter')
			del df['$$hashKey']
			del df['id']
			del df['counter']

			# HD- i am assuming insert list is adding data to vendor_info table. explain high level logic used below.
			if len(insert_list) > 0:
					#grabbing only items in the insert list from the dataframe
					insert_df = df[df['precimaVendorID'].isin(insert_list)]
					print insert_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					insert_np = insert_df.as_matrix()
					insert_col =  str(df.columns.values.tolist())
					insert_col = insert_col.replace("[","(")
					insert_col = insert_col.replace("]",")")
					insert_col = insert_col.replace("u\'","")
					insert_col = insert_col.replace("\'","")
					print insert_col
	
					
					for line in insert_np:
							i = 1
							insert_sql = "INSERT INTO vendor_info " + insert_col + " values ("
							print insert_sql

							val = ""
							for item in line:
								if (str(item)=='None' or str(item)=='nan'):
									val = val + "NULL"
									if (i != len(column_names)):
										val = val + ","
								else:
									val = val + "'" + str(item) + "'"
									if (i != len(column_names)):
										val = val + ","
								i = i + 1

							insert_sql = insert_sql + val + ");\n"
							print "\n" + insert_sql
							cur.execute(insert_sql)

					db.commit()
			#HD - explain high level logic used below to update vendor_info table.
			if len(update_list) > 0:
					update_df = df[df['precimaVendorID'].isin(update_list)]
					print update_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					update_np = update_df.as_matrix()
	
					
					for line in update_np:
							i2 = 0
							i = 1
							update_sql = "UPDATE vendor_info SET "

							for item in line:
								if (column_names[i2]=='precimaVendorID'):
											where_phrase = " where precimaVendorID='" + str(item) + "'; "
											i = i + 1

								else:
									if (str(item)!='None' and str(item)!='nan'):
										update_sql = update_sql + column_names[i2] + "='" + str(item) + "' "

									else:
										update_sql = update_sql + column_names[i2] + "=NULL "

									if (i!=len(line)):
										update_sql = update_sql + ","

									i = i + 1

								i2 = i2 + 1

							update_sql = update_sql + where_phrase
							update_sql = update_sql + ";\n"
							print "\n" + update_sql
							cur.execute(update_sql)

					db.commit()
		#HD - explain high level logic used below.
		if  delete_list!=[]:
				db = MySQLdb.connect(host = mysqlhost,
					user = mysqluser,
					passwd = mysqlpw,
					db = mysqldb)
				cur = db.cursor()
				
				for item in delete_list:
					delete_sql = "DELETE FROM vendor_info WHERE precimaVendorID='"
					delete_sql = delete_sql + str(item) + "';\n"
				
					print "\n" + delete_sql
					cur.execute(delete_sql)

				db.commit()

		if (selected_vendor=="none"):
			return vendor_send(request)
		else:
			return offer_send(request)

@login_required
# HD - high level function definition
def offer_send(request):
	db = MySQLdb.connect(host = mysqlhost,
		user = mysqluser,
		passwd = mysqlpw,
		db = mysqldb)

	cur = db.cursor()

	if (len(current.objects.all())!=0):
			target = current.objects.all()[0]
			selected_supplier = target.vendor_id
			selected_camp = target.campaign_id
			clientname = target.clientname
			clientnum = target.clientnum
			target.offer_id = ""
			target.save()

	offer_sql = "select a.* , count(b.precimaskuID) as counter " \
				+ "from offer_info a left join sku_info b " \
				+ "on a.precimaofferID=b.precimaofferID " \
				+ "where a.precimaVendorID= '" + selected_supplier + "' " \
				+ "group by 1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23"

	
	cur.execute(offer_sql)  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	offer_data = [dict(itertools.izip(column_names, row)) for row in result]

	offer_list = []
	for item in result:
    		offer_list.append(item[21])



	db.close

	offer_info = json.dumps(offer_data,default=date_handler)

	if selected_camp=="" or selected_supplier=="":
		return render_to_response('error.html', {}, 
												context_instance=RequestContext(request))

	else:
		selected_camp = "\'" + selected_camp + "\'"
		selected_supplier = "\'" + selected_supplier + "\'"
		clientname = "'" + clientname + "'"
		clientnum = "'" + clientnum + "'"
	
		return render_to_response('offer.html', {"offer_info": offer_info, 
												"selected_camp": selected_camp, 
												"selected_supplier": selected_supplier,
												"clientname": clientname,
												"clientnum": clientnum,
												"offer_list": offer_list})


	#return HttpResponse("yo")

@login_required
# HD - high level function definition. there is a fair bit of reuse of logic in 
# the if statements below, highlight & comment what is unique for this code
def offer_receive(request):

	if request.method == 'POST':

		data = request.body
		read_data = json.loads(data)
		delete_list = read_data['delete_list']

		print read_data

		poid = read_data['poid']
		offernum = read_data['offernum']
		print poid
		print offernum

		if (poid!="none"): 
			if (len(current.objects.all())!=0):
				target = current.objects.all()[0]
				target.offer_id = poid
				target.offernum = offernum
				target.save()


		if (len(read_data['data'])!=0):
			insert_list = read_data['insert_list']
			update_list = read_data['update_list']
			

			db = MySQLdb.connect(host = mysqlhost,
				user = mysqluser,
				passwd = mysqlpw,
				db = mysqldb)
			cur = db.cursor()
	
			data_to_load = read_data['data']
			df = pd.read_json(json.dumps(data_to_load))
			df.fillna("")
			column_names =  df.columns.values.tolist()
			column_names.remove('$$hashKey')
			column_names.remove('id')
			column_names.remove('counter')
			del df['$$hashKey']
			del df['id']
			del df['counter']

			if len(insert_list) > 0:
					insert_df = df[df['precimaOfferID'].isin(insert_list)]
					print insert_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					insert_np = insert_df.as_matrix()
					insert_col =  str(df.columns.values.tolist())
					insert_col = insert_col.replace("[","(")
					insert_col = insert_col.replace("]",")")
					insert_col = insert_col.replace("u\'","")
					insert_col = insert_col.replace("\'","")
					print insert_col
	
					
					for line in insert_np:
							i = 1
							insert_sql = "INSERT INTO offer_info " + insert_col + " values ("
							print insert_sql

							val = ""
							for item in line:
								if (str(item)=='None' or str(item)=='nan'):
									val = val + "NULL"
									if (i != len(column_names)):
										val = val + ","
								else:
									val = val + "'" + str(item) + "'"
									if (i != len(column_names)):
										val = val + ","
								i = i + 1

							insert_sql = insert_sql + val + ");\n"
							print "\n" + insert_sql
							cur.execute(insert_sql)

					db.commit()

			if len(update_list) > 0:
					update_df = df[df['precimaOfferID'].isin(update_list)]
					print update_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					update_np = update_df.as_matrix()
	
					
					for line in update_np:
							i2 = 0
							i = 1
							update_sql = "UPDATE offer_info SET "
							good_values = 0
							for item in line:
								if (str(item)!='None' and str(item)!='nan'):
										good_values = good_values + 1
							print good_values
							for item in line:
								if (str(item)!='None' and str(item)!='nan'):
										if (column_names[i2]=='precimaOfferID'):
											where_phrase = " where precimaOfferID='" + str(item) + "'; "
											i = i + 1
										else:
											update_sql = update_sql + column_names[i2] + "='" + str(item) + "' "
										
											if (i!=good_values):

												update_sql = update_sql + ", "
												i = i + 1
												print "i =" + str(i)
											print column_names[i2] + ": " + str(item)
								i2 = i2 + 1

							update_sql = update_sql + where_phrase
							update_sql = update_sql + "\n"
							print "\n" + update_sql
							cur.execute(update_sql)

					db.commit()

		if delete_list!=[]:
				db = MySQLdb.connect(host = mysqlhost,
					user = mysqluser,
					passwd = mysqlpw,
					db = mysqldb)
				cur = db.cursor()

				for item in delete_list:
					delete_sql = "DELETE FROM offer_info WHERE precimaOfferID='"
					delete_sql = delete_sql + str(item) + "';\n"
				
					print "\n" + delete_sql
					cur.execute(delete_sql)

				db.commit()

		if (poid=="none"):
			return offer_send(request)
		else:
			return product_send(request)

@login_required		
# HD - high level function definition. additional comments for unique if statements
def product_send(request):
	db = MySQLdb.connect(host = mysqlhost,
		user = mysqluser,
		passwd = mysqlpw,
		db = mysqldb)

	cur = db.cursor()

	if (len(current.objects.all())!=0):
			target = current.objects.all()[0]
			selected_offer = target.offer_id
			selected_vendor = target.vendor_id
			selected_campaign = target.campaign_id
			clientname = target.clientname
			clientnum = target.clientnum
			offernum = target.offernum

	product_sql = "SELECT * FROM SKU_INFO WHERE precimaOfferID="
	product_sql = product_sql + "\'" + selected_offer + "\';\n"
	
	cur.execute(product_sql)  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	product_data = [dict(itertools.izip(column_names, row)) for row in result]

	product_list = []
	for item in result:
    		product_list.append(item[3])

   	item_sql = "SELECT item as itemno, ean, item_desc, div_name, grp_name, dept_name, " \
   				+ "class_name, subclass_name, brand_desc " \
   				+ "FROM item WHERE " \
   				+ "parent_supl_num ='" + clientnum + "';"

   	cur.execute(item_sql)
   	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	item_data = [dict(itertools.izip(column_names, row)) for row in result]
	

	db.close

	product_info = json.dumps(product_data,default=date_handler)
	item_info = json.dumps(item_data,default=date_handler)

	if selected_offer=="" or selected_vendor==""  or selected_campaign=="":
		return render_to_response('error.html', {}, 
												context_instance=RequestContext(request))

	else:
		selected_offer = "\'" + selected_offer + "\'"
		selected_vendor = "\'" + selected_vendor + "\'"
		selected_campaign = "\'" + selected_campaign + "\'"
		clientname = "'" + clientname + "'"
		clientnum = "'" + clientnum + "'"
	
	return render_to_response('product.html', {"product_info": product_info, 
												"product_list":product_list, 
												"selected_offer":selected_offer,
												"selected_vendor":selected_vendor,
												"clientname": clientname,
												"clientnum": clientnum,
												"offernum" : offernum,
												"selected_campaign":selected_campaign,
												"item_info": item_info})



@login_required
# HD - high level function definition
def product_receive(request):
	
	if request.method == 'POST':

		data = request.body
		read_data = json.loads(data)
		delete_list = read_data['delete_list']


		if (len(read_data['data'])!=0):
			insert_list = read_data['insert_list']
			update_list = read_data['update_list']


			db = MySQLdb.connect(host = mysqlhost,
				user = mysqluser,
				passwd = mysqlpw,
				db = mysqldb)
			cur = db.cursor()
	
			data_to_load = read_data['data']
			df = pd.read_json(json.dumps(data_to_load))
			df.fillna("")
			column_names =  df.columns.values.tolist()
			column_names.remove('$$hashKey')
			column_names.remove('id')
			del df['$$hashKey']
			del df['id']

			if len(insert_list) > 0:
					insert_df = df[df['precimaSkuID'].isin(insert_list)]
					print insert_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					insert_np = insert_df.as_matrix()
					insert_col =  str(df.columns.values.tolist())
					insert_col = insert_col.replace("[","(")
					insert_col = insert_col.replace("]",")")
					insert_col = insert_col.replace("u\'","")
					insert_col = insert_col.replace("\'","")
					print insert_col
	
					
					for line in insert_np:
							i = 1
							insert_sql = "INSERT INTO sku_info " + insert_col + " values ("
							print insert_sql

							val = ""
							for item in line:
								if (str(item)=='None' or str(item)=='nan'):
									val = val + "NULL"
									if (i != len(column_names)):
										val = val + ","
								else:
									val = val + "'" + str(item) + "'"
									if (i != len(column_names)):
										val = val + ","
								i = i + 1

							insert_sql = insert_sql + val + ");\n"
							print "\n" + insert_sql
							cur.execute(insert_sql)

					db.commit()

			if len(update_list) > 0:
					update_df = df[df['precimaSkuID'].isin(update_list)]
					print update_df
					print "##########################"
					i = 0

					db = MySQLdb.connect(host = mysqlhost,
							user = mysqluser,
							passwd = mysqlpw,
							db = mysqldb)
					cur = db.cursor()
					update_np = update_df.as_matrix()
	
					
					for line in update_np:
							i2 = 0
							i = 1
							update_sql = "UPDATE sku_info SET "
							good_values = 0
							for item in line:
								if (str(item)!='None' and str(item)!='nan'):
										good_values = good_values + 1
							print good_values
							for item in line:
								if (str(item)!='None' and str(item)!='nan'):
										if (column_names[i2]=='precimaSkuID'):
											where_phrase = " where precimaSkuID='" + str(item) + "'; "
											i = i + 1
										else:
											update_sql = update_sql + column_names[i2] + "='" + str(item) + "' "
										
											if (i!=good_values):

												update_sql = update_sql + ", "
												i = i + 1
												print "i =" + str(i)
											print column_names[i2] + ": " + str(item)
								i2 = i2 + 1

							update_sql = update_sql + where_phrase
							update_sql = update_sql + ";\n"
							print "\n" + update_sql
							cur.execute(update_sql)

					db.commit()

		if delete_list!=[]:
				db = MySQLdb.connect(host = mysqlhost,
					user = mysqluser,
					passwd = mysqlpw,
					db = mysqldb)
				cur = db.cursor()

				for item in delete_list:
					delete_sql = "DELETE FROM vendor_info WHERE precimaSkuID='"
					delete_sql = delete_sql + str(item) + "';\n"
				
					print "\n" + delete_sql
					cur.execute(delete_sql)

				db.commit()

		return offer_send(request)


# HD - high level function definition-- is this required for production use or for only development?
def test(request):
	db = MySQLdb.connect(host = mysqlhost,
		user = mysqluser,
		passwd = mysqlpw,
		db = mysqldb)

	cur = db.cursor()
	cur.execute("SELECT * FROM vendor_info")  
	desc = cur.description
	column_names = [col[0] for col in desc]
	result = cur.fetchall()
	data = [dict(itertools.izip(column_names, row)) for row in result]
	
	db.close

	campaign_info = json.dumps(data,default=date_handler)
	return render_to_response('test.html', {"campaign_info": campaign_info}, context_instance=RequestContext(request))



from forms import UserForm

# HD - assuming you are using an opensource function, how are you using it within the app logic? Context
def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render(request,
            'register.html',
            {'user_form': user_form, 'registered': registered} )

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
# HD - assuming you are using an opensource function, how are you using it within the app logic?
def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/home/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'login.html', {})


from django.contrib.auth import logout

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
# HD - assuming you are using an opensource function, how are you using it within the app logic?
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    if (len(current.objects.all())!=0):
			target = current.objects.all()[0]

			target.campaign_id = ""
			target.vendor_id = ""
			target.clientname = ""
			target.clientnum = ""
			target.offer_id = ""
			target.offernum = ""
			target.product_id = ""

			target.save()

    # Take the user back to the homepage.
    return HttpResponseRedirect('/login/')



import excel_export
import xlsxwriter as xw
@login_required
# HD - assuming you are using an opensource function, how are you using it within the app logic?
def excel_file(request):
	if request.method == 'POST':
		data = request.body
		print data
		target = current.objects.all()[0]
		selected_vendor = target.vendor_id
		excel_export.export_file(selected_vendor)
	

		if data == 'offer':	
			return offer_send(request)
		else:
			return product_send(request)



@login_required
def export_page(request):
	return render_to_response('export.html')
