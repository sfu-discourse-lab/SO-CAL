import sys, getopt, os
import argparse
from pycorenlp import StanfordCoreNLP


class Preprocess():
    def __init__(self, argv):
        self.input = ""
        self.output_folder = ""       # output has to be a folder
        self.input_type = ""

        # Start Stanford CoreNLP Server
        self.nlp = StanfordCoreNLP('http://localhost:9000')

        # Read User Command Line
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
        for opt, arg in opts:
          if opt == '-h':
             print("Type 'python3.5 text_preprocessing/preprocess.py  -i <inputfile> -o <outputfile>' \
                   in run_source_code.sh file")
             sys.exit()
          elif opt in ("-i", "--ifile"):
             self.input = arg
             if os.path.exists(arg) == False:
                 print("Input doesn't exist")
                 sys.exit()
             if os.path.isdir(arg) == True: self.input_type = "dir"
             elif os.path.isfile(arg) == True: self.input_type = "file"
          elif opt in ("-o", "--ofile"):
             self.output_folder = arg

        print("Input: " + self.input +", " + self.input_type)
        print("Output: " + self.output_folder)


    def sentence_parsing(self, row_string):
        parsed_json = self.nlp.annotate(row_string, properties={
                       'annotators': 'tokenize,ssplit,pos',
                       'outputFormat': 'json'
                   })
        return parsed_json


    def output_preprocessed_data(self, json_input, file_name):
        rows = []
        for sent in json_input['sentences']:
            parsed_sent = " ".join([t['originalText'] + "/" + t['pos'] for t in sent['tokens']])
            rows.append(parsed_sent)
        output_file_path = self.output_folder + file_name
        with open(output_file_path, 'a') as preprocessed_out:
            for r in rows:
                preprocessed_out.write(r + "\n")


    def pos_parsing(self):
        if self.input_type == "file":
            input_path_elems = self.input.split("/")
            file_name = ""
            if input_path_elems[-1] != "/":
                file_name = input_path_elems[-1]
            else:
                file_name = input_path_elems[-2]
            text_string = ""
            with open(self.input, 'rb') as file_input:
                for r in file_input:
                    text_string = " ".join([text_string, r.strip().decode('utf-8', 'backslashreplace')])
            print(self.input)
            parsed_json = self.sentence_parsing(text_string)
            self.output_preprocessed_data(parsed_json, file_name)
        elif self.input_type == "dir":
            for file_name in os.listdir(self.input):
                input_file_path = self.input + file_name
                text_string = ""
                with open(input_file_path, 'rb') as file_input:
                    for r in file_input:
                        text_string = " ".join([text_string, r.strip().decode('utf-8', 'backslashreplace')])
                parsed_json = self.sentence_parsing(text_string)
                print(input_file_path)
                self.output_preprocessed_data(parsed_json, file_name)



def main(argv):
    p = Preprocess(argv)
    p.pos_parsing()

if __name__ == "__main__":
    main(sys.argv[1:])
