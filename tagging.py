from os import listdir, makedirs
from os.path import isfile, join, exists
import re


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


untagged_text_files_path = 'untagged/'
output_files_path = 'tagged'
if not exists(output_files_path):
    makedirs(output_files_path)
untagged_text_files_list = [f for f in listdir(untagged_text_files_path) if isfile(join(untagged_text_files_path, f))]

for untagged_text_file_name in untagged_text_files_list:
    path_to_read = join(untagged_text_files_path, untagged_text_file_name)
    file_to_read = open(path_to_read, 'r')
    print(untagged_text_file_name)
    untagged_text_file_text = file_to_read.read()
    file_to_read.close()
    tagged_text_file_text = tag_text(untagged_text_file_text, 'topic', 'sampleTag')
    print(tagged_text_file_text)
