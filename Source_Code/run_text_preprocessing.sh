#!/bin/sh

echo "Preprocess Raw Text Input: "
python3.5 text_preprocessing/preprocess.py  -i '../Sample/input/Raw_Text/BOOKS/no1.txt' -o '../Sample/output/Preprocessed_Output/BOOKS/' -a 'tokenize,ssplit,pos'
echo "Done! Generated Preprocessed Data"


