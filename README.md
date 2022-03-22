# lnspammityspam
Analysis and Documentation of Rate-limited LN Gossip

This script scans a clightning log for entries of rate-limited gossip. It
does some basic analysis on the found channel updates and node announcements.

copy a cl.log file to the working directory before running spamanalysis.py or
enter the location as a commandline argument. The clightning instance should be
set to log gossip or there will be nothing useful to parse.
