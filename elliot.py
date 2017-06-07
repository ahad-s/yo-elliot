import csv
from datetime import datetime, timedelta

now = datetime.now()
max_date = now + timedelta(days=7)
strf = "%Y-%m-%d %H:%M:%S"
days = [[] for i in xrange(7)] # dates for the 7 days

# assume user is only busy for one day period at a time
# i.e. cant be busy from 2am Tues -> 2am Wed

with open('calandar.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=",")
	for row in reader:
		usr, busy_start, busy_end = row

		d_start = datetime.strptime(busy_start, strf)
		d_end = datetime.strptime(busy_end, strf)

		# only care about meetings for the next 7 days
		if d_start.date() > max_date.date() or \
			d_start.date() < now.date(): 
			continue

		day_slot = (d_start.date() - now.date()).days
		days[day_slot].append((d_start, d_end))

def compare(a, b):
	if a[0] > b[0]:
		return 1
	elif a[0] < b[0]:
		return -1
	else:
		if a[1] > b[1]:
			return 1
		elif a[1] < b[1]:
			return -1
		return 0

for idx, d in enumerate(days):
	if len(d) > 0:
		days[idx] = sorted(d, cmp=compare)

avails = []

overallmaxdelta = None
overallmaxstart = None
overallmaxend = None

for idx, day in enumerate(days):

	maxstart = None
	maxend = None
	maxdelta = None

	prevstart = None
	prevend = None

	currdayBEG = datetime(now.year, now.month, now.day, 8) \
					+ timedelta(days=idx)
	currdayEND = datetime(now.year, now.month, now.day, 22) \
					+ timedelta(days=idx)


	for idx in xrange(0, len(day)):
		if prevstart is None:

			prevstart = day[idx][0]
			prevend = day[idx][1]

			if prevstart > currdayBEG:
				maxdelta = prevstart  - currdayBEG
				maxstart = currdayBEG
				maxend = prevstart
			continue

		currstart = day[idx][0]
		currend = day[idx][1]

		# if overlapping busy people, extend busy period
		if prevend > currstart:
			prevend = currend
			continue
		else: # new free period!
			# if possible free period ends before 8am
			if currend < currdayBEG: 
				prevend = currend
				continue

			possibledelta = currstart - max(prevend, currdayBEG)

			if maxdelta is None or possibledelta > maxdelta:
				maxdelta, maxstart, maxend = possibledelta, max(prevend, currdayBEG), currstart

			prevend = currend


	# no one busy on this day
	if prevend is None: 
		maxend = currdayEND
		maxstart = currdayBEG
		maxdelta = currdayEND - currdayBEG
	# check possible slot between last person and 10pm
	elif (len(day) > 0 and \
		(currdayEND > max(currdayBEG, prevend))) or maxdelta is None:
		m = min(max(prevend, currdayBEG), currdayEND) # might have date past 10pm
		if maxdelta is None or currdayEND-m > maxdelta:
			maxdelta, maxstart, maxend = currdayEND-m, prevend, currdayEND

	# gives us the max free day slots in each day
	avails.append((maxdelta, maxstart, maxend))

	if overallmaxdelta is None or maxdelta > overallmaxdelta:
		overallmaxdelta = maxdelta
		overallmaxend = maxend
		overallmaxstart = maxstart

if overallmaxdelta is None:
	print "All the days are free!"
else:
	print "Best time for a meeting in the week:"
	print overallmaxstart,"to", overallmaxend


print "\nMaximum available meeting times for each day:"
for idx, (delta, start, end) in enumerate(avails):
	if end > start:
		print start, "to", end
	else:
		print "no possible time on", (now + timedelta(days=idx)).date()
