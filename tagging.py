from os import listdir, makedirs
from os.path import isfile, join, exists
import re
import sys
from nltk.tokenize import sent_tokenize


def tag_text(all_text, text_to_tag, tag_name):
    # set up the open and close for the tag
    # e.g. <tag> and </tag>
    tag_open = "<" + tag_name + ">"
    tag_close = "</" + tag_name + ">"
    # create the search expression with negative lookbehind and ahead to prevent double tagging
    # also makes use of non capturing groups for regex sub
    # e.g. (?<!<tag>)(some string here)(?!<\tag>)
    search_expression = r'(?<!' + tag_open + r')(' + re.escape(text_to_tag) + r')(?!' + tag_close + r')'
    # the text that will be inserted
    # the \1 is a backreference to whatever was found in the initial match of the regex
    substitution_text = tag_open + r'\1' + tag_close
    # uses re.IGNORECASE to make sure to match where necessary
    # TODO: check if re.IGNORECASE is needed
    return re.sub(search_expression, substitution_text, all_text, flags=re.IGNORECASE)


def tag_paragraphs(text):
    output = text
    # prevents over tagging of unnecessary information
    text_to_process = remove_email_text(output)
    # finds a new line followed by any letter then any characters then punctuation
    # positive lookahead for 2 new lines or the end of the document
    search_expression = r'''(?:^|\n)(?:\t?)(\w(?:.|\n{1})+?[.!?'"]+?)(?=\s*\n{2,}|\s*\n?$)'''
    all_paragraphs = re.findall(search_expression, text_to_process)
    for each in all_paragraphs:
        # tags each paragraph
        output = tag_text(output, each, 'paragraph')
    return output


def tag_sentences(text):
    output = text
    # only tags within paragraph tags
    search_expression = r'(?:<paragraph>)((?:.|\n)*?)(?:<\/paragraph>)'
    paragraphs = re.findall(search_expression, text)
    # iterate over paragraph text
    for p in paragraphs:
        # tokenize the sentences
        sentences = sent_tokenize(p)
        for s in sentences:
            # tag each sentence
            output = tag_text(output, s, 'sentence')
    return output


def remove_single_new_lines(text):
    # negative lookahead and lookbehind for \n
    search_expression = r'(?:^|[^\n])(\n)(?!\n)'
    output = re.sub(search_expression, " ", text)
    return output


def tag_times(text):
    output = text
    # look for lines containing the 'time:' (with/without an s)
    search_expression = r'(?:\s*times?:\s*)(.+?)(?:\s)*(?:\n|$)'
    times_set_initial = set(re.findall(search_expression, text, flags=re.IGNORECASE))
    times_set_extracted = set()
    if len(times_set_initial) == 0:
        # TODO maybe scan paragraph tags
        # maybe don't worry as none of these has this issues
        # apart from 485.txt which is an empty file check
        # has to do something
        print(":(")
    else:
        # set so as to not have duplicates
        times_24_hour = set()
        for times in times_set_initial:
            # TODO times -> 24 hour, compare times, check if 2 unique times exist, if yes tag, else ???
            extracted_times = extract_times(times)
            for time in extracted_times:
                times_set_extracted.add(time)
                times_24_hour.add(time_to_24_hour_format(time))
        print(times_set_initial)
        print(times_set_extracted)
        print(times_24_hour)
        # if only 2 times exist then assume they have to be the start and end times
        if len(times_24_hour) == 2:
            time_first = times_24_hour.pop()
            time_second = times_24_hour.pop()
            # check which time is earlier
            # swaps if necessary
            if time_first[0] > time_second[0]:
                time_first, time_second = time_second, time_first
            elif time_first[0] == time_second[0] and time_first[1] > time_second[1]:
                time_first, time_second = time_second, time_first
            # tags the text
            output = tag_equivalent_times(output, time_first, times_set_extracted, 'stime')
            output = tag_equivalent_times(output, time_second, times_set_extracted, 'etime')
    return output


def tag_equivalent_times(text, time, times_set, tag_name):
    output = text
    times_sorted = list(times_set)
    # sorted by longest to shortest
    # prevents partial tagging for sort of repeats
    # e.g. prevents '<stime>5:00</stime> P.M.' if 5:00 came first in the set
    # should be '<stime>5:00 P.M.</stime>'
    times_sorted.sort(key=len, reverse=True)
    for check_time in times_sorted:
        if time == time_to_24_hour_format(check_time):
            output = tag_text(output, check_time, tag_name)
    return output


