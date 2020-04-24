import csv
import nltk

csv.field_size_limit(1048576) # increase field size limit, number is eight times default limit, found by trial & error

def query_in(query, field):
    for q in query:
        if q in field:
            return True

    return False

def search(doc, query):
    with open("/Users/mandy/Desktop/NUS/CS3245/Homeworks/Homework #4/dataset/dataset.csv", 'r') as csvfile:
        file_reader = csv.DictReader(csvfile)
        for row in file_reader:
            docID = row["document_id"]

            if int(docID) == int(doc):
                title = row["title"]
                date = row["date_posted"]
                court = row["court"]
                content = row["content"]

                print("doc {d} found!".format(d=doc))
                print("is {query} in {field}?".format(query=query, field=title))
                print(query_in(query, title))

                print("is {query} in {field}?".format(query=query, field=date))
                print(query_in(query, date))

                print("is {query} in {field}?".format(query=query, field=date))
                print(query_in(query, court))

                print("query in content:")
                print(query_in(query, content))

                return

for i in range(1, 4):
    addr = "/Users/mandy/Desktop/NUS/CS3245/Homeworks/Homework #4/dataset/q{n}.txt".format(n=i)
    print("opening doc q{n}".format(n=i))
    with open(addr, 'r') as q:
        j = 0
        query = []
        for row in q:
            if j == 0:
                query = nltk.word_tokenize(row)
                print("processing query {q}".format(q=query))
            else:
                doc = row
                print("searching for doc {d}".format(d=doc))
                search(doc, query)

            j += 1

        print("query {q} done!".format(q=query))
