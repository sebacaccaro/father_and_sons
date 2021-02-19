#!/usr/bin/env bash

# Install dependencies
pip3 install sklearn tqdm pyspellchecker nltk python-Levenshtein pandas matplotlib


## Parsing
cd Parsing
#python3 decoder_1.py
#python3 decoder_12.py
#python3 decoder_17.py
#python3 decoder_18.py
#
#python3 group_leaders_1.py
#python3 group_leaders_1x.py 12
#python3 group_leaders_1x.py 17
#python3 group_leaders_1x.py 18

cd ..


## Modelling
cd Modelling
#python3 tokenizer.py 1  
#python3 tokenizer.py 12  
#python3 tokenizer.py 17 
#python3 tokenizer.py 18 
#
#python3 divide_in_parties_1.py 
#python3 divide_in_parties_1x.py 12 
#python3 divide_in_parties_1x.py 17
#python3 divide_in_parties_1x.py 18

#mkdir perplexity_score
python3 lda_modelling.py 40
python3 compare.py 40 final_table.png

