#!/usr/bin/env python2.6
# encoding: utf-8
#
# iTunes XML to CSV.
# Written by Håkan Waara (hwaara@gmail.com), February 2011
#
# input: iTunes Library XML on STDIN
# output: CSV with interesting data (specify which track columns you are
# interested in).
#
# Only track data is saved. Playlist data is ignored.

import sys
import csv
import xml.etree.cElementTree as ET

METADATA_LEVEL = 1
GROUP_LEVEL = 2
TRACK_LEVEL = 3

# the iTunes XML track key/values we want to export
interesting_keys = [
    "Name",
    "Location",
    "Artist",
    "Album",
    "Track ID",
    "Total Time",
    "Date Added",
]
# make a hash lookup too, for speed.
interesting_keys_lookup = dict([(x, 1) for x in interesting_keys])

def run(input, output):
    # write CSV header. strip space from column names.
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([key.replace(" ", "") for key in interesting_keys])

    # state
    current_level = 0
    current_group = None
    current_info = {}
    current_key = None
    listen = False
    counter = 0
    for event, elem in ET.iterparse(input, events=("end", "start")):
        # remember at what level of <dict/>s we are
        if elem.tag == "dict":
            if event == "start":
                current_level += 1
            else:
                current_level -= 1
    
        # we don't care about start elements, except to keep track of level above.
        if event == "start":
            continue
    
        if current_level == METADATA_LEVEL:
            if elem.tag == "key":
                if elem.text == "Tracks":
                    listen = True
                elif elem.text == "Playlists":
                    listen = False
        elif current_level == TRACK_LEVEL and listen:
            # handle key
            if elem.tag == "key":
                if elem.text in interesting_keys_lookup:
                    current_key = elem.text
                else:
                    current_key = None
            # handle value
            elif current_key:
                # we got a value for the current key
                current_info[current_key] = elem.text
                current_key = None
        elif current_level == GROUP_LEVEL and listen:
            # handle finished row
            if elem.tag == "dict":
                if current_info:
                    writer.writerow([current_info.get(key, "").encode("utf-8") for key in interesting_keys])
                # clear current element when done, to save memory.
                elem.clear()

        # some progress output 
        counter += 1
        if counter % 4000 == 0:
            sys.stderr.write("%d elements parsed...\n" % counter)

if __name__ == "__main__":
    input = sys.stdin
    if len(sys.argv) > 1:
        # file specified instead of stdin. read from it.
        input = open(sys.argv[1], "rb")
    run(input=input, output=sys.stdout)
