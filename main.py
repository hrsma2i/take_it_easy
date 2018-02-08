import ui
import csv
from copy import copy, deepcopy
from datetime import *
from download_from_gss import download_from_gss

# String to
def str2hm(s):
    """
    # Parmas
    - s (String): e.g "6:30"

    # Return
    - hour (int): e.g. 6
    - minute (int): e.g. 30
    """
    hour, minute = [ int(t) for t in s.split(':') ]
    return hour, minute

def str2time(s):
    """
    String to time
    # Params
    - s (String): e.g "6:30"

    # Return
    - (datetime.time)
    """
    h,m = str2hm(s)
    return time(h,m)

def str2dttm(s):
    """
    String to datetime
    # Params
    - s (String): e.g "6:30"

    # Return
    - (datetime.datetime)
    """
    return datetime.combine(date.today(),str2time(s))

def str2tmdlt(s):
    """
    String to timedelta
    # Params
    - s (String): e.g "6:30"

    # Return
    - (datetime.timedelta)
    """
    h,m = str2hm(s)
    return timedelta(hours = h, minutes = m)


# to String
def time2str(t):
    """
    time to String
    # Params
    - (datetime.time)

    # Return
    - (String): e.g "6:30"
    """
    return time.strftime(t,'%H:%M')
	
def dttm2str(dttm):
    """
    datetime to String
    # Params
    - (datetime.datetime)

    # Return
    - (String): e.g "6:30"
    """
    return datetime.strftime(dttm,'%H:%M')

def tmdlt2str(tmdlt):
    """
    timedelta to String
    # Params
    - (datetime.timedelta)

    # Return
    - (String): e.g "6:30"
    """
    zero = datetime.combine(date.today(), time(0,0))
    return dttm2str(zero+tmdlt)

class Event:
    """
    # Params
    - name (str)
    - drtn_str (str): duration
    - drtn_tmdlt (datetime.timedelta): duration
    """
    def __init__(self,name,drtn_str):
        self.name = name 
        # drtn_str: duration string	
        if len(drtn_str) == 4:
                drtn_str = '0' + drtn_str
        self.drtn_str = drtn_str
        # drtn_tmdlt: duration timedelta
        self.drtn_tmdlt = str2tmdlt(drtn_str)

def evls2sch(eventlist, currenttime):
    """
    eventlist to schedule

    # Params
    - eventlist (list of Event)
    - currenttime (str): e.g. "6:30"
    
    # Return
    - schedule (list of str): is stored as TableView.data_source.items
    """
    schedule = []
    nexttime = str2dttm(currenttime)
    for event in eventlist:
        #scheduel's row
        row = dttm2str(nexttime) + ' | '
        row += event.drtn_str + ' | '
        row += event.name
        nexttime += event.drtn_tmdlt
        schedule.append(row)
    return schedule

def sch2evls(schedule):
    """
    eventlist to schedule

    # Params
    - schedule (list of str): is stored as TableView.data_source.items
    
    # Return
    - eventlist (list of Event)
    """
    eventlist = []
    for row in schedule:
            drtn_str = row[8:13]
            name = row[16:]
            eventlist.append(Event(name,drtn_str))
    return eventlist

def store_csv(eventlist):
    """
    store eventlist as csv

    # Params
    - eventlist (list of Event)
    - currenttime (str): e.g. "6:30"
    """
	
    global csv_file, currenttime
    F = open(csv_file,'w',encoding='utf-8')
    writer = csv.writer(F, lineterminator='\n')
    writer.writerow([currenttime])
    writer.writerows([[e.drtn_str, e.name] for e in eventlist])
    F.close()

def update_evls_from_sch(self):
    """ 
    ACTION METHOD: tv_schedule (TableView)

    When deleting/rearranging schedule,
            1. update eventlist
            2. store eventlist as csv

    # Params
    - self (tv_schedule.data_source): self.items is list of items (=schedule)
    """

    # update eventlist
    global eventlist
    eventlist = sch2evls(self.items)
    # store eventlist as csv
    store_csv(eventlist=eventlist)
    # reload tv_schedule
    update_sch_from_evls(eventlist=eventlist)

def update_sch_from_evls(eventlist):
    """
    update schedule from eventlist
    1. store eventlist as csv
    2. update schedule from eventlist
    """

    global tv_schedule
    # store eventlist as csv
    store_csv(eventlist=eventlist)
    # rewrite tv_schedule(table view) along with eventlist
    tv_schedule.data_source.items = evls2sch(eventlist=eventlist, currenttime=currenttime)
    tv_schedule.reload()