def extract_times(text):
    search_expression = r'(?:^|\s|-)+(' + TIME_REGEX + r')(?:\b|\n|\r|\s)'
    return re.findall(search_expression, text, re.IGNORECASE)


def time_to_24_hour_format(time):
    partial_time = time
    hour = int(re.findall(r'(?:^|\s)\d+', partial_time)[0])
    partial_time = re.sub(r'(?:^|\s)\d+', '', partial_time)
    try:
        minute = int(re.findall(r'\d+', partial_time)[0])
    except (TypeError, IndexError):
        minute = 0
    if len(re.findall(r'(p\.?m\.?)', partial_time, re.IGNORECASE)) != 0:
        hour = int(hour) + 12
    time_tuple = (hour, minute)
    return time_tuple


def remove_email_text(text):
    # remove lines surrounded by < and > or any word followed by a :
    search_expression = r'(?:\n|^)((?:<.*>)|(?:[^\S\n]*\w+:.*))'
    text = re.sub(search_expression, "", text)
    # remove lines with no text but some symbols
    search_expression = r'(?:^|\n)([^\w\d\n]+)(?:$|\n)'
    text = re.sub(search_expression, "", text)
    # remove lines with lots of whitespace before text
    search_expression = r'(?:^)(?!\t\w)([^\S\n]{2,}[\w\d\t \r]+.*)(?:$)'
    text = re.sub(search_expression, "", text, flags=re.MULTILINE)
    # remove lines with lots of whitespace in the middle
    search_expression = r'(?:^|\n)(\w.+?[^\S\n]{6,}.+?\w)(?:$|\n)'
    text = re.sub(search_expression, "", text)
    # remove lines starting with a time
    search_expression = r'(?:^|\n)(\s+' + TIME_REGEX + r'.*)(?:$|\n)'
    text = re.sub(search_expression, "", text, re.IGNORECASE)
    # remove lines starting with a day (not case sensitive)
    days_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    # includes 3 letter variations
    # e.g. mon (rather than Monday)
    days_string = '|'.join(day + "|" + day[:3] for day in days_list)
    search_expression = r'(?:^|\n)(\s*(?:' + days_string + r').*)(?:$|\n)'
    text = re.sub(search_expression, "", text, flags=re.IGNORECASE)
    # remove lines that are in all caps
    # TODO: see if (?:^|\n)([^a-z]+)(?:$|\n) works
    search_expression = r'(?:^|\n)([\sA-Z\d:.,()[\]{}/\\!?\-"\'`]+)(?:$|\n)'
    text = re.sub(search_expression, "", text)
    # remove lines that end in the word seminar
    search_expression = r'(?:^|\n)(.*seminar\s*)(?:$|\n)'
    output = re.sub(search_expression, "", text, flags=re.IGNORECASE)
    # remove leading/trailing whitespace
    output = output.strip()
    return output


# TODO: check if global variable is /really/ necessary
# maybe make all regexps global? needs some consistency
TIME_REGEX = r'[0-2]?\d(?:(?:[.:]{1}[0-5]\d\s?(?:a|p)\.?m\.?)|(?:[.:]{1}[0-5]\d|\s?(?:a|p)\.?m\.?))'

# check if input arguments exist
if len(sys.argv) != 3:
    print('usage: ' + sys.argv[0] + " input_files_directory output_files_directory")
    sys.exit(2)
# set up the file paths
untagged_text_files_path = sys.argv[1]
output_files_path = sys.argv[2]
if output_files_path[-1] != '/':
    output_files_path += '/'
# check if the output directory exists
# if not then create it
if not exists(output_files_path):
    makedirs(output_files_path)
# get the untagged files
untagged_text_files_list = [f for f in listdir(untagged_text_files_path) if isfile(join(untagged_text_files_path, f))]
# iterate over all files
for untagged_text_file_name in untagged_text_files_list:
    # set up file
    path_to_read = join(untagged_text_files_path, untagged_text_file_name)
    print(untagged_text_file_name)
    # an open and shut case
    file_to_read = open(path_to_read, 'r')
    untagged_text_file_text = file_to_read.read()
    file_to_read.close()
    # data processing
    tagged_text_file_text = tag_paragraphs(untagged_text_file_text)
    tagged_text_file_text = tag_sentences(tagged_text_file_text)
    tagged_text_file_text = tag_times(tagged_text_file_text)
    # save data
    with open(output_files_path + untagged_text_file_name, "w+") as text_file:
        text_file.write(tagged_text_file_text)
