import os
import urllib.parse

sent_query = urllib.parse.parse_qs(os.environ['QUERY_STRING'])

def greeter(name, surename):
    return('Hello ' + str(name).capitalize() + ' ' + str(surename).capitalize())

print("Content-Type: text/html\n")
print(str(sent_query))

