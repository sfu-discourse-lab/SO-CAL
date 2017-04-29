import argparse
import os
import csv


def get_command_arguments():
    '''
    Read command line input and set values to arguments.
    :return: a list of arguments
    '''
    parser = argparse.ArgumentParser(description='SFU Sentiment Calculator')
    parser.add_argument('--input', '-i', type=str, dest='input', action='store',
                        default='../../Sample/output/Preprocessed_Output/BOOKS',
                        help="The input file or folder, and the file should be SO_CAL preprocessed text")

    parser.add_argument('--output', '-o', type=str, dest='output', action='store',
                        default='../../Sample/output/SO_CAL_Output/BOOKS',
                        help="The output folder")

    parser.add_argument('--config', '-c', type=str, dest='config', action='store',
                        default='../../Resources/config_files/en_SO_Calc_ini.json',
                        help="The configuration file for SO-CAL")

    parser.add_argument('--word_lists', '-wl', type=str, dest='word_lists', action='store',
                        default='../../Resources/internal_word_lists/en_word_lists.json',
                        help="The internal word lists for SO-CAL")

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
    gold_folder = "../../Resources/gold/"
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
                return ""
        elif os.path.isdir(input_path) == True:
            for f in os.listdir(input_path):
                if f.startswith("no"):
                    out.write(f+","+"negative"+"\n")
                elif f.startswith("yes"):
                    out.write(f+","+"positive"+"\n")
                else:
                    return ""
        else:
            print("Your gold input " + os.path.abspath(input_path) + "is neither a file nor a folder.")

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
            gold_dct[file_sentiment[0]] = file_sentiment[1]
    return gold_dct


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

    cmd = "python3.5 SO_Calc.py -i \"" + input_path + "\" -o \"" + output_folder + "\" -c \"" + config_file + "\" -cf " \
          + str(cutoff) + " -wl \"" + args.word_lists + "\""
    os.system(cmd)

    # if gold_file == "":
    #     print("""
    #           Without gold data, the prediction accuracy will not be generated.
    #           To create gold data, either name your preprocessed data with "yes" or "no",
    #           or create a gold file similar to Sample/gold/gold.txt,
    #           and indicate the gold file path through command line.
    #           """)
    # else:
    #     prediction_accuracy =  os.path.abspath(output_folder) + "/prediction_accuracy.txt"
    #     file_sentiment = os.path.abspath(output_folder) + "file_sentiment.csv"
    #     gold_dct = read_gold_file(gold_file)
    #     p_total = 0
    #     n_total = 0
    #     p_correct = 0
    #     n_correct = 0
    #
    #     with open(file_sentiment) as fs:
    #         sentiment_csv = csv.DictReader(fs)
    #         for r in sentiment_csv:
    #             file_name = r['File_Name']
    #             predicted_sentiment = r['Sentiment']
    #             if gold_dct[file_name] == pos_mark:
    #                 p_total += 1
    #                 if predicted_sentiment == pos_mark:
    #                     p_correct += 1
    #             elif gold_dct[file_name] == neg_mark:
    #                 n_total += 1
    #                 if predicted_sentiment == neg_mark:
    #                     n_correct += 1
    #
    #     open(prediction_accuracy, 'w').close()
    #     with open(prediction_accuracy, 'a') as pa:
    #         pa.write("------\nResults:\n------\n")
    #         if p_total > 0:
    #             pa.write(str(p_total) + " Positive Reviews\n")
    #             pa.write("Percent Correct: " + str(100.0*p_correct/p_total) + " %\n")
    #         else:
    #             pa.write("Total Predicted Positive Review is 0.\n")
    #         if n_total > 0:
    #             pa.write(str(n_total) + " Negative Reviews\n")
    #             pa.write("Percent Correct: " + str(100.0*n_correct/n_total) + " %\n")
    #         else:
    #             pa.write("Total Predicted Negative Review is 0.\n")
    #         total = p_total + n_total
    #         correct = p_correct + n_correct
    #         if total > 0:
    #             pa.write(str(total) + " Total Reviews\n")
    #             pa.write("Percent Correct: " + str(100.0*correct/total) + " %\n")
    #         else:
    #             pa.write("Total Predicted Positive & Negative Review is 0.\n")
    #
    # print("Find all the output in: " + output_folder)

if __name__ == "__main__":
    main()