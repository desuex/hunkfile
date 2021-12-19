import csv


def readfile():
    with open('dialogimport.csv', 'r', newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            yield row


# data = list()
with open("Dialog.txt", 'w') as fp:
    for row in readfile():
        if row[0] == "Hash": continue
        fp.write("<Hash=0x"+row[0]+">\t"+row[3]+"\n")

# print(data[0])
