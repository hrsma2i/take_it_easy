# -*- coding: utf-8 -*-
"""
download csv from gss
"""

from requests import get
import csv
import numpy as np
from datetime import datetime as dttm
from datetime import timedelta as tmdlt

def tmdlt2hm(tmdlt):
    return tmdlt.seconds//3600, (tmdlt.seconds//60)%60

def download_from_gss(csv_file="./schedule.csv", url_gss_file="./url_gss"):
    f = open(csv_file,'w')

    url = open(url_gss_file).readline().rstrip()
    s = get(url)
    f.write(s.content.decode('utf-8'))
    f.close()


    reader = csv.reader(csv_file)

    i_weekday= dttm.now().weekday()+1

    ls_duration = []
    ls_event = []
    event = ""

    # header
    next(reader)

    duration = tmdlt()
    for row in reader:
        tmp_event = row[i_weekday]
        
        if tmp_event != "":
            event = event.replace('\n', ' ')
            h,m = tmdlt2hm(duration)
            ls_duration.append("{}:{:02d}".format(h,m))
            ls_event.append(event)
            
            duration = tmdlt()
            event = tmp_event
            
        duration +=  tmdlt(minutes=30)
        
    h,m = tmdlt2hm(duration)
    ls_duration.append("{}:{:02d}".format(h,m))
    ls_event.append(event)


    # write to scv again
    ff = open(csv_file,'w')
    ff.write('6:00,\n')
    itr_dr_ev = zip(ls_duration, ls_event)
    # header
    next(itr_dr_ev)
    for dr, ev in itr_dr_ev:
        ff.write('{},{}\n'.format(dr,ev))
    ff.close()
