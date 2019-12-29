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
		orig_sent = ''
		for word in sent:
			orig_sent += word+' '

		n = simp_obj.get_information(sent)[0] #sent_w_quot
		head = simp_obj.get_information(sent)[1]
		new_sent = simp_obj.simplify(sent, n, head) #ant
		print(type(new_sent))
		if new_sent:
			x = re.sub('\s', '', orig_sent)
			y = re.sub('\s', '', new_sent)
			if x != y:
				if type(new_sent) == str:
					print('Original sentence: '+orig_sent+'\n'+'Simplified sentence: '+new_sent+'\n')
					new_file.write('Original sentence: '+orig_sent+'\n'+'Simplified sentence: '+new_sent+'\n\n')

#remove auxiliary files
os.remove("tmpfile.txt")
os.remove(document[3:]+'.cg3')
