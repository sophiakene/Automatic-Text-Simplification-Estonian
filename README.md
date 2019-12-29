# Automatic-Text-Simplification-Estonian

Rule-based automatic text simplification for Estonian implemented in Python

## Requirements

Python3, Estonian parser Est-CG: https://github.com/EstSyntax/EstCG

Parser files have to be in 'EstCG-parser' called folder in same directory as pipeline, post_parse and simplify scripts. 


## Usage

- python3 pipeline_ee_.py [textfile_to_simplify] 

-> Returns simplified text file [textfile_to_simplify]\_simplified in same directory as textfile_to_simplify.

- python3 pipeline_ee_parallel_simplified_only.py [textfile_to_simplify]

-> Returns text file with original sentences and simplified sentences only if a simplification has been made as [textfile_to_simplify]\_simplified in same directory as [textfile_to_simplify].
