import argparse
import os
import csv
from collections import OrderedDict
import json


def get_command_arguments():
    '''
    Read command line input and set values to arguments.
    :return: a list of arguments
    '''
    parser = argparse.ArgumentParser(description='SFU Sentiment Calculator')
    parser.add_argument('--input', '-i', type=str, dest='input', action='store',
                        default='../Sample/output/Preprocessed_Output/BOOKS',
                        help="The input file or folder, and the file should be SO_CAL preprocessed text")

    parser.add_argument('--output', '-o', type=str, dest='output', action='store',
                        default='../Sample/output/SO_CAL_Output/BOOKS',
                        help="The output folder")

    parser.add_argument('--config', '-c', type=str, dest='config', action='store',
                        default='../Resources/config_files/en_SO_Calc.ini',
                        help="The configuration file for SO-CAL")

    parser.add_argument('--cutoff', '-cf', type=float, dest='cutoff', action='store',
                        default=0.0,
                        help="The threshold for sentiment distinction")

    parser.add_argument('--gold', '-g', type=str, dest='gold', action='store',
                        default='',
                        help="""The gold file,
                                but if your data files start with 'yes' or 'no', the gold file is not necessary
                             """)
    args = parser.parse_args()
    return args


def create_gold_file(input_path):
    '''
    If the user have input file names start with "yes" or "no",
    this function will generate the gold file for them.
    :param input_path: input path of the preprocessed file or folder
    :return: the gold file path
    '''
    gold_folder = "../Resources/gold/"
    if os.path.exists(gold_folder) == False:
        os.mkdir(gold_folder)
    gold_output = gold_folder + "gold.txt"

    open(gold_output, 'w').close()
    with open(gold_output, "a") as out:
        if os.path.isfile(input_path) == True:
            f = os.path.basename(input_path)
            if f.startswith("no"):
                out.write(f+","+"negative"+"\n")
            elif f.startswith("yes"):
                out.write(f+","+"positive"+"\n")
            else:
                print("""Each input file has to start with "yes" or "no", or create your own gold file. """)
                return ""
        elif os.path.isdir(input_path) == True:
            for f in os.listdir(input_path):
                if f.startswith("no"):
                    out.write(f+","+"negative"+"\n")
                elif f.startswith("yes"):
                    out.write(f+","+"positive"+"\n")
                else:
                    print("""Each input file has to start with "yes" or "no", or create your own gold file. """)
                    return ""
        else:
            print("Your gold input " + os.path.abspath(input_path) + "is neither a file nor a folder.")
            return ""

    return gold_output


def read_gold_file(gold_file):
    '''
    Convert the gold file into a dictionary.
    :param gold_file: the path of gold file
    :return: the gold dictionary
    '''
    gold_dct = {}
    with open(gold_file) as gold_input:
        for r in gold_input:
            file_sentiment = r.split(',')
            gold_dct[file_sentiment[0]] = file_sentiment[1].strip()
    return gold_dct


def generate_file_sentiment(basicout_path, cutoff, file_sentiment_path):
    '''
    Generate file_sentiment.csv based on output.txt.
    This csv contains file name, sentiment for the file and the SO score.
    :param basicout_path: output.txt path
    :param cutoff: cutoff value
    :param file_sentiment_path: file_sentiment.csv path
    :return: None, but write into file_sentiment.csv
    '''
    dct_lst = []

    with open(basicout_path) as basic_output:
        for r in basic_output:
            file_score = r.strip().split()
            file = file_score[0]
            score = float(file_score[1])
            if score < cutoff:
                sentiment = "negative"
            elif score > cutoff:
                sentiment = "positive"
            else:
                sentiment = "neutral"
            dct_lst.append({"File_Name":file, "Sentiment":sentiment, "Score":score})

    with open(file_sentiment_path, 'a') as csv_out:
        fieldnames = ['File_Name', 'Sentiment', 'Score']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)

        if os.stat(file_sentiment_path).st_size == 0: writer.writeheader()
        for dct in dct_lst:
            writer.writerow(dct)


