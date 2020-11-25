#import inspect
import csv
import os.path

def printResults(*arg, **kwarg):
    for key in kwarg:
        print(f"{key}={kwarg[key]}")

def getHighestAllowResult(results):
    max_value = 0
    max_value_d = None
    for d in results:
        if d["allow"] > max_value:
            max_value = d["allow"]
            max_value_d = d
    return max_value_d

def saveResultsToCSV(results):
    with open("results.csv", mode="w", newline='', encoding='utf-8') as csv_file:
        header_names = ['D', 'w', 't', 'allow', 'MS']
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header_names)
        for result in results:
            writer.writerow([result[a] for a in header_names])

def doResultsExist():
    return os.path.exists(os.path.relpath("./results.csv"))

def readResultsFromCSV():
    results = []
    line_count = 0
    with open("results.csv", mode="r", newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        first = True
        for r in csv_reader:
            if first:
                first = False
            else:
                results.append({"D": float(r[0]), "w": float(r[1]), "t": float(r[2]), "allow": float(r[3]), "MS": float(r[4])})
                line_count += 1
        print(f'Processed {line_count} lines.')
    return results, line_count