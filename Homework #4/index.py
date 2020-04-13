import csv

"""
Reads a csv file and returns a list of list
containing rows in the csv file and its entries,
including header row.
"""
def read_csv(csvfilename):
    rows = []

    with open(csvfilename) as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows