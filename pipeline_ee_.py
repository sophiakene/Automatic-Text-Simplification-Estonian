from post_parse_ee import PostParser
from simplify_ee import Simplify
import sys
import subprocess
import os
import re

#document to parse = argument
document = sys.argv[1]
document = '../'+document

#run Parser; creates new file (incl. parsed information) called [document].cg3 in same directory as document
subprocess.call(['./parser17.sh', document], cwd='EstCG-parser')

#temporary file
parsed_document = document[3:]+'.cg3'

#output file after simplification
simple_document = document[3:]+'_simplified'

with open(parsed_document, encoding='utf-8') as parsed_document, open('tmpfile.txt', 'w+', encoding='utf') as tmpfile,\
 open(simple_document, 'w', encoding='utf-8') as new_file:

	lines = parsed_document.readlines()
	postparser = PostParser()
	postprocessed = postparser.reform(lines, tmpfile)
	sentences = postparser.makedic(tmpfile)
	simp_obj = Simplify(sentences)

	for sent in sentences:
		n = simp_obj.get_information(sent)[0]
		head = simp_obj.get_information(sent)[1]
		new_sent = simp_obj.simplify(sent, n, head)

		if type(new_sent) == str:
			new_file.write(new_sent+'\n')

#remove auxiliary files
os.remove("tmpfile.txt")
os.remove(document[3:]+'.cg3')
