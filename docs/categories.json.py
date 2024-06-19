#!/usr/bin/env python3

# parse upload categories

# yeah i know, "parsing" html with regex is bad ...
# but this html is really simple

import re
import json

result = dict()

with open("docs/forms/upload.html", "r") as f:

    html = f.read()

    for groupname, optgroup in re.findall('<optgroup label="([^"]+)">(.*?)</optgroup>', html, re.S):

        result[groupname] = dict()

        #print(groupname, optgroup)

        for option_id, option in re.findall('<option value="([0-9]+)">([^<]+)</option>', optgroup, re.S):

            #print(option_id, option)

            assert str(int(option_id)) == option_id, f"bad option_id {option_id!r}"

            option_id = int(option_id)

            #result[groupname][option_id] = option
            result[groupname][option] = option_id

print(json.dumps(result, indent=4))
