# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 11:36:55 2016

@author: chuang
"""

import xlsxwriter as xw
import MySQLdb
import pandas as pd

################################################
#                                              # 
#         For the offer table                  #
#                                              #
################################################


def export_file(selected_vendor):

mysqlhost = "djangomysqltest.ckeqhtrt4wyd.us-west-2.rds.amazonaws.com"
mysqluser = "morrisons"
mysqlpw = "morrisons"
mysqldb = "usf"
     
    db = MySQLdb.connect(host = mysqlhost,
            user = mysqluser,
            passwd = mysqlpw,
            db = mysqldb)
    
    cur = db.cursor()

    
    df = pd.read_sql("select distinct a.*, b.* " \
                + "from campaign_information a, vendor_info b " \
                + "where a.precimaCampaignID=b.precimaCampaignID and " \
                + "b.precimaVendorID='" + selected_vendor + "'"
        ,db)
    
    
    
    
    workbook = xw.Workbook('static/export.xlsx')
    worksheet = workbook.add_worksheet()
    
    #money value
    money = workbook.add_format({'num_format': u'£#,##0'})
    
    #bold
    bold = workbook.add_format({'bold': True})
    
    #left
    left = workbook.add_format({'align': 'left'})
    moneyleft = workbook.add_format({'align': 'left', 'num_format': u'£#,##0'})
    
    worksheet.write('A2','Morrisons Loyalty Driver Promotion Specofication Form', bold)
    worksheet.set_column('A:A', 50)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 20)
    worksheet.set_column('H:H', 20)
    worksheet.set_column('I:I', 20)
    worksheet.set_column('J:J', 20)
    worksheet.set_column('K:K', 20)
    worksheet.set_column('L:L', 20)
    worksheet.set_column('M:M', 20)
    worksheet.set_column('N:N', 20)
    worksheet.set_column('O:O', 20)
    worksheet.set_column('P:P', 20)
    worksheet.set_column('Q:Q', 20)
    worksheet.set_column('R:R', 20)
    worksheet.set_column('S:S', 20)
    worksheet.set_column('T:T', 20)
    worksheet.set_column('U:U', 20)
    worksheet.set_column('V:V', 20)
    
    worksheet.write('A4','Submission Date:')
    worksheet.write('B4', str(df.ix[0].submissionDate))
    
    worksheet.write('F2', 'Files confirmed in correct form')
    worksheet.write('F3', 'Name of Verifier')
    worksheet.write('F4', 'Date')
    
    worksheet.write('A6','Company Information', bold)
    worksheet.write('B6','Precima', bold)
    worksheet.write('D6','Participating Supplier', bold)
    
    worksheet.write('A8','Contact Name')
    worksheet.write('A9','Contact Number')
    worksheet.write('A10','Contact Email')
    
    worksheet.write('B8', df.ix[0].supplierContactName)
    worksheet.write('B9', df.ix[0].supplierContactNumber, left)
    worksheet.write('B10', df.ix[0].supplierContactEmail)
    
    worksheet.write('D8', df.ix[0].precimaContactName)
    worksheet.write('D9', df.ix[0].precimaContactNumber, left)
    worksheet.write('D10', df.ix[0].precimaContactEmail)
    
    worksheet.write('A12','Client Number')
    worksheet.write('A13','Client Name')
    
    worksheet.write('B12', df.ix[0].parentSupplierNumber)
    worksheet.write('B13', df.ix[0].parentSupplierName)
    
    timeframe = (df.ix[0].startDate).strftime('%b %d, %Y - ') \
                + (df.ix[0].endDate).strftime('%b %d, %Y')
    
    worksheet.write('A15','Participation Timeframe', bold)
    worksheet.write('B15', timeframe)
    worksheet.write('A16','Campaign Start Date')
    worksheet.write('B16', str(df.ix[0].startDate), left)
    worksheet.write('A17','Campaign End Date')
    worksheet.write('B17', str(df.ix[0].endDate))
    worksheet.write('A18','Campaign Type')
    worksheet.write('B18', df.ix[0].campaignTypeDesc)
    worksheet.write('A19','Max Campaign Client Fee')
    worksheet.write('B19', df.ix[0].maxCampaignClientFee, left)
    
    worksheet.write('C19','Cost Per Delivered Offer')
    worksheet.write('D19', df.ix[0].costPerDeliveredOffer, moneyleft)
    
    
    worksheet.write('A21','Admin Only (Unique Campaign ID)', bold)
    worksheet.write('B21','Offer Number', bold)
    worksheet.write('C21','Bar Code 1', bold)
    worksheet.write('D21','Valassis Code 1', bold)
    worksheet.write('E21','Unica Code', bold)
    worksheet.write('F21','Bar Code 2', bold)
    worksheet.write('G21','Valassis Code 2', bold)
    worksheet.write('H21','E-Code', bold)
    worksheet.write('I21','Brand Name', bold)
    worksheet.write('J21','Item #', bold)
    worksheet.write('K21','Promoted Item EAN #\'s', bold)
    worksheet.write('L21','Offer Copy(Promoted Items + Exlcusions)', bold)
    worksheet.write('M21','Sub Copy', bold)
    worksheet.write('N21','Image ID-DM', bold)
    worksheet.write('O21','Image ID-Catalina', bold)
    worksheet.write('P21','Image ID-Email', bold)
    worksheet.write('Q21','Max Client Fees', bold)
    worksheet.write('R21','Min Incentive', bold)
    worksheet.write('S21','Max Incentive', bold)
    worksheet.write('T21','Max Points', bold)
    worksheet.write('U21','Min Points', bold)
    worksheet.write('V21','Placeholder for Ad ID', bold)
    
# HD - Does this SQL create a new DF
   
    df = pd.read_sql("select a.*, b.item, b.promotedItemEAN from offer_info a " + \
                "left join sku_info b " + \
                "on a.precimaofferid=b.precimaofferid " + \
                "where a.precimaVendorID='" + selected_vendor + "'"
                ,db)
        
    df.rename(columns={'item':'itemno'}, inplace=True)    

#HD - some explanation about the variables and logic used. Is this the actual promo data from row 23 onwards?
    if (len(df)>0):
        i1 = 0
        i2 = 21
        df_len = len(df)
        offernum = df.ix[0].precimaOfferNumber
        
        while i1 < df_len:
            
            if df.ix[i1].precimaOfferNumber!=offernum:
                offernum = df.ix[i1].precimaOfferNumber
                i2 = i2 + 1
            
            if (str(df.ix[i1].precimaCampaignID)!='nan'  and str(df.ix[i1].precimaCampaignID)!='None'):
                worksheet.write(i2, 0, df.ix[i1].precimaCampaignID, left)
                
            if (str(df.ix[i1].precimaOfferNumber)!='nan'  and str(df.ix[i1].precimaOfferNumber)!='None'):
                worksheet.write(i2, 1, df.ix[i1].precimaOfferNumber, left)
                
            if (str(df.ix[i1].barCode1)!='nan'  and str(df.ix[i1].barCode1)!='None'):
                worksheet.write(i2, 2, df.ix[i1].barCode1, left)
                
            if (str(df.ix[i1].valassisCode1)!='nan'  and str(df.ix[i1].valassisCode1)!='None'):
                worksheet.write(i2, 3, df.ix[i1].valassisCode1, left)
                
            if (str(df.ix[i1].unicaCode)!='nan'  and str(df.ix[i1].unicaCode)!='None'):
                worksheet.write(i2, 4, df.ix[i1].unicaCode, left)
                
            if (str(df.ix[i1].barCode2)!='nan'  and str(df.ix[i1].barCode2)!='None'):
                worksheet.write(i2, 5, df.ix[i1].barCode2, left)
                
            if (str(df.ix[i1].valassisCode2)!='nan'  and str(df.ix[i1].valassisCode2)!='None'):
                worksheet.write(i2, 6, df.ix[i1].valassisCode2, left)
                
            if (str(df.ix[i1].eCode)!='nan'  and str(df.ix[i1].eCode)!='None'):
                worksheet.write(i2, 7, df.ix[i1].eCode, left)
                
            if (str(df.ix[i1].brandName)!='nan' and str(df.ix[i1].brandName)!='None'):
                worksheet.write(i2, 8, df.ix[i1].brandName, left)
                
            if (str(df.ix[i1].itemno)!='nan' and str(df.ix[i1].itemno)!='None'):
                worksheet.write(i2, 9, df.ix[i1].itemno, left)
                
            if (str(df.ix[i1].promotedItemEAN)!='nan' and str(df.ix[i1].promotedItemEAN)!='None'):
                worksheet.write(i2, 10, df.ix[i1].promotedItemEAN, left)
                
            if (str(df.ix[i1].offerCopy)!='nan'  and str(df.ix[i1].offerCopy)!='None'):
                worksheet.write(i2, 11, df.ix[i1].offerCopy, left)

            if (str(df.ix[i1].subCopy)!='nan'  and str(df.ix[i1].subCopy)!='None'):
                worksheet.write(i2, 12, df.ix[i1].subCopy, left)
                
            if (str(df.ix[i1].imageIDDM)!='nan'  and str(df.ix[i1].imageIDDM)!='None'):
                worksheet.write(i2, 13, df.ix[i1].imageIDDM, left)
                
            if (str(df.ix[i1].imageIDCatalina)!='nan'  and str(df.ix[i1].imageIDCatalina)!='None'):
                worksheet.write(i2, 14, df.ix[i1].imageIDCatalina, left)
                
            if (str(df.ix[i1].imageIDEmail)!='nan'  and str(df.ix[i1].imageIDEmail)!='None'):
                worksheet.write(i2, 14, df.ix[i1].imageIDEmail, left)
                
            if (str(df.ix[i1].maxClientFee)!='nan'  and str(df.ix[i1].maxClientFee)!='None'):
                worksheet.write(i2, 16, df.ix[i1].maxClientFee, moneyleft)
                
            if (str(df.ix[i1].minIncentive)!='nan'  and str(df.ix[i1].minIncentive)!='None'):
                worksheet.write(i2, 17, df.ix[i1].minIncentive, left )
                
            if (str(df.ix[i1].maxIncentive)!='nan'  and str(df.ix[i1].maxIncentive)!='None'):
                worksheet.write(i2, 18, df.ix[i1].maxIncentive, left )
                
            if (str(df.ix[i1].minPoints)!='nan'  and str(df.ix[i1].minPoints)!='None'):
                worksheet.write(i2, 19, df.ix[i1].minPoints, left)
                
            if (str(df.ix[i1].maxPoints)!='nan'  and str(df.ix[i1].maxPoints)!='None'):
                worksheet.write(i2, 20, df.ix[i1].maxPoints, left)
                
            if (str(df.ix[i1].adID)!='nan'  and str(df.ix[i1].adID)!='None'):
                worksheet.write(i2, 21, df.ix[i1].adID, left)
            
            i1 = i1 + 1
            i2 = i2 + 1
    
    workbook.close()
