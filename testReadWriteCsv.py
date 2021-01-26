import csv
import os
from readWriteCsv import readCSV, writeCSV

my_file = './traWeightLoss1.csv'
data = readCSV(my_file)
for val in data:
	print(val)

writeFileName='./testWrite.csv'
writeCSV(data, writeFileName)
