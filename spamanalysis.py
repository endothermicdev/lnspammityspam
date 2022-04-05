#!/usr/bin/python3
#quantifying rate limiting incidences of gossip traffic by parsing clightning
#log file.
#copy cl.log to working directory, or add log path and filename as a commandline
#arg.

import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
#log is simply put in the same directory
log_src = os.path.join(__location__,"cl.log")

import sys
if len(sys.argv) > 1:
    log_src = str(sys.argv[1])
print("looking for log file {}".format(log_src))

# I was asked to check for spam updates from a particular node's channels
# This will import those form a file in the same directory.
# It should be formatted with one SCID per line similar to:
# 686771x950x0/0
# These are stored as strings and later matched with the log file, so channel
# half is optional here.
chan_src = os.path.join(__location__,"channels.txt")
if os.path.isfile(chan_src):
    node_check_chans = []
    with open(chan_src) as f:
        for l in f:
            if len(l) > 5:
                node_check_chans.append(l.strip())
    print("node check channel list:")
    for l in node_check_chans:
        print("   {}".format(l))

def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])
with open(log_src, 'rb') as f:
    t = tail(f).decode('ascii')
lines = t.splitlines()
last_line = ' '.join(lines[-1].split())
log_end = last_line.split("Z")[0]
log_end = log_end.split(":")[0]
print("log end:",log_end)

#anything in the log before this timestamp is ignored.
from datetime import datetime, timedelta
fmt = '%Y-%m-%dT%H'
delta = timedelta(hours = -336) #14 days
start_time = (datetime.strptime(log_end,fmt) + delta).strftime(fmt)
print("log_start:", start_time)

log = []
spam = 0
lines = 0
cupdates = 0
nannounce = 0
ignoring = True
with open(log_src) as f:
    for line in f:
        if ignoring:
            if line[0:13] != start_time:
                pass
            else:
                print("found start time.")
                print(line)
                ignoring = False
        else:
            lines += 1
            if "Received channel_update" in line:
                cupdates += 1
            if "Received node_announcement" in line:
                nannounce += 1
            if "spammy" in line:
                spam += 1
                log.append(' '.join(line.split()))
log_start = log[0].split("Z")[0]
log_end = log[-1].split("Z")[0]
fmt2 = fmt + ":%M:%S.%f"
t_diff = datetime.strptime(log_end,fmt2) - datetime.strptime(log_start,fmt2)
t_diff = t_diff.total_seconds()/3600
print("spam found: {} of {} log entries.".format(spam, lines))
print("{} valid node announcements found of {} log entries.".format(nannounce, lines))
print("{} valid channel updates found of {} log entries.".format(cupdates, lines))
print("total valid channel updates/hr: {:.1f}".format(cupdates/t_diff))
print("log file processing start:",log_start)
print("log file processing end:",log_end)
print("log time = {:.2f} hrs".format(t_diff))

#stored as tuple(SCID,timestamp)
updates = []
#stored as tuple(channel_id,timestamp)
announcements = []
for e in log:
    if "update" in e:
        up = e.split(" ")
        updates.append((up[7],up[11][:-1]))
    elif "nannounce" in e:
        an  = e.split(" ")
        #print(an)
        announcements.append((an[7],an[11][:-1]))
print("spam updates and node announcements filtered to lists.")

#remove duplicate spam coming from different peers
updates_filtered = []
updates_filtered = set(updates)
print("updates filtered for duplicates:",len(updates_filtered))

#remove duplicate spam coming from different peers
announcements_filtered = []
announcements_filtered = set(announcements)
print("announcements filtered for duplicates:",len(announcements_filtered))
#print(updates[0])
#print(announcements[0])
print("total spam updates: {}".format(len(updates)))
print("total filtered spam updates: {}".format(len(updates_filtered)))
print("total spam announcements: {}".format(len(announcements)))
print("total filtered spam announcements: {}".format(len(announcements_filtered)))
print("total spam updates/hr: {:.1f}".format(len(updates_filtered)/t_diff))
print("total spam announcements/hr: {:.1f}".format(len(announcements_filtered)/t_diff))
#unique by SCID
unique_spammy_channels = []
uf = []
for u in updates_filtered:
    uf.append(u[0]) #grab only the SCID
unique_spammy_channels = set(uf)
print("unique spammy channels:",len(unique_spammy_channels))

channel_tally = {}
for u in unique_spammy_channels:
    channel_tally.update({u:0})
for u in updates_filtered:
    channel_tally[u[0]] += 1
aFewChannels14 = [] #I want a handful of samples with 14 spam updates
aFewChannels56 = []
occurence = []
for k,v in channel_tally.items():
    occurence.append(v)
    if len(aFewChannels14) < 6:
        if v == 14:
            aFewChannels14.append(k)
    if len(aFewChannels56) < 6:
        if v == 56:
            aFewChannels56.append(k)
print("selected channels with 14 spam updates:")
for c in aFewChannels14:
    print("\t{}".format(c))
print("selected channels with 56 spam updates:")
for c in aFewChannels56:
    print("\t{}".format(c))
histogram = []
hist_max = 50
for r in range(0,hist_max+1):
    histogram.append(0)
for n,o in enumerate(occurence):
    if o > (hist_max - 1):
        #print("channel {} exceeds {} with {} updates".format(n, hist_max-1, o))
        histogram[hist_max] += 1
    else:
        histogram[o] += 1
print("histogram data:")
tsu = len(unique_spammy_channels)
histpct = 0
for n,c in enumerate(histogram[0:hist_max]):
    histpct += c/tsu
    print("{:>3}: {:>4} {:>6.1%}".format(n,c,histpct))
#special treatment for the "exceeds maximum" group
histpct += histogram[hist_max]/tsu
print("{}+: {:>4} {:>6.1%}".format(hist_max,histogram[hist_max],histpct))
# Check requested channels if file was imported.
try:
    if node_check_chans:
        print("Node analysis:")
        for k, v in channel_tally.items():
            if k in node_check_chans:
                print("  chan {} rate limited {} times".format(k,v))
except NameError:
    pass
