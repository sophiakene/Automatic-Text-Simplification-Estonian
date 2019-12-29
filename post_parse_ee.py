 # -*- coding: UTF-8 -*-
from collections import OrderedDict
import subprocess
import sys
import random

class PostParser():

	def reform(self, rfile, wfile):
		"""Aligns word and its corresponding analysis."""
		output = ''
		for line in rfile:
			if line.startswith('"<'):
				output += '\n'
			output += line.strip()+"\t"
		wfile.write(output)
		return output

	def makedic(self, rfile):
		"""Creates a list of dictionaries for each sentence with words as keys and their corresponding analysis as values."""
		sentences = []

		rfile.seek(0)
		for line in rfile:
			if '"<s>"' in line:
				pos = {}
			if len(line.strip().split("\t")) == 2:
				key = (line.strip('"').split("\t"))[0]
				value = (line.strip('"').split("\t"))[1]
				if key.strip('"<').strip('>"') in pos:
					key = key.strip('"<').strip('>"') + random.randint(0,10)*' '
				pos[key.strip('"<"').strip('">"')] = value
			if '"</s>"' in line:
				sentences.append(pos)
		return sentences

#----------------------------------------------------------------------------------------------------------------------------------------------
def main():

	subprocess.call(['./parser17.sh', '../parsethis.txt'], cwd='EstCG-parser')

	with open('parsethis.txt.cg3') as parsed_doc, open('parsethis.txt', 'w+', encoding='utf-8') as writefile:
		lines = parsed_doc.readlines()
		postparser = PostParser()
		postprocessed = postparser.reform(lines, writefile)
		sentences = postparser.makedic(writefile)
		print(sentences)

if __name__ == '__main__':
	main()