def send_event(self):
    """
    ACTION METHOD: bt_send (Button)

    1. add an event to eventlist
    2. update schedule from eventlist
    3. reset text fields
    """

    # add an event to eventlist
    global eventlist, tf_name, tf_duration, tv_schedule
    name = tf_name.text
    duration = tf_duration.text
    eventlist.append(Event(name,duration))
    # update schedule from eventlist
    update_sch_from_evls(eventlist)
    # reset text fields
    tf_name.text, tf_duration.text = '',''

def invert_edit(self):
    """
    ACTION METHOD: bt_edit (Button)

    Turn on/off edit mode.
    """
    
    global tv_schedule
    tv_schedule.editing = not(tv_schedule.editing)

def set_bookmark(self):
    """
    ACTION METHOD: bt_bookmark (Button)
    
    1. Download favrite csv_file
    2. Rewrite csv_file
    """
    global eventlist
    download_from_gss()
    load_csv_to_crtm_evls()
    update_sch_from_evls(eventlist)
	
def update_current(self):
    """
    ACTION METHOD: tf_current (TextField)

    update currenttime from tf_current.
    """

    global tv_schedule, currenttime
    currenttime = self.text
    tv_schedule.data_source.items = evls2sch(eventlist=eventlist, currenttime=currenttime)
    tv_schedule.reload()

def get_current(self):
    """
    ACTION METHOD: bt_get_current (Button)

    rewrites tf_current(TextField) as current time.
    """

    global tf_current
    # round minutes to 00 or 30
    h, m = str2hm(dttm2str(datetime.now()))
    if m < 15:
            m = 0
    elif m < 45:
            m = 30
    else:
            h, m = h+1, 0
    tf_current.text = tmdlt2str(timedelta(hours=h,minutes=m))
	
def all_delete(self):
    """
    ACTION METHOD: bt_alldelete (Button)

    delete all events from eventlist (changes eventlist as a empty list.)
    """
    global eventlist
    eventlist = []
    update_sch_from_evls(eventlist=eventlist)

class TextFiledDelegate(object):
	def textfield_did_begin_editing(self, textfield):
		global editview, mainview
		editview.y -= 250
		# show bt_get_current(Button)
		if textfield.name == 'tf_current':
			bt_get_current = ui.Button(
				name = 'bt_get_current',
				title = 'Get current',
				background_color = editview.background_color
			)
			# view's frame(x,y,width,height) can be decided after added to their parent view. Because the coordinats is relaitve to the parent view's coordinates.
			bt_get_current.width = 100
			bt_get_current.height = 50
			bt_get_current.action = get_current
			bt_get_current.x= mainview.width - bt_get_current.width
			bt_get_current.y= editview.y - bt_get_current.height
			mainview.add_subview(bt_get_current)
			
	def textfield_did_end_editing(self,textfield):
		global editview, mainview, eventlist
		editview.y += 250
		if textfield.name == 'tf_current':
			# hide bt_get_current
			mainview.remove_subview(mainview['bt_get_current'])
			store_csv(eventlist)

def load_csv_to_crtm_evls(csv_file="./schedule.csv"):
	global eventlist
	with open(csv_file,'r',encoding='utf-8') as f:
		reader = csv.reader(f)
		currenttime = next(reader)[0]
		for row in reader:
			eventlist.append(Event(row[1],row[0]))
			
	return currenttime, eventlist


if __name__=='__main__':
	csv_file = './schedule.csv'
	eventlist = []
	currenttime, eventlist = load_csv_to_crtm_evls(csv_file)
	
	mainview = ui.load_view()
	tv_schedule = mainview['tv_schedule']
	editview = mainview['editview']
	tf_current = editview['tf_current']
	tf_current.text = currenttime
	tf_current.keyboard_type = ui.KEYBOARD_NUMBERS
	tf_duration = editview['tf_duration']
	tf_duration.keyboard_type = ui.KEYBOARD_NUMBERS
	tf_name = editview['tf_name']

	schedule = copy(tv_schedule.data_source.items)

	# set textfields' delegate
	# Delegate is an obeject which type attribute view have.
	# It has an SPECIAL ACTION method that you implement
	# when you aren't satisfied with the timing of default view's action.
	tf_current.delegate = TextFiledDelegate()
	tf_name.delegate = TextFiledDelegate()
	tf_duration.delegate = TextFiledDelegate()

	tv_schedule.data_source.items = evls2sch(eventlist=eventlist,currenttime=currenttime)
	mainview.present(hide_title_bar=True)
