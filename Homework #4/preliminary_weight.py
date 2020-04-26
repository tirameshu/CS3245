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

def tried_to_find_g():
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

def printing_courts():
    with open("/Users/mandy/Desktop/NUS/CS3245/Homeworks/Homework #4/dataset/dataset.csv", 'r') as csvfile:
        file_reader = csv.DictReader(csvfile)

        i = 0

        for row in file_reader:

            if i == 100:
                break

            title = row["title"]
            date = row["date_posted"]
            court = row["court"]
            content = row["content"]

            print(court)

            i += 1

def get_courts():
    most_impt_courts = []
    less_impt_courts = []

    with open("Notes about Court Hierarchy.txt", 'r') as court_hierarchy:
        most_impt_flag = False
        less_impt_flag = False
        for line in court_hierarchy:
            line = line.strip()
            if line == "The rest":
                break
            elif line == "Most important":
                most_impt_flag = True
                continue
            elif line == "?Important?":
                less_impt_flag = True
                continue

            if most_impt_flag:
                if not line.strip():  # empty line, end of most impt courts
                    most_impt_flag = False
                else:  # still in most impt courts
                    most_impt_courts.append(line.strip())

            if less_impt_flag:
                if not line.strip():  # empty line, end of most impt courts
                    less_impt_flag = False
                else:  # still in most impt courts
                    less_impt_courts.append(line.strip())

    return most_impt_courts, less_impt_courts

"""
Sorts docIDs by whether any part of the query is in their title.

:param results: a list of docIDs
:param first: first metadata field to sort by
:param second: as above
:param third: as above

:return sorted docIDs according to param sequence.
"""
def sort_results_by_metadata(results, metadata, query_tokens):
    most_impt_courts, less_impt_courts = get_courts()

    doc_with_metadata = {} # Python3.7 onwards this preserves insertion order

    for docID in results:
        if docID not in doc_with_metadata: # prevents duplicate results
            title, year, court = metadata[docID]
            query_in_title = 0
            court_score = 0

            # if title contains query, give it a 1 and later sort in reverse order
            for token in query_tokens:
                if token in title:
                    # there are mostly no stopwords in free text query,
                    # and for phrasal search we assume all words matter,
                    # and for boolean searches, if stopwords exist, they
                    query_in_title = +1

            # if court is most impt, give score 2; less impt give score 1, others 0
            if court in most_impt_courts:
                court_score = 2
            elif court in less_impt_courts:
                court_score = 1

            doc_with_metadata[docID] = [query_in_title, year, court_score]

    doc_with_metadata = list(doc_with_metadata.items())
    doc_with_metadata.sort(key=lambda x: x[1][0], reverse=True) # first by how much of query is in title
    doc_with_metadata.sort(key=lambda x: x[1][1], reverse=True) # then by year, in desc order
    doc_with_metadata.sort(key=lambda x: x[1][2], reverse=True) # then by court, in desc order

    print(list(map(lambda x: x[0], doc_with_metadata))) # list of docIDs

metadata = {
    1: ["one", 1990, "SG Court of Appeal"],
    2: ["two", 1925, "UK Crown Court"],
    3: ["nth", 2013 , "some court"],
    4: ["four", 2010, "High Court of Australia"]
}

query_tokens = ["one", "two", "three", "four"]
sort_results_by_metadata([1, 2, 3, 4], metadata, query_tokens)