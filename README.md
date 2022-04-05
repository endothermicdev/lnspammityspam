# lnspammityspam
Analysis and Documentation of Rate-limited LN Gossip

This script scans a clightning log for entries of rate-limited gossip. It
does some basic analysis on the found channel updates and node announcements.

Before parsing a log file, make sure the core-lightning node is configured with
at least log-level=debug:gossipd in order to catch rate-limiting.

Copy a core-lightning debug.log file to the working directory before running
spamanalysis.py or enter the location as a commandline argument.

The CLN working directory and log file information can be found with the
core-lightning cli:
$lightning-cli listconfigs

Specifically, the entire path and file is returned with:
lightning-cli listconfigs | jq -r '. | {"lightning-dir", "log-file"} | join("/bitcoin/")'

