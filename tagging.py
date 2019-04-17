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
    # only tags within paragraphs
    paragraphs = re.findall(r'(?:<paragraph>)((?:.|\n)*?)(?:<\/paragraph>)', text)
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
    output = re.sub(r'(?:^|[^\n])(\n)(?!\n)', " ", text)
    return output


def remove_email_text(text):
    # removes lines surrounded by < and > or any word followed by a :
    text = re.sub(r'(?:\n|^)((?:<.*>)|(?:[^\S\n]*\w+:.*))', "", text)
    # removes lines with no text but some symbols
    text = re.sub(r'(?:^|\n)([^\w\d\n]+)(?:$|\n)', "", text)
    # removes lines with lots of whitespace before text
    text = re.sub(r'(?:^)(?!\t\w)([^\S\n]{2,}[\w\d\t \r]+.*)(?:$)', "", text, flags=re.MULTILINE)
    # removes lines with lots of whitespace in the middle
    text = re.sub(r'(?:^|\n)(\w.+?[^\S\n]{6,}.+?\w)(?:$|\n)', "", text)
    # removes lines starting with a time
    text = re.sub(r'(?:^|\n)(\s+\d{1,2}(?:(?:[.:]{1}\d{2})|(?:\s?p\.?m\.?|\s?a\.?m\.?)){1,2}.*)(?:$|\n)', "", text)
    # removes lines starting with a day (not case sensitive)
    days_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    # includes 3 letter variations
    # e.g. sun (rather than Sunday
    days_string = '|'.join(day + "|" + day[:3] for day in days_list)
    text = re.sub(r'(?:^|\n)(\s*(?:' + days_string + r').*)(?:$|\n)', "", text, flags=re.IGNORECASE)
    # removes lines that are in all caps
    text = re.sub(r'(?:^|\n)([\sA-Z\d:.,()[\]{}/\\!?\-"\'`]+)(?:$|\n)', "", text)
    # removes lines that end in the word seminar
    output = re.sub(r'(?:^|\n)(.*seminar)(?:$|\n)', "", text, flags=re.IGNORECASE)
    # removes leading/trailing whitespace
    output = output.strip()
    return output


# check that the input arguments exist
if len(sys.argv) != 3:
    print('usage: ' + sys.argv[0] + " input_files_directory output_files_directory")
    sys.exit(2)
# set up the file paths
untagged_text_files_path = sys.argv[1]
output_files_path = sys.argv[2]
if output_files_path[-1] != '/':
    output_files_path += '/'
# check if the output directory exists
# if not then creates it
if not exists(output_files_path):
    makedirs(output_files_path)
# gets the untagged files
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
    # save data
    with open(output_files_path + untagged_text_file_name, "w+") as text_file:
        text_file.write(tagged_text_file_text)
