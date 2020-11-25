#import inspect
import csv

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
    with open("results.csv", mode="w") as csv_file:
        header_names = ['D', 'w', 't', 'allow', 'MS']
        writer = csv.DictWriter(csv_file, fieldnames=header_names)

        writer.writeheader()
        for result in results:
            writer.writerow(result)