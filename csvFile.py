import csv 
from collections import Counter, defaultdict, OrderedDict
counter = 0
entries = []
duplicate_entries = []

with open('C:\\Users\\vasile.belmega\\Desktop\\projects\\python\\FullDatasetResult.csv','r') as csv_file:
	for row in csv_file:
		columns = row.strip().split(',')
		counter=counter+1
		print(counter)
		for substr in columns:
			if substr not in entries:
				entries.append("{}\n".format(substr))
				
			else:
				duplicate_entries.append(substr)
				
if len(entries) > 0:
	with open('C:\\Users\\vasile.belmega\\Desktop\\projects\\python\\Result.csv', 'a') as out_file:
		for line in entries:
			out_file.write(line)
else:
	print("no repetition")
	
print(done)
