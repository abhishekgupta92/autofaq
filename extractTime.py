#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

months=['January','February','March','April','May','June','July','August','September','October','November','December']
months_lower=map(lambda a:a.lower(), months)

#Look for two digit numbers 0 to 31 and seperated by spaces
def getDate(query):
    query=query.replace(",","");
    try:
        date=re.search(r'([1-9]|0[1-9]|[12][0-9]|3[01])\s((j|J)((an|anuary)|(ul|uly))|(m|M)a((r|rch)|y)|(a|A)(ug|ugust)|(o|O)(ct|ctober)|(d|D)(ec|ecember)|(a|A)(pr|pril)|(j|J)(un|une)|((s|S)(ep|eptember)|(n|N)(ov|ovember))|(f|F)(eb|ebruary))\s(1[0-9][0-9][0-9]|2[0-9][0-9][0-9])', query).group(0)
        #n=re.match(r'(.*)([1-9]|0[1-9]|[12][0-9]|3[01])\s((j|J)((an|anuary)|(ul|uly))|(m|M)a((r|rch)|y)|(a|A)(ug|ugust)|(o|O)(ct|ctober)|(d|D)(ec|ecember)|(a|A)(pr|pril)|(j|J)(un|une)|((s|S)(ep|eptember)|(n|N)(ov|ovember))|(f|F)(eb|ebruary))\s(1[0-9][0-9][0-9]|2[0-9][0-9][0-9])', query).group(1)
        #date=m[len(n):]
        s=date.split();
        return (s[0],s[1],s[2])
    except:
        pass
    
    try:
        date=re.search(r'((j|J)((an|anuary)|(ul|uly))|(m|M)a((r|rch)|y)|(a|A)(ug|ugust)|(o|O)(ct|ctober)|(d|D)(ec|ecember)|(a|A)(pr|pril)|(j|J)(un|une)|((s|S)(ep|eptember)|(n|N)(ov|ovember))|(f|F)(eb|ebruary))\s([1-9]|0[1-9]|[12][0-9]|3[01])\s(1[0-9][0-9][0-9]|2[0-9][0-9][0-9])', query).group(0)
        #n=re.match(r'(.*)((j|J)((an|anuary)|(ul|uly))|(m|M)a((r|rch)|y)|(a|A)(ug|ugust)|(o|O)(ct|ctober)|(d|D)(ec|ecember)|(a|A)(pr|pril)|(j|J)(un|une)|((s|S)(ep|eptember)|(n|N)(ov|ovember))|(f|F)(eb|ebruary))\s([1-9]|0[1-9]|[12][0-9]|3[01])\s(1[0-9][0-9][0-9]|2[0-9][0-9][0-9])', query).group(1)
        #date=m[len(n):]
        s=date.split();
        return (s[1],s[0],s[2])
    except:
        pass
    
    return (None,None,None) 
    #re.match(r'(.+)(0[1-9]|[12][0-9]|3[01])\s((j|J)((an|anuary)|(ul|uly))|(m|M)a((r|rch)|y)|(a|A)(ug|ugust)|(o|O)(ct|ctober)|(d|D)(ec|ecember))\s[1-9][0-9]{3}|(0[1-9]|[12][0-9]|30)\s((a|A)(pr|pril)|(j|J)(un|une)|((s|S)(ep|eptember)|(n|N)(ov|ovember)))\s[1-9][0-9]{3}|(0[1-9]|1[0-9]|2[0-8])\s(f|F)(eb|ebruary)\s[1-9][0-9]{3}|29\s(f|F)(eb|ebruary)\s((0[48]|[2468][048]|[13579][26])00|[0-9]{2}(0[48]|[2468][048]|[13579][26]))(.+)',a).group(0)

def getMonth(query):
    cnt=0
    ans=""
    for i,month in enumerate(months):
        if query.lower().find(month.lower()) != -1:
            cnt+=1
            ans+=month
    if cnt==1:
        return ans
    return None

def giveYear(query):
    try:
        return int(re.search(r'14[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'15[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'16[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'17[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'18[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'19[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'20[0-9][0-9]',query).group(0))
    except:
        pass

    try:
        return int(re.search(r'21[0-9][0-9]',query).group(0))
    except:
        pass
    return None

def getYear(query):
    year1=giveYear(query)
    if year1==None:
        return None

    query=query.replace(str(year1),"")
    if giveYear(query)==None:
        return year1
    return None


