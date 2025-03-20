def read_csv(csvfilename):
    rows = ()
    with open(csvfilename, encoding="utf8") as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows += (tuple(row), )
    return rows

f = read_csv("tripadvisor.csv")