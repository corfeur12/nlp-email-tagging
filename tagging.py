from os import listdir, makedirs
from os.path import isfile, join, exists
import re


def tag_text(all_text, text_to_tag, tag_name):
    tag_open = "<" + tag_name + ">"
    tag_open = re.escape(tag_open)
    tag_close = "</" + tag_name + ">"
    tag_close = re.escape(tag_close)
    return re.sub(r'(?<!' + tag_open + r')(' + re.escape(text_to_tag) + r')(?!' + tag_open + r')', tag_open + r'\1' + tag_close, all_text, flags=re.IGNORECASE)


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
