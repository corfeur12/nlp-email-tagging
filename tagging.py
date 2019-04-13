from os import listdir, makedirs
from os.path import isfile, join, exists

untaggedTextFilesPath = 'untagged/'
outputFilesPath = 'tagged'
if not exists(outputFilesPath):
    makedirs(outputFilesPath)
untaggedTextFilesList = [f for f in listdir(untaggedTextFilesPath) if isfile(join(untaggedTextFilesPath, f))]

for untaggedTextFileName in untaggedTextFilesList:
    pathToRead = join(untaggedTextFilesPath, untaggedTextFileName)
    fileToRead = open(pathToRead, 'r')
    print(untaggedTextFileName)
    untaggedTextFileText = fileToRead.read()