def generate_richoutJSON(richout_input, richout_output):
    '''
    Convert richout.txt to JSON formatted output. The original order did not change.
    :param richout_input: the path of richout.txt
    :param richout_output: the path of rich_output.json
    :return: None, but generated rich_output.json
    '''
    rich_dct = {}
    within_file = 0
    latest_key = ""
    latest_file = ""
    keys = ["Nouns", "Verbs", "Adjectives", "Adverbs", "SO by Sentence"]

    with open(richout_input) as richin:
        for r in richin:
            r = r.strip()
            if r == "": continue
            if "######" not in r and '---' not in r and ":" not in r and within_file == 0:
                within_file = 1
                file_name = r
                rich_dct[file_name] = OrderedDict([("Text Length", 0), ("Nouns", {"List":[], "Average SO":0}),
                                                   ("Verbs", {"List":[], "Average SO":0}),
                                                   ("Adjectives", {"List":[], "Average SO":0}),
                                                   ("Adverbs", {"List":[], "Average SO":0}), ("SO by Sentence",[]),
                                                   ("Total SO", 0)])
                latest_file = file_name
                continue
            if within_file == 1:
                if r.startswith("Text Length:"):
                    rich_dct[latest_file]["Text Length"] = float(r.split(': ')[1])
                elif r.split(':')[0] in keys:
                    latest_key = r.split(':')[0]
                elif '---' not in r and r.startswith("Total SO:") == False:
                    if r.startswith("Average SO:"):
                        rich_dct[latest_file][latest_key]["Average SO"] = float(r.split(': ')[1])
                    elif latest_key != "SO by Sentence":
                        rich_dct[latest_file][latest_key]["List"].append(r)
                    elif "######" not in r:
                        so_score = r.split()[-1]
                        sent = ' '.join(r.split()[:-1])
                        rich_dct[latest_file][latest_key].append({sent:so_score})
                elif r.startswith("Total SO:"):
                    rich_dct[latest_file]["Total SO"] = float(r.split(': ')[1])

            if "######" in r:
                within_file = 0

    sorted_dict = OrderedDict(sorted(rich_dct.items(), key=lambda t: t[0]))
    with open(richout_output, 'w') as richout:
        json.dump(sorted_dict, richout)


def main():
    pos_mark = "positive"
    neg_mark = "negative"

    args = get_command_arguments()
    input_path = args.input
    output_folder = args.output
    if os.path.exists(output_folder) == False:
        os.mkdir(output_folder)
    config_file = args.config
    cutoff = args.cutoff
    gold_file = args.gold
    if gold_file == "":
        gold_file = create_gold_file(input_path)

    basicout_path = os.path.abspath(output_folder) + "/output.txt"
    richout_path = os.path.abspath(output_folder) + "/richout.txt"
    file_sentiment_path = os.path.abspath(output_folder) + "/file_sentiment.csv"
    prediction_accuracy_path =  os.path.abspath(output_folder) + "/prediction_accuracy.txt"
    richout_json = os.path.abspath(output_folder) + "/rich_output.json"

    open(basicout_path, "w").close()
    open(richout_path, "w").close()
    open(file_sentiment_path, 'w').close()
    open(prediction_accuracy_path, 'w').close()

    if os.path.isfile(input_path):  # 1 single file
        print("Processing " + os.path.basename(input_path) + "...")
        cmd = "python3.5 sentiment_calculator/SO_Calc.py -i \"" + input_path + "\" -bo \"" + basicout_path + "\" -ro \"" + richout_path + "\" -c \"" + config_file + "\""
        os.system(cmd)
    elif os.path.isdir(input_path):   # an input folder, only reads files
        for f_name in os.listdir(input_path):
            print("Processing " + f_name + "...")
            file_path = os.path.abspath(input_path) + "/" + f_name
            if os.path.isfile(file_path) == False: continue
            cmd = "python3.5 sentiment_calculator/SO_Calc.py -i \"" + file_path + "\" -bo \"" + basicout_path + "\" -ro \"" + richout_path + "\" -c \"" + config_file + "\""
            os.system(cmd)

    generate_file_sentiment(basicout_path, cutoff, file_sentiment_path)
    generate_richoutJSON(richout_path, richout_json)

    if gold_file == "":
        print("""
              Without gold data, the prediction accuracy will not be generated.
              To create gold data, either name your preprocessed data with "yes" or "no",
              or create a gold file similar to Sample/gold/gold.txt,
              and indicate the gold file path through command line.
              """)
    else:
        gold_dct = read_gold_file(gold_file)
        p_total = 0
        n_total = 0
        p_correct = 0
        n_correct = 0

        with open(file_sentiment_path) as fs:
            sentiment_csv = csv.DictReader(fs)
            for r in sentiment_csv:
                file_name = r['File_Name']
                predicted_sentiment = r['Sentiment']
                if gold_dct[file_name] == pos_mark:
                    p_total += 1
                    if predicted_sentiment == pos_mark:
                        p_correct += 1
                elif gold_dct[file_name] == neg_mark:
                    n_total += 1
                    if predicted_sentiment == neg_mark:
                        n_correct += 1

        with open(prediction_accuracy_path, 'a') as pa:
            pa.write("------\nResults:\n------\n")
            if p_total > 0:
                pa.write(str(p_total) + " Positive Reviews\n")
                pa.write("Percent Correct: " + str(100.0*p_correct/p_total) + " %\n")
            else:
                pa.write("Total Predicted Positive Review is 0.\n")
            if n_total > 0:
                pa.write(str(n_total) + " Negative Reviews\n")
                pa.write("Percent Correct: " + str(100.0*n_correct/n_total) + " %\n")
            else:
                pa.write("Total Predicted Negative Review is 0.\n")
            total = p_total + n_total
            correct = p_correct + n_correct
            if total > 0:
                pa.write(str(total) + " Total Reviews\n")
                pa.write("Percent Correct: " + str(100.0*correct/total) + " %\n")
            else:
                pa.write("Total Predicted Positive & Negative Review is 0.\n")

    print("Find all the output in: " + output_folder)

if __name__ == "__main__":
    main()