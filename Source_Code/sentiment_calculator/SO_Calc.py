# coding: utf-8
######## Semantic Orientation Calculator (SO-CAL) #######
# The code is is majorly from Julian Brooke's code written in 2008
# Changes are made to allow the code running in Python3.5
# The Semantic Orientation Calculator take a properly formated textfile and
# (optionally) a file of span weights and calculates a semantic orietation (SO)
# for the file based on the appearance of words carrying positive or negative
# sentiment, multiplied by weight according to their location in the text
#
# SO-CAL v1.0 (written in perl) supported adjectives, nouns, verbs, adjectives,
# intensification, modals, and negation.
#
# Major Changes since 1.0
# added support for multi-word dictionaries
# added extra weighing of negative phrases
# added lowered weight on (or nullification of) repeated items
# added intensification and nullification based on punctuation
# added intensification based on captialization
# added intensification based on other "highlighting" words
# added clause final intensification for verbs
# added modifier blocking of opposite polarity SO values
# added part-of-speech-specific restricted negation, by word or tag
# added clause boundary words that block backward searches
# added negation-external intensification
# added optional negation shifting limits
# added tag fixing for all_caps words
# added external weighing by use of XML tags
# added weighing based on part of speech
# added external ini file
# added flexible weighing by location in text
# added to the list of irrealis markers (modals)
# added definite determiner overriding of irrealis nullification
# improved handling of "too"
# improved rich output to show calculation
# fixed some small stemming problems
# intensification and negation are now totally separate
#
#
# Changes since V1.11
# merged Spanish and English calculators
# expanded dictionaries
# various minor bug fixes
# XML weighting with real number tags
# added negative negation nullification
# some lists moved to config file
# now uses boundares as indicated by newlines in the input as search
# and sentence boundaries


import operator
import argparse
import os


def get_command_arguments():
    '''
    Read command line input and set values to arguments.
    :return: a list of arguments
    '''
    parser = argparse.ArgumentParser(description='SFU Sentiment Calculator')
    parser.add_argument('--input', '-i', type=str, dest='input', action='store',
                        default='../Sample/output/Preprocessed_Output/BOOKS/no1.txt',
                        help="The input file or folder, and the file should be SO_CAL preprocessed text")

    parser.add_argument('--basicout_path', '-bo', type=str, dest='basicout_path', action='store',
                        default='',
                        help="The basic output")

    parser.add_argument('--richcout_path', '-ro', type=str, dest='richout_path', action='store',
                        default='',
                        help="The basic output")

    parser.add_argument('--config', '-c', type=str, dest='config', action='store',
                        default='../Resources/config_files/en_SO_Calc.ini',
                        help="The configuration file for SO-CAL")


    args = parser.parse_args()
    return args

args = get_command_arguments()
infile = open(args.input, "r")
configfile = open(args.config, "r")

basicout = open(args.basicout_path, "a")
richout = open(args.richout_path, "a")

config = {}

def get_configuration_from_file():
# gets the configuration settings from the supplied .ini file
    for line in configfile.readlines():
        if line:
            line = line.split("#")[0].strip()
            if "=" in line:
                (key, value) = map(str.strip, line.split("="))
                if value.strip():
                    if "[" not in value:
                        if value[-1].isdigit():
                            value = float(value)
                        elif value == "True":
                            value = True
                        elif value == "False":
                            value = False
                        config[key] = value
                    else:
                         elements = value[1:-1].split( ",")
                         if ":" in value:
                             svalues = {}
                             for element in elements:
                                 if element:
                                     (skey,svalue) = map(str.strip, element.split(":"))
                                     if svalue[-1].isdigit():
                                         svalue = float(svalue)
                                     elif svalue == "True":
                                         svalue = True
                                     elif svalue == "False":
                                         svalue = False
                                 svalues[skey] = svalue
                             config[key] = svalues
                         else:
                             config[key] = map(str.strip, elements)
    configfile.close()

get_configuration_from_file()

language = config["language"]
use_adjectives = config["use_adjectives"]
use_nouns = config["use_nouns"]
use_verbs = config["use_verbs"]
use_adverbs = config["use_adverbs"]
use_intensifiers = config["use_intensifiers"]
use_negation = config["use_negation"]
use_comparatives = config["use_comparatives"]
use_superlatives = config["use_superlatives"]
use_multiword_dictionaries = config["use_multiword_dictionaries"]
use_extra_dict = config["use_extra_dict"]
use_XML_weighing = config["use_XML_weighing"]
use_weight_by_location = config["use_weight_by_location"]
use_irrealis = config["use_irrealis"]
use_subjunctive = config["use_subjunctive"]
use_imperative = config["use_imperative"]
use_conditional = config["use_conditional"]
use_highlighters = config["use_highlighters"]
use_cap_int = config["use_cap_int"]
fix_cap_tags = config["fix_cap_tags"]
use_exclam_int = config["use_exclam_int"]
use_quest_mod = config["use_quest_mod"]
use_quote_mod = config["use_quote_mod"]
use_definite_assertion = config["use_definite_assertion"]
use_clause_final_int = config["use_clause_final_int"]
use_heavy_negation = config["use_heavy_negation"]
use_word_counts_lower = config["use_word_counts_lower"]
use_word_counts_block = config["use_word_counts_block"]
use_blocking = config["use_blocking"]
adv_learning = config["adv_learning"]
limit_shift = config["limit_shift"]
neg_negation_nullification = config["neg_negation_nullification"]
polarity_switch_neg = config["polarity_switch_neg"]
restricted_neg = config["restricted_neg"]
simple_SO = config["simple_SO"]
use_boundary_words = config["use_boundary_words"]
use_boundary_punct = config["use_boundary_punctuation"]

### Modifiers ###

adj_multiplier = config["adj_multiplier"]
adv_multiplier = config["adv_multiplier"]
verb_multiplier = config["verb_multiplier"]
noun_multiplier = config["noun_multiplier"]
int_multiplier = config["int_multiplier"]
neg_multiplier = config["neg_multiplier"]
capital_modifier = config["capital_modifier"]
exclam_modifier = config["exclam_modifier"]
verb_neg_shift = config["verb_neg_shift"]
noun_neg_shift = config["noun_neg_shift"]
adj_neg_shift = config["adj_neg_shift"]
adv_neg_shift = config["adv_neg_shift"]
blocker_cutoff = config["blocker_cutoff"]

### Dictionaries ###

dic_dir = config["dic_dir"]
adj_dict_path = dic_dir + config["adj_dict"]
adv_dict_path = dic_dir + config["adv_dict"]
noun_dict_path = dic_dir + config["noun_dict"]
verb_dict_path = dic_dir + config["verb_dict"]
int_dict_path = dic_dir + config["int_dict"]
if use_extra_dict and config["extra_dict"]:
    extra_dict_path = dic_dir + config["extra_dict"]
else:
    extra_dict_path = False
adj_dict = {} # simple (single-word) dictionaries
adv_dict = {}
noun_dict = {}
verb_dict = {}
int_dict = {}
c_adj_dict = {} # complex (multi-word) dictionaries
c_adv_dict = {}
c_noun_dict = {}
c_verb_dict = {}
c_int_dict = {}
new_adv_dict = {}

### Text ###

text = [] # the text is a list of word, tag lists
weights = [] # weights should be the same length as the text, one for each token
word_counts = [{},{},{},{}] # keeps track of number of times each word lemma appears in the text
text_SO = 0 # a sum of the SO value of all the words in the text
SO_counter = 0 # a count of the number of SO carrying terms
boundaries = [] # the location of newline boundaries from the input

### Internal Word lists ###
if language == "English":
    not_wanted_adj = ["other", "same", "such", "first", "next", "last", "few", "many", "less", "more", "least", "most"]
    not_wanted_adv = [ "really", "especially", "apparently", "actually", "evidently", "suddenly", "completely","honestly", "basically", "probably", "seemingly", "nearly", "highly", "exactly", "equally", "literally", "definitely", "practically", "obviously", "immediately", "intentionally", "usually", "particularly", "shortly", "clearly", "mildly", "sincerely", "accidentally", "eventually", "finally", "personally", "importantly", "specifically", "likely", "absolutely", "necessarily", "strongly", "relatively", "comparatively", "entirely", "possibly", "generally", "expressly", "ultimately", "originally", "initially", "virtually", "technically", "frankly", "seriously", "fairly",  "approximately", "critically", "continually", "certainly",  "regularly", "essentially", "lately", "explicitly", "right", "subtly",  "lastly", "vocally", "technologically", "firstly", "tally", "ideally", "specially", "humanly", "socially", "sexually", "preferably", "immediately", "legally", "hopefully", "largely", "frequently", "factually", "typically"]
    not_wanted_verb = []
    negators = ["not", "no", "n't", "neither", "nor", "nothing", "never", "none", "lack", "lacked", "lacking", "lacks", "missing", "without", "absence", "devoid"];
    punct = [".", ",", ";", "!", "?", ":", ")", "(", "\"", "'", "-"]
    sent_punct = [".", ";", "!", "?", ":", "\n", "\r"]
    skipped = {"JJ": ["even", "to", "being", "be", "been", "is", "was", "'ve", "have", "had", "do", "did", "done", "of", "as", "DT", "PSP$"], "RB": ["VB", "VBZ", "VBP", "VBG"], "VB":["TO", "being", "been", "be"], "NN":["DT", "JJ", "NN", "of", "have", "has", "come", "with", "include"]}
    comparatives = ["less", "more", "as"]
    superlatives = ["most", "least"]
    definites = ["the","this", "POS", "PRP$"]
    noun_tag = "NN"
    verb_tag = "VB"
    adj_tag = "JJ"
    adv_tag = "RB"
    macro_replace = {"#NP?#": "[PDT]?_[DET|PRP|PRP$|NN|NNP]?_[POS]?_[NN|NNP|JJ]?_[NN|NNP|NNS|NNPS]?","#PER?#": "[me|us|her|him]?","#give#": "give|gave|given","#fall#": "fall|fell|fallen","#get#": "get|got|gotten","#come#": "come|came","#go#": "go|went|gone", "#show#": "show|shown","#make#": "make|made","#hang#": "hang|hung","#break#": "break|broke|broken", "#see#": "see|saw|seen", "#be#": "be|am|are|was|were|been", "#bring#": "bring|brought", "#think#" : "think|thought", "#have#": "has|have|had", "#blow#": "blow|blew", "#build#": "build|built", "#do#": "do|did|done", "#can#": "can|could", "#grow#":"grow|grew|grown", "#hang#": "hang|hung", "#run#": "run|ran", "#stand#": "stand|stood", "#string#": "string|strung", "#hold#" : "hold|held", "#take#" : "take|took|taken"}
elif language == "Spanish":
    not_wanted_adj = ["otro","mio","tuyo","suyo","nuestro","vuestro","mismo","primero","segundo","último"]
    additional = []
    for adj in not_wanted_adj:
       additional += [adj[:-1] + "a",adj[:-2] + "os", adj[:-2] + "as"]
    not_wanted_adj += additional
    not_wanted_adv = ["básicamente", "claramente","ampliamente", "atentamente", "completamente"]
    not_wanted_verb = ["haber", "estar"]
    negators = ["no", "ni", "nunca", "jam"+ chr(225) + "s", "nada", "nadie", "ninguno", "ningunos", "ninguna", "ningunas", "faltar", "falta", "sin"];
    punct = [".", ",", ";", "!", "?", ":", ")", "(", "\"", "'", "-", chr(161), chr(191)]
    sent_punct = [".", ";", "!", "?", ":", "\n", "\r", chr(161), chr(191)]
    skipped = {"AQ": [ "a", "estar", "haber", "hacer", "de", "como", "NC", "PP", "DP", "DD", "DI", "DA", "RG"], "RG": ["VM", "VA", "VS"], "VM":["haber", "estar", "PP"], "NC":["DP", "DD", "DI", "DA", "AQ", "AO", "de", "tener", "hacer", "estar", "con", "incluso"]}
    comparatives = ["m" + chr(225) + "s", "menos", "como"]
    definites = ["el", "la", "los", "las", "este", "esta","estos", "estas", "de", "DP"]
    accents = {chr(237):"i", chr(243):"o", chr(250):"u", chr(233):"e", chr(225):"a",chr(241):"n"}
    noun_tag = "NC"
    verb_tag = "VM"
    adj_tag = "AQ"
    adv_tag = "RG"
    macro_replace = {"#NP?#": "[DI|DP|DA]?_[AQ|AC]?_[NC|NP]?_[AQ]?"}

weight_tags= config["weight_tags"]
weights_by_location = config["weights_by_location"]
highlighters = config["highlighters"]
irrealis = config["irrealis"]
boundary_words = config["boundary_words"]


### Multi-word dictionary macros:
### These macros allow for relatively simple and uncluttered multiword
### dictionary definitions. The dictionary keys will be replaced by the
### their corresponding values when they appear in definitions (in the
### dictionary files). In particular, allows the forms of irregular verbs
### to be listed only once (here, rather than in the dictionary)

### Output ###

output_calculations = config["output_calculations"]
output_sentences = config["output_sentences"]
output_unknown = config["output_unknown"]
output_used = config["output_used"]
output_used_lemma = config["output_used_lemma"]
search = config["search"]
contain_all_words = config["contain_all_words"]

### Loading functions ###

def same_lists (list1, list2):
    '''
    Check if 2 lists exactly the same (same elements, same order)
    :param lst1: list 1
    :param lst2: list 2
    :return: if they are exactly the same, return True, otherwise False
    '''
    return list1 == list2

def get_multiword_entries (string):
### Coverts the multiword dictionary entry in a file to something that can
### be accessed by the calculator
### In the dictionary, each word of a multi-word definition is separated by
### an underscore. The primary word (the one whose part of speech is the same
### as the phrase as a whole, except for intensifiers) should be in parentheses;
### it becomes the key (if there are multiple keys, multiple entries are created)
### The value of an c_dict is a list of all multi-word phrases a key word
### appears in (as a key) and each of these contains a 2-ple: the list all the
### words in the phrase, with the key word removed and replaced with a #,
### and the SO value for the phrase. If a word or words is modified by an
### operator (such as ?,*,+,|, or a number), the operator should be placed in
### []--all operators but | appear outside the right bracket
### ? = optional, + = one or more, * = zero or more, 2 (3, etc.) = two of these
### | = or. INT refers to a word or words in the intensifier dictionary.
### with that key (minus the last word), together with the modifier value
### ex.: c_int_dict["little"] = [[["a", "#"], -0.5]]
    if "#" in string:  #if there is a macro, replace
        for item in macro_replace:
            string = string.replace(item, macro_replace[item])
    words = string.split("_")
    entry = []
    keyindex = len(words) - 1 # if no parens, default to last word
    for index in range(len(words)):
        word = words[index]
        slot = []
        if word[0] == "(":
            slot.append(1)
            slot.append(word[1:-1].split("|"))
            keyindex = index # found the key
        elif word[0] == "[":
            ordinality = False
            if word[-1] != "]":
                ordinality = True
            if ordinality:
                slot.append(word[-1])
                word = word[:-1]
            else:
                slot.append(1)
            slot.append(word[1:-1].split("|"))
        else:
            slot = word
        entry.append(slot)
    final_entries = []
    if not isinstance(entry[keyindex], list):
        key = entry[keyindex]
        entry[keyindex] = "#"
        final_entries = [[key,entry]]
    else:
        for key in entry[keyindex][1]:
            final_entry = []
            for index in range(len(entry)):
                if index == keyindex:
                    final_entry.append("#")
                else:
                    final_entry.append(entry[index])
            final_entries.append([key, final_entry])
    return final_entries

def has_accent(word):
    for accent in accents:
        if accent in word:
            return True
    return False

def remove_accents(word):
    for accent in accents:
        word = word.replace(accent, accents[accent])
    return word

def load_dictionary (filepointer, s_dict, c_dict):
### General function for loading dictionaries from files and putting them
### either in the simple or complex dictionary, as appropriate
    for line in filepointer.readlines():
        pair = line.strip().split()
        if len(pair) == 2:
            if "_" not in pair[0]:  #if single word
                if language == "Spanish" and has_accent(pair[0]):
                    s_dict[remove_accents(pair[0])] = float(pair[1])
                s_dict[pair[0]] = float(pair[1]) #put in simple dictionary
            elif use_multiword_dictionaries:
                entries = get_multiword_entries(pair[0])
                for entry in entries:
                    if entry[0] not in c_dict:
                        c_dict[entry[0]] = [[entry[1], float(pair[1])]]
                    else:
                        c_dict[entry[0]].append([entry[1], float(pair[1])])
    filepointer.close()

def load_extra_dict (filepointer):
### loads the optional dictionary, which contains entries from all the
### various types of words
    s_dict = False
    c_dict = False
    for line in filepointer.readlines():
        line = line.strip()
        if line:
            if line == "adjectives":
                s_dict = adj_dict
                c_dict = c_adj_dict
            elif line == "nouns":
                s_dict = noun_dict
                c_dict = c_noun_dict
            elif line == "verbs":
                s_dict = verb_dict
                c_dict = c_verb_dict
            elif line == "adverbs":
                s_dict = adv_dict
                c_dict = c_adv_dict
            elif line == "intensifiers":
                s_dict = int_dict
                c_dict = c_adv_dict
            elif s_dict:
                pair = line.split()
                if "_" not in pair[0]:  #if single word
                    s_dict[pair[0]] = float(pair[1]) #put in simple dictionary
                elif use_multiword_dictionaries:
                    entries = get_multiword_entries(pair[0])
                    for entry in entries:
                        if entry[0] not in c_dict:
                            c_dict[entry[0]] = [[entry[1], float(pair[1])]]
                        else:
                             for old_entry in c_dict[entry[0]]: # duplicate entry
                                if same_lists(old_entry[0], entry[1]):
                                    c_dict[entry[0]].remove(old_entry)
                             c_dict[entry[0]].append([entry[1], float(pair[1])])
    filepointer.close()

def load_dictionaries ():
### load the five kinds of dictionaries
    load_dictionary (open (adj_dict_path, encoding = "ISO-8859-1"), adj_dict, c_adj_dict)
    load_dictionary (open (adv_dict_path, encoding = "ISO-8859-1"), adv_dict, c_adv_dict)
    load_dictionary (open (verb_dict_path, encoding = "ISO-8859-1"), verb_dict, c_verb_dict)
    load_dictionary (open (noun_dict_path, encoding = "ISO-8859-1"), noun_dict, c_noun_dict)
    load_dictionary (open (int_dict_path, encoding = "ISO-8859-1"), int_dict, c_int_dict)
    if extra_dict_path:
        load_extra_dict(open (extra_dict_path, encoding = "ISO-8859-1"))
    if simple_SO:
        for s_dict in [adj_dict,adv_dict,verb_dict, noun_dict]:
            for entry in s_dict:
                if s_dict[entry] > 0:
                    s_dict[entry] = 2
                elif s_dict[entry] < 0:
                    s_dict[entry] = -2
        for entry in int_dict:
            if int_dict[entry] > 0:
                int_dict[entry] = .5
            elif int_dict[entry] < 0 and int_dict[entry] > -1:
                int_dict[entry] = -.5
            elif int_dict[entry] < -1:
                int_dict[entry] = -2
        for c_dict in [c_adj_dict,c_adv_dict,c_verb_dict, c_noun_dict]:
            for entry in c_dict:
                for i in range(len(c_dict[entry])):
                    if c_dict[entry][i][1] > 0:
                        c_dict[entry][i] = [c_dict[entry][i][0], 2]
                    elif c_dict[entry][i][1] < 0:
                        c_dict[entry][i] = [c_dict[entry][i][0], -2]
        for entry in c_int_dict:
             for i in range(len(c_int_dict[entry])):
                 if c_int_dict[entry][i][1] > 0:
                     c_int_dict[entry][i] = [c_int_dict[entry][i][0], .5]
                 elif c_int_dict[entry][i][1] < 0 and c_int_dict[entry][i][1] > -1:
                     c_int_dict[entry][i] = [c_int_dict[entry][i][0], -.5]
                 elif c_int_dict[entry][i][1] < -1:
                     c_int_dict[entry][i] = [c_int_dict[entry][i][0], -2]


def convert_fraction(fraction):
### coverts a fraction string into a float
    if "/" not in fraction:
        return float(fraction)
    else:
        fraction = fraction.split("/")
        if len(fraction) == 2:
            return float(fraction[0])/float(fraction[1])
    return -1

def is_decimal(string):
    decimal_yet = False
    if len(string) == 0:
        return False
    if string[0] == "-":
        string = string[1:]
        if len(string) == 0:
            return False
    for letter in string:
        if not letter.isdigit():
            if not letter == "." or decimal_yet:
                return False
            else:
                decimal_yet = True
    return True

def convert_ranges():
### converts a list of string ranges in faction form (e.g. ["1/4-1/2", 2]) into a
### a list of numerical ranges plus weight (e.g. [0.25, .5, 2]
    new_ranges = []
    for range in weights_by_location:
        pair = range.split("-")
        if len(pair) == 2:
            start = convert_fraction(pair[0].strip())
            end = convert_fraction(pair[1].strip())
            if start >= 0 and start <= 1 and end >= 0 and end <= 1 and start < end:
                new_ranges.append([start,end, weights_by_location[range]])
    return new_ranges


def fill_text_and_weights(infile):
### Read in the textfile. The file is assumed to be properly spaced and tagged,
### i.e. there should be a space between every word/tag pair or XML tag
### if there are XML tags and those tags have been assigned weight, the weight
### will be applied after the opening tag and will be removed at the closing
### tag. All XML tags are removed for the SO calculation
    weight = 1.0 # start with weight 1
    temp_weight = 1.0 # keep track of weight before a zero
    for line in infile.readlines():
        line = line.replace("<", " <").replace(">", "> ")
        for word in line.strip().split(" "):
            if word:
                if word[0] == "<" and word[-1] == ">": #XML tag
                    XML_tag = word.strip("<>/")
                    if use_XML_weighing:
                        if XML_tag in weight_tags:
                            weight_modifier = weight_tags[XML_tag]
                        elif is_decimal(XML_tag):
                            weight_modifier = float(XML_tag)
                        else:
                            weight_modifier = 1
                        if word[1] == "/":
                            if weight_modifier != 0:
                                weight /= weight_modifier # remove weight
                            else:
                                weight = temp_weight # use pre-zero weight
                        else:
                            if weight_modifier != 0:
                                weight *= weight_modifier # add weight
                            else:
                                temp_weight = weight # save weight
                                weight = 0
                elif "/" in word:
                    text.append(word.split("/"))
                    weights.append(weight)
        boundaries.append(len(text))
    if use_weight_by_location:  # add location weights
        range_dict = convert_ranges()
        for i in range(len(weights)):
            for interval in range_dict:  #if the current index in range
                if interval[0] <= float(i)/len(weights) and interval[1] > float(i)/len(weights):
                    weights[i] *= interval[2]  #add the weight
    infile.close()

### English steming functions ###

def stem_NN(NN):
    if NN not in noun_dict and NN not in c_noun_dict and  len(NN) > 2 and NN[-1] == "s":   # boys -> boy
        NN = NN[:-1]
        if NN not in noun_dict and NN not in c_noun_dict and NN[-1] == "e": # watches -> watch
            NN = NN[:-1]
            if NN not in noun_dict and NN not in c_noun_dict and NN[-1] == "i": # flies -> fly
                NN = NN[:-1] + "y"
    return NN

def stem_VB(VB, type):
    if type == "" or type == "P" or len(VB) < 4 or VB in verb_dict or VB in c_verb_dict:
        return VB
    elif type == "D" or type == "N":
        if VB[-1] == "d":
            VB = VB[:-1]   #  loved -> love
            if not VB in verb_dict and not VB in c_verb_dict:
                if VB[-1] == "e":
                    VB = VB[:-1]   # enjoyed -> enjoy
                if not VB in verb_dict and not VB in c_verb_dict:
                    if VB[-1] == "i":
                        VB = VB[:-1] + "y" # tried -> try
                    elif len(VB) > 1 and VB[-1] == VB[-2]:
                        VB = VB[:-1]   # compelled -> compel
        return VB
    elif type == "G":
        VB = VB[:-3] # obeying -> obey
        if not VB in verb_dict and not VB in c_verb_dict:
            if len(VB) > 1 and VB[-1] == VB[-2]:
                VB = VB[:-1] # stopping -> stop
            else:
                VB = VB + "e" # amusing -> amuse
        return VB
    elif type == "Z" and len(VB) > 3:
        if VB[-1] == "s":
            VB = VB[:-1]  # likes -> like
            if VB not in verb_dict and not VB in c_verb_dict and VB[-1] == "e":
                VB = VB[:-1]  # watches -> watch
                if VB not in verb_dict and not VB in c_verb_dict and VB[-1] == "i":
                    VB = VB[:-1] + "y"  # flies -> fly
        return VB

def stem_RB_to_JJ(RB):
### used to find the adjective that is the stem of an adverb so that the adverb
### can be added automatically to the dictionary
    JJ = RB
    if len(JJ) > 3 and JJ[-2:] == "ly":
        JJ = JJ[:-2]  # sharply -> sharp
        if not JJ in adj_dict:
            if JJ + "l" in adj_dict:
                JJ += "l" # full -> fully
            elif JJ + "le" in adj_dict:
                JJ += "le" # simply -> simple
            elif JJ[-1] == "i" and JJ[:-1] + "y" in adj_dict:
                JJ = JJ[:-1] + "y" # merrily -> merry
            elif len(JJ) > 5 and JJ[-2:] == "al" and JJ[:-2] in adj_dict:
                JJ = JJ[:-2] # angelic -> angelically
    return JJ

def stem_ative_adj(JJ):
# this function does stemming for both comparative and superlative adjectives
# after the suffix "er" or "est" has been removed
    if JJ not in adj_dict:
        if JJ + "e" in adj_dict:
            JJ += "e" # abler/ablest -> able
        elif JJ[:-1] in adj_dict:
            JJ = JJ[:-1] # bigger/biggest -> big
        elif JJ[-1] == "i" and JJ[:-1] + "y" in adj_dict:
            JJ = JJ[:-1] + "y" # easier/easiest -> easy
    return JJ


def stem_comp_JJ(JJ):
    if JJ[-2:] == "er":
        JJ = stem_ative_adj(JJ[:-2]) # fairer -> fair
    return JJ

def stem_super_JJ(JJ):
    if JJ[-3:] == "est":
        JJ = stem_ative_adj(JJ[:-3]) # fairest -> fair
    return JJ

### Spanish Stemming Fuctions

def stem_NC(NC):
    if NC not in noun_dict and len(NC) > 2 and NC[-1] == "s":   # diplomas -> diploma
        NC = NC[:-1]
    if NC not in noun_dict and NC not in c_noun_dict and len(NC) > 1:
        if NC[-1] == "a":
            NC = NC[:-1] + "o" #hermanas -> hermano
        elif NC[-1] == "e": # actor -> actores
            NC = NC[:-1]
    return NC

def stem_AQ(AQ):
    if AQ not in adj_dict and len(AQ) > 2 and AQ[-1] == "s":   # buenos -> bueno
        AQ = AQ[:-1]
    if AQ not in adj_dict and AQ not in c_adj_dict and len(AQ) > 1:
        if AQ[-1] == "a":    # buena -> bueno
            AQ = AQ[:-1] +  "o"
        elif AQ[-1] == "e": #  -> watch
            AQ = AQ[:-1]
    return AQ

def stem_RG_to_AQ(RG):
### used to find the adjective that is the stem of an adverb so that the adverb
### can be added automatically to the dictionary
    AQ = RG
    if len(AQ) > 6 and AQ[-5:] == "mente" :
        AQ = AQ[:-5]  # felizmente -> feliz
        if not AQ in adj_dict:
            if AQ[-1] == "a":
                AQ = AQ[:-1] + "o" # nuevamente -> nuevo
    return AQ


def stem_super_AQ(AQ):
# this function removes "isima" or "isimo" from the word
    if AQ not in adj_dict:
        if len(AQ) > 6 and AQ[-5:] in [chr(237) + "sima", chr(237) + "simo", "isima", "isimo"]:
            AQ = AQ[:-5]
            if AQ not in adj_dict:
                if AQ[-2:] == "qu":
                    AQ = AQ[:-2] + "co"
                elif AQ[-2] == "gu":
                    AQ = AQ[:-1] = "o"
                else:
                    AQ += "o"
    return AQ

### Language general stemming functions ###

def stem_noun(noun):
    if language == "English":
        return stem_NN(noun)
    elif language == "Spanish":
        return stem_NC(noun)

def stem_adv_to_adj(adverb):
    if language == "English":
        return stem_RB_to_JJ(adverb)
    elif language == "Spanish":
        return stem_RG_to_AQ(adverb)

def stem_super_adj(adj):
    if language == "English":
        return stem_super_JJ(adj)
    elif language == "Spanish":
        return stem_super_AQ(adj)


### General functions ###

def get_word (pair): return pair[0] # get word from (word, tag) pair
def get_tag (pair) : return pair[1] # get tag from (word, tag) pair

def sum_word_counts (word_count_dict):
### gives the total count in a word count dictionary
    count = 0
    for word in word_count_dict:
        count+= word_count_dict[word]
    return count

def find_intensifier(index):
### this function determines whether the given index is the last word (or,
### trivially, the only word) in an intensifier. If so, it returns a list
### containing, as its first element, the length of the intensifier and,
### as its second element, the modifier from the relevant intensifier dictionary
    if index < 0 or index >= len(text) or get_tag(text[index]) == "MOD": # already modifying something
        return False
    if get_word(text[index]).lower() in c_int_dict: # might be complex
        for word_mod_pair in c_int_dict[get_word(text[index]).lower()]:
            if same_lists(word_mod_pair[0][:-1],map(str.lower, map(get_word,text[index - len(word_mod_pair[0]) + 1:index]))):
                return [len(word_mod_pair[0]), word_mod_pair[1]]
    if get_word(text[index]).lower() in int_dict: # simple intensifier
        modifier = int_dict[get_word(text[index]).lower()]
        if get_word(text[index]).isupper() and use_cap_int: # if capitalized
             modifier *= capital_modifier   # increase intensification
        return [1, modifier]
    return False

def match_multiword_f(index, words):
### this function recursively matches the (partial) multi-word dictionary entry
### (words) with the corresponding part of the text (from index)
### the function returns a list containing the number of words matched (or -1
### if the match failed) and the value of any intensifier found
    if len (words) == 0:
        return [0, 0] #done
    else:
        current = words[0]
        if not isinstance(current,list):
            current = [1, [current]] # unmodified words should be appear once
        if current[0] == "0":
            return match_multiword_f(index, words[1:]) #this word done
        if current[0] == "*" or current[0] == "?": # word optional - try
            temp = match_multiword_f(index, words[1:]) # without first
            if temp[0] != -1:
                return temp
        if index == len(text):
            return [-1, 0] # reached the end of the text
        match = False
        for word_or_tag in current[1]:
            if word_or_tag.islower(): #match by word
                match = match or get_word(text[index]).lower() == word_or_tag
            elif word_or_tag.isupper(): #match by tag
                if word_or_tag == "INT": # if looking for a intensifiers
                    i = 1
                    while index + i < len(text) and text[index + i][0] not in sent_punct:
                        intensifier = find_intensifier(index + i - 1)
                        if intensifier and intensifier[0] == i:
                                result = match_multiword_f(index + i, words[1:])
                                if result[0] != -1:
                                    return [result[0] + i, intensifier[1]]
                        i += 1
                else:
                    match = match or get_tag(text[index]) == word_or_tag
        if not match:
            return [-1, 0]
        else:
            if current[0] == "*":
                temp = match_multiword_f(index + 1, words)
            elif current[0] == "+":
                temp = match_multiword_f(index + 1, [["*", current[1]]] + words[1:])
            elif current[0] == "?":
                temp = match_multiword_f(index + 1, words[1:])
            else:
                temp = match_multiword_f(index + 1, [[str(int(current[0]) - 1), current[1]]] + words[1:])
            if temp[0] == -1:
                return temp #failed
            else:
                return [temp[0] + 1, temp[1]] #success


def match_multiword_b(index, words):
### same as match_multiword_f, except it looks in the other direction
    if len (words) == 0:
        return [0, 0]
    else:
        current = words[-1]
        if not isinstance(current,list):
            current = [1, [current]]
        if current[0] == "0":
            return match_multiword_b(index, words[:-1])
        if current[0] == "*" or current[0] == "?":
            temp = match_multiword_b(index, words[:-1])
            if temp[0] != -1:
                return temp
        if index == -1:
            return [-1,0]
        match = False
        for word_or_tag in current[1]:
            if word_or_tag.islower():
                match = match or get_word(text[index]).lower() == word_or_tag
            elif word_or_tag.isupper():
                if word_or_tag == "INT":
                    intensifier = find_intensifier(index)
                    if intensifier:
                        i = intensifier[0]
                        result = match_multiword_b(index  - i, words[:-1])
                        if result[0] != -1:
                            return [result[0] + i, intensifier[1]]
                else:
                    match = match or get_tag(text[index]) == word_or_tag
        if not match:
            return [-1, 0]
        else:
            if current[0] == "*":
                temp = match_multiword_b(index - 1, words)
            elif current[0] == "+":
                temp = match_multiword_b(index - 1, words[:-1] + [["*", current[1]]])
            elif current[0] == "?":
                temp = match_multiword_b(index - 1, words[:-1])
            else:
                temp = match_multiword_b(index - 1, words[:-1] + [[str(int(current[0]) - 1), current[1]]])
            if temp[0] == -1:
                return temp
            else:
                return [temp[0] + 1, temp[1]]


def find_multiword(index, dict_entry_list):
### this function determines whether the words surrounding the key word at
### index match one of the dictionary definitions in dict_entry_list. If so,
### it returns a list containing the SO value, the number of words in the phrase,
### that are to the left of index, the number of words to the right, and the
### value of any intensifier. Any word specifically designated in the defintion
### will have its tag changed to "MOD" so that it will not be counted twice
    for dict_entry in dict_entry_list:
        words = dict_entry[0]
        SO = dict_entry[1]
        start = words.index("#")
        intensifier = 0
        if start < len(words) - 1:
            (countforward, int_temp) = match_multiword_f(index + 1, words[start +1:])
            if int_temp != 0:
                intensifier = int_temp
        else:
            countforward = 0
        if start > 0:
            (countback, int_temp) = match_multiword_b(index - 1, words[:start])
            if int_temp != 0:
                intensifier = int_temp
        else:
            countback = 0
        if countforward != -1 and countback != -1:
            for i in range(index - countback, index + countforward + 1):
                if get_word(text[i]) in dict_entry[0]:
                    text[i][1] = "MOD"
            return [SO, countback, countforward, intensifier]
    return False

def words_within_num(index, words_tags, num):
### check to see if something in words_tags is within num of index (including
### index), returns true if so
    while num > 0:
        if get_word(text[index]) in words_tags or get_tag(text[index]) in words_tags:
            return True
        num -= 1
        index -= 1
    return False


def get_sentence (index):
### extracts the sentence (a string) that contains the given index, for searching
    sent_start = index
    sent_end = index + 1
    while sent_start > 0 and sent_start not in boundaries:
        sent_start -= 1
    while sent_end < len(text) and sent_end not in boundaries:
        sent_end += 1
    return " ".join(map(get_word, text[sent_start : sent_end]))

def get_sentence_no (index):
### returns the sentence number, based on the orignal text newlines
    while index not in boundaries:
        index += 1
    return boundaries.index(index)

def get_sent_punct (index):
### get the next sentence punctuation (e.g. ?, !, or .) after the given index
    while text[index][0] not in sent_punct:
        if index == len(text) - 1: #if the end of the text is reached
            return "EOF"
        index += 1
    return get_word(text[index])

def at_boundary (index):
    if index +1 in boundaries:
        return True
    elif use_boundary_punct and get_word(text[index]) in punct:
        return True
    elif use_boundary_words and get_word(text[index]) in boundary_words:
        return True
    else:
        return False


def has_sent_irrealis(index):
### Returns true if there is a irrealis marker in the sentence and no
### punctuation or boundary word intervenes between the marker and the index
    if not (use_definite_assertion and words_within_num(index, definites, 1)):
        while index != -1 and not at_boundary(index):
            if get_word(text[index]).lower() in irrealis:
                return True
            if language == "Spanish":
                tag = get_tag(text[index])
                if len(tag) == 4 and tag[0] == "V" and ((tag[2] == "M" and use_imperative) or (tag[2] == "S" and use_subjunctive) or (tag[3] == "C" and use_conditional)):
                    return True
            index -= 1
    return False

def get_sent_highlighter(index):
### If there is a word in the sentence prior to the index but before a boundary
### marker (including a boundary marker) in the highlighter list, return it
    while index != -1 and not at_boundary(index):
        if get_word(text[index]).lower() in highlighters:
            return get_word(text[index]).lower()
        else:
            index -= 1
    return False


def find_negation(index, word_type):
### looks backwards for a negator and returns its index if one is found and
### there is no intervening puctuation or boundary word. If restricted negation
### is used (for the given word type), the search will only continue if each
### word or its tag is in the skipped list for its type
    search = True
    found = -1
    while search and not at_boundary(index) and index != -1:
        current = get_word(text[index]).lower()
        if current in negators:
            search = False
            found = index
        if restricted_neg[word_type] and current not in skipped[word_type] and get_tag(text[index]) not in skipped[word_type]:
            search = False
        index -= 1
    return found

def is_blocker(SO, index):
    if index > -1 and index < len(text) and len(text[index]) == 2:
        (modifier, tag) = text[index]
        if tag == adv_tag and modifier in adv_dict and abs(adv_dict[modifier]) >= blocker_cutoff:
            if abs(SO + adv_dict[modifier]) < abs(SO) + abs(adv_dict[modifier]):
                return True
        elif tag == adj_tag and modifier in adj_dict and abs(adj_dict[modifier]) >= blocker_cutoff:
            if abs(SO + adj_dict[modifier]) < abs(SO) + abs(adj_dict[modifier]):
                return True
        elif tag[:2] == verb_tag and modifier in verb_dict and abs(verb_dict[modifier]) >= blocker_cutoff:
            if abs(SO + verb_dict[modifier]) < abs(SO) + abs(verb_dict[modifier]):
                return True


def find_blocker(SO, index, POS):
### this function tests if the item at index is of the correct type, orientation
### and strength (as determined by blocker_cutoff) to nullify a word having the
### given SO value
    stop = False
    while index > 0 and not stop and not at_boundary(index):
        if len (text[index-1]) == 2:
            (modifier, tag) = text[index-1]
            if is_blocker(SO, index-1):
                return True
            if not modifier in skipped[POS] and not tag[:2] in skipped[POS]:
                stop = True
        index -= 1
    return False


def find_VP_boundary (index):
### forward search for the index immediately preceding punctuation or a boundary
### word or punctuation. Used to find intensifiers remote from the verb
    while not at_boundary(index) and index < len(text) - 1:
        index += 1
    return index

def is_in_predicate (index):
### backwards search for a verb of any kind. Used to determine if a comparative
### or superlative adjective is in the predicate
    while not at_boundary(index) and index > 0:
        index -= 1
        tag = get_tag(text[index])
        if (language == "English" and tag[:2] == "VB" or tag in ["AUX", "AUXG"]) or (language == "Spanish" and tag[0] == "V"):
            return True
    return False

def is_in_imperative (index):
### Tries to determine if the word at index is in an imperative based on whether
### first word in the clause is a VBP (and not a question or within the
### scope of a definite determiner)
    if get_sent_punct(index) != "?" and not (words_within_num(index, definites, 1)):
        i = index
        while i > -1 and get_word(text[i]) not in sent_punct:
            if at_boundary(index):
                return False
            i -=1
        (word, tag) = text[i+1]
        if (tag == "VBP" or tag == "VB") and word.lower() not in ["were", "was", "am"]:
            return True
    return False

def is_in_quotes (index):
### check to see if a particular word is contained within quotation marks.
### looks to a sentence boundary on the left, and one past the sentence
### boundary on the right; an item in quotes should have an odd number of
### quotation marks in the sentence on either sides
    quotes_left = 0
    quotes_right = 0
    found = False
    current = ""
    i = index
    while current not in sent_punct and i > -1:
        current = get_word(text[i])
        if current == '"' or current == "'":
            quotes_left += 1
        i -= 1
    if operator.mod(quotes_left,2) == 1:
        current = ""
        i = index
        while not found and current not in sent_punct and i < len(text):
            current = get_word(text[i])
            if current == '"' or current == "'":
                quotes_right += 1
            i += 1
        if  (quotes_left - quotes_right == 1) and i < len(text) - 1 and get_word(text[i+1]) == '"':
            quotes_right += 1
        if operator.mod(quotes_right,2) == 1:
            found = True
    return found



def apply_other_modifiers (SO, index, leftedge):
### several modifiers that apply equally to all parts of speech based on
### their context. Words in all caps, in a sentences ending with an
### exclamation mark, or with some other highlighter are intensified,
### while words appearing in a question or quotes or with some other
### irrealis marker are nullified
        output = []
        if  use_cap_int and get_word(text[index]).isupper():
            output.append("X " + str(capital_modifier) +  " (CAPITALIZED)")
            SO *= capital_modifier
        if  use_exclam_int and get_sent_punct(index) == "!":
            output.append("X " + str(exclam_modifier) + " (EXCLAMATION)")
            SO *= exclam_modifier
        if  use_highlighters:
            highlighter = get_sent_highlighter(leftedge)
            if highlighter:
                output.append("X " + str(highlighters[highlighter]) + " (HIGHLIGHTED)")
                SO *= highlighters[highlighter]
        if use_quest_mod and get_sent_punct(index) == "?" and not (use_definite_assertion and words_within_num(leftedge, definites, 1)):
            output.append("X 0 (QUESTION)")
            SO = 0
        if language == "English" and use_imperative and is_in_imperative(leftedge):
            output.append("X 0 (IMPERATIVE)")
            SO = 0
        if use_quote_mod and is_in_quotes(index):
            output.append("X 0 (QUOTES)")
            SO = 0
        if  use_irrealis and has_sent_irrealis(leftedge):
            output.append ("X 0 (IRREALIS)")
            SO = 0
        return [SO, output]

def fix_all_caps_English():
### tagger tags most all uppercase words as NNP, this function tries to see if
### they belong in another dictionary (if so, it changes the tag)
    for i in range(0, len(text)):
        if len(text[i]) == 2:
            (word, tag) = text[i]
            if len(word) > 2 and word.isupper() and tag == "NNP":
                word = word.lower()
                if word in adj_dict or word in c_adj_dict:
                    text[i][1] = "JJ"
                elif word in adv_dict or word in c_adv_dict:
                    text[i][1] == "RB"

                else:
                    ex_tag = "" # verbs need to be stemmed
                    if word[-1] == "s":
                        word = stem_VB(word, "Z")
                        ex_tag = "Z"
                    elif word[-3:] == "ing":
                        word = stem_VB(word, "G")
                        ex_tag = "G"
                    elif word[-2:] == "ed":
                        word = stem_VB(word, "D")
                        ex_tag = "D"
                    if word in verb_dict or word in c_verb_dict:
                        text[i][1] = "VB" + ex_tag

def fix_all_caps_Spanish():
### tagger tags most all uppercase words as NP, this function tries to see if
### they belong in another dictionary (if so, it changes the tag)
    for i in range(0, len(text)):
        if len(text[i]) == 2:
            (word, tag) = text[i]
            if len(word) > 2 and word.isupper() and tag == "NP":
                word = word.lower()
                alt_word = stem_AQ(word)
                if alt_word in adj_dict or word in c_adj_dict:
                    text[i][1] = "AQ"
                else:
                    alt_word = stem_adv_to_adj(word)
                    if alt_word in adj_dict:
                        text[i][1] == "RG"

def fix_all_caps():
    if language == "English":
        fix_all_caps_English()
    elif language == "Spanish":
        fix_all_caps_Spanish()


def apply_weights (word_SO, index):
### this is the last step in the calculation, external weights and negation
### weights are applied
    if use_heavy_negation and word_SO < 0: # weighing of negative SO
        word_SO *= neg_multiplier          # items
        if output_calculations:
            richout.write(" X " + str(neg_multiplier) + " (NEGATIVE)")
    word_SO *= weights[index] # apply weights
    if weights[index] != 1:
        if output_calculations:
            richout.write (" X " + str(weights[index]) + " (WEIGHTED)")
    if output_calculations:
        richout.write (" = " + str(word_SO) + "\n")
    return word_SO

def apply_weights_adv (word_SO, index, output):
### this is the last step in the calculation, external weights and negation
### weights are applied
    if use_heavy_negation and word_SO < 0: # weighing of negative SO
        word_SO *= neg_multiplier          # items
        if output_calculations:
            output += " X " + str(neg_multiplier) + " (NEGATIVE)"
    word_SO *= weights[index] # apply weights
    if weights[index] != 1:
        if output_calculations:
            output += " X " + str(weights[index]) + " (WEIGHTED)"
    if output_calculations:
        output += (" = " + str(word_SO) + "\n")
    return [word_SO, output]


### SO calculators by part of speech
### All of these sub-calculators do more or less the same thing:
### Stem the word (if necessary)
### look for intensifiers
### look for negation
### look for negation external intensifiers (e.g. I really didn't like it)
### apply intensification and negation, if necessary
### apply other types of modifiers, including those relevant to capitalization,
### punctuation, blocking, repitition, etc.
### print the output
###
### differences that are particular to certain parts of speech are noted below

def get_noun_SO(index):
    NN = get_word(text[index])
    original_NN = NN
    if NN.isupper():
        NN = NN.lower() # if all upper case, change to lower case
    if get_word(text[index - 1]) in sent_punct:
        NN = NN.lower() # change the word to lower case if sentence initial
    ntype = get_tag(text[index])[2:]
    NN = stem_noun(NN)
    if NN in c_noun_dict:
        multiword_result = find_multiword(index, c_noun_dict[NN])
    else:
        multiword_result = False
    if NN not in noun_dict and not multiword_result:
        return 0
    else:
        if multiword_result:
            (noun_SO, backcount, forwardcount, int_modifier) = multiword_result
            output = list(map(get_word, text[index - backcount:index + forwardcount + 1]))
            i = index - backcount - 1
        else:
            int_modifier = 0
            output = [original_NN]
            noun_SO = noun_dict[NN]
            i = index - 1
        if use_intensifiers:
            if language == "Spanish": # look for post-nominal adj
                intensifier = find_intensifier(index +1) # look for post-nominal adj
                if intensifier:
                    int_modifier += intensifier[1]
                    text[index + 1][1] = "MOD"
                    output += [get_word(text[index+1])]
            intensifier = find_intensifier(i)
            if intensifier:
                int_modifier = intensifier[1]
                for j in range (0, intensifier[0]):
                    text[i][1] = "MOD" # block modifier being used twice
                    i -= 1
                output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        negation = find_negation(i, noun_tag)
        if negation != -1:
            output = list(map(get_word, text[negation:i+1])) + output
            if use_intensifiers:
                int_modifier_negex = 0
                i = negation - 1
                if language == "English":
                    while text[i][0] in skipped[adj_tag]:
                        i -= 1
                intensifier = find_intensifier(i)
                if intensifier:
                    int_modifier_negex = intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        output.append(str(noun_SO))
        if int_modifier != 0:
            noun_SO = noun_SO *(1+int_modifier)
            output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
        elif use_blocking and find_blocker(noun_SO, index, noun_tag):
            output.append("X 0 (BLOCKED)")
            noun_SO = 0
        if use_negation and negation != -1:
            if neg_negation_nullification and noun_SO < 0:
                neg_shift = abs(noun_SO)
            elif polarity_switch_neg or (limit_shift and abs(noun_SO) * 2 < noun_neg_shift):
                neg_shift = abs(noun_SO) * 2
            else:
                neg_shift = noun_neg_shift
            if noun_SO > 0:
                noun_SO -= neg_shift
                output.append ("- "+ str(neg_shift))
            elif noun_SO < 0:
                noun_SO += neg_shift
                output.append ("+ "+ str(neg_shift))
            output.append("(NEGATED)")
            if use_intensifiers and int_modifier_negex != 0:
                noun_SO *=(1+int_modifier_negex)
                output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
        (noun_SO, new_out) = apply_other_modifiers(noun_SO, index, i)
        output += new_out
        if noun_SO != 0:
            if int_modifier != 0 and int_multiplier != 1:
                noun_SO *= int_multiplier
                output.append("X " + str(int_multiplier) + " (INT_WEIGHT)")
            if NN not in word_counts[0]:
                word_counts[0][NN] = 1
            else:
                word_counts[0][NN] += 1
                if negation == -1:
                    if use_word_counts_lower:
                        noun_SO /= word_counts[0][NN]
                        output.append("X 1/" + str(word_counts[0][NN]) + " (REPEATED)")
                    if use_word_counts_block:
                        noun_SO = 0
                        output.append("X 0 (REPEATED)")
        if noun_multiplier != 1:
            noun_SO *= noun_multiplier
            output.append("X " + str(noun_multiplier) + " (NOUN)")
        if output_calculations:
            for word in output:
                richout.write(word + " ")
        if output_calculations and noun_SO == 0:
            richout.write("= 0\n")
        return noun_SO

def get_verb_SO(index):
### Verbs are special because their adverbal modifiers are not necessarily
### adjecent to the verb; a special search is done for clause
### final modifiers
    VB = get_word(text[index])
    original_VB = VB
    if VB.isupper():
        VB = VB.lower()   # if all upper case, change to lower case
    if get_word(text[index - 1]) in sent_punct:
        VB = VB.lower()  # change the word to lower case if sentence initial
    if language == "English":
        vtype = get_tag(text[index])[2:]
        VB = stem_VB(VB, vtype)
    if VB in c_verb_dict:
        multiword_result = find_multiword(index, c_verb_dict[VB])
    else:
        multiword_result = False
    if VB in not_wanted_verb:
        return 0
    elif VB not in verb_dict and not multiword_result:
        return 0
    else:
        if multiword_result:
            (verb_SO, backcount, forwardcount, int_modifier) = multiword_result
            output = list(map(get_word, text[index - backcount:index + forwardcount + 1]))
            i = index - backcount - 1
        else:
            int_modifier = 0
            output = [original_VB]
            verb_SO = verb_dict[VB]
            i = index - 1
        if use_intensifiers:
            intensifier = find_intensifier(i)
            if intensifier:
                int_modifier += intensifier[1]
                for j in range (0, intensifier[0]):
                    text[i][1] = "MOD" # block modifier being used twice
                    i -= 1
                output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
            if use_clause_final_int: # look for clause-final modifier
                edge = find_VP_boundary(index)
                intensifier = find_intensifier(edge - 1)
                if intensifier:
                    int_modifier = intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[edge - 1 - j][1] = "MOD"
                    output = output + list(map(get_word, text[index + 1: edge]))
        negation = find_negation(i, verb_tag)
        if negation != -1:
            output = list(map(get_word, text[negation:i+1])) + output
            if use_intensifiers:
                int_modifier_negex = 0
                i = negation - 1
                if language == "English":
                    while text[i][0] in skipped["JJ"]:
                        i -= 1
                intensifier = find_intensifier(i)
                if intensifier:
                    int_modifier_negex = intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        output.append(str(verb_SO))
        if int_modifier != 0:
            verb_SO = verb_SO *(1+int_modifier)
            output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
        elif use_blocking and find_blocker(verb_SO, index, verb_tag):
            output.append("X 0 (BLOCKED)")
            verb_SO = 0
        if use_negation and negation != -1:
            if neg_negation_nullification and verb_SO < 0:
                neg_shift = abs(verb_SO)
            elif polarity_switch_neg or (limit_shift and abs(verb_SO) * 2 < verb_neg_shift):
                neg_shift = abs(verb_SO) * 2
            else:
                neg_shift = verb_neg_shift
            if verb_SO > 0:
                verb_SO -= neg_shift
                output.append ("- "+ str(neg_shift))
            elif verb_SO < 0:
                verb_SO += neg_shift
                output.append("+ " + str(neg_shift))
            output.append("(NEGATED)")
            if use_intensifiers and int_modifier_negex != 0:
                verb_SO *=(1+int_modifier_negex)
                output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
        (verb_SO, new_out) = apply_other_modifiers(verb_SO, index, i)
        output += new_out
        if verb_SO != 0:
            if int_modifier != 0 and int_multiplier != 1:
                verb_SO *= int_multiplier
                output.append("X " + str(int_multiplier) + " (INT_WEIGHT)")
            if VB not in word_counts[1]:
                word_counts[1][VB] = 1
            else:
                word_counts[1][VB] += 1
                if negation == -1:
                    if use_word_counts_lower:
                        verb_SO /= word_counts[1][VB]
                        output.append("X 1/" + str(word_counts[1][VB]) + " (REPEATED)")
                    if use_word_counts_block:
                        verb_SO = 0
                        output.append("X 0 (REPEATED)")
        if verb_multiplier != 1:
            verb_SO *= verb_multiplier
            output.append("X " + str(verb_multiplier) + " (VERB)")
        if output_calculations:
            for word in output:
                richout.write(word + " ")
        if output_calculations and verb_SO == 0:
            richout.write("= 0\n") # calculation is over
        return verb_SO

def get_adj_SO(index):
### Comparative and superlative adjectives require special stemming, and are
### treated as if they have been intensified with "more" or "most". Non-
### predicative uses of this kind of adjective are often not intended to
### express sentiment, and are therefore ignored. Adjectives often have
### more than one intensifier (e.g. really very good) so the search for
### intensifiers is iterative.
    JJ = get_word(text[index])
    original_JJ = JJ
    int_modifier = 0
    if JJ.isupper():
        JJ = JJ.lower()      # if all upper case, change to lower case
    if get_word(text[index - 1]) in sent_punct:
        JJ = JJ.lower()    # change the word to lower case if sentence initial
    if language == "English":
        adjtype = get_tag(text[index])[2:]
        if not use_comparatives and (adjtype == "R" or get_word(text[index -1]) in comparatives):
            return 0
        if not use_superlatives and (adjtype == "S" or get_word(text[index-1]) in superlatives or JJ in ["best","worst"]):
            return 0
        if adjtype == "R" and JJ not in adj_dict and JJ not in not_wanted_adj:
            JJ = stem_comp_JJ(JJ)
            if use_intensifiers:
                int_modifier += int_dict["more"]
        elif adjtype == "S" and JJ not in adj_dict and JJ not in not_wanted_adj:
            JJ = stem_super_adj(JJ)
            if use_intensifiers:
                int_modifier += 1
    elif language == "Spanish":
        JJ = stem_AQ(JJ)
        if not use_comparatives and (get_word(text[index -1]) in comparatives):
            return 0
        if not use_superlatives and ((get_word(text[index-1]) in comparatives and get_tag(text[index-2]) == "DA")or (AQ in ["mejor","p"+chr(233) + "simo"] and get_tag(text[index-2]) == "DA")):
            return 0
        if JJ not in adj_dict and JJ not in not_wanted_adj:
            new_JJ = stem_super_adj(JJ)
            if use_intensifiers and use_superlatives and new_JJ != JJ:
                JJ = new_JJ
                int_modifier += 1
    if JJ in c_adj_dict:
        multiword_result = find_multiword(index, c_adj_dict[JJ])
    else:
        multiword_result = False
    if JJ in not_wanted_adj:
        return 0
    elif language == "English" and ((adjtype == "S" or get_word(text[index-1]) in superlatives) and (not words_within_num(index, definites, 2) or not is_in_predicate(index)) or ((adjtype == "R" or get_word(text[index -1]) in comparatives) and not is_in_predicate(index))):
        return 0        # superlatives must be preceded by a definite and be in the predicate         # comparatives must be in the predicate
    elif JJ not in adj_dict and not multiword_result:
        return 0
    else:
        if multiword_result:
            (adj_SO, backcount, forwardcount, int_modifier) = multiword_result
            output = list(map(get_word, text[index - backcount:index + forwardcount + 1]))
            i = index - backcount - 1
        else:
            output = [original_JJ]
            adj_SO = adj_dict[JJ]
            i = index - 1
        if (language == "English" and get_tag(text[i]) == "DET" or get_word(text[i]) == "as") or (language == "Spanish" and get_tag(text[i]) == "DA" or get_tag(text[i]) == "DI" or get_word(text[i]) == "tan"): # look past determiners and "as" for intensification
            i -= 1
        if use_intensifiers:
            intensifier = 1
            while intensifier: # keep looking for instensifiers until no more
                intensifier = find_intensifier(i)           # are found
                if intensifier:
                    int_modifier += intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        negation = find_negation(i, adj_tag)
        if negation != -1:
            output = list(map(get_word, text[negation:i+1])) + output
            if use_intensifiers:
                int_modifier_negex = 0
                i = negation - 1
                if language == "English":
                    while text[i][0] in skipped["JJ"]:
                        i -= 1
                intensifier = find_intensifier(i)
                if intensifier:
                    int_modifier_negex = intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        output.append(str(adj_SO))
        if int_modifier != 0:
            adj_SO = adj_SO *(1+int_modifier)
            output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
            if ((language == "English" and adjtype == "R") or get_word(text[index -1]) in comparatives):
                output.append("(COMPARATIVE)")
            if (language == "English" and (adjtype == "S" or get_word(text[index-1]) in superlatives)):
                output.append("(SUPERLATIVE)")
            elif (language == "Spanish" and (get_word(text[index-1]) in comparatives and get_tag(text[index-2]) == "DA")or (JJ in ["mejor","p"+chr(233) + "simo"] and get_tag(text[index-2]) == "DA")):
                output.append("(SUPERLATIVE)")
        elif use_blocking and find_blocker(adj_SO, index, adj_tag):
            output.append("X 0 (BLOCKED)")
            adj_SO = 0
        if use_negation and negation != -1:
            if neg_negation_nullification and adj_SO < 0:
                neg_shift = abs(adj_SO)
            elif polarity_switch_neg or (limit_shift and abs(adj_SO) * 2 < adj_neg_shift):
                neg_shift = abs(adj_SO) * 2
            else:
                neg_shift = adj_neg_shift
            if adj_SO > 0:
                adj_SO -= neg_shift
                output.append ("- "+ str(neg_shift))
            elif adj_SO < 0:
                adj_SO += neg_shift
                output.append ("+ "+ str(neg_shift))
            output.append("(NEGATED)")
            if use_intensifiers and int_modifier_negex != 0:
                adj_SO *=(1+int_modifier_negex)
                output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
        (adj_SO, new_out) = apply_other_modifiers(adj_SO, index, i)
        output += new_out
        if int_modifier != 0 and int_multiplier != 1:
            adj_SO *= int_multiplier
            output.append("X " + str(int_multiplier) + " (INT_WEIGHT)")
        if JJ not in word_counts[2]:
            word_counts[2][JJ] = 1
        else:
            word_counts[2][JJ] += 1
            if negation == -1:
                if use_word_counts_lower:
                    adj_SO /= word_counts[2][JJ]
                    output.append("X 1/" + str(word_counts[2][JJ]) + " (REPEATED)")
                if use_word_counts_block:
                    adj_SO = 0
                    output.append("X 0 (REPEATED)")
        if adj_multiplier != 1:
            adj_SO *= adj_multiplier
            output.append("X " + str(adj_multiplier) + " (ADJECTIVE)")
        if output_calculations:
            for word in output:
                richout.write(word + " ")
        if output_calculations and adj_SO == 0:
            richout.write("= 0\n") # calculation is over
        return adj_SO

def get_adv_SO(index):
### There are two special things to note about dealing with adverbs: one is that
### their SO value can be derived automatically from the lemma in the
### adjective dictionary. The other is the special handling of "too", which
### is counted only when it does not appear next to punctuation (which rules out
### most cases of "too" in the sense of "also")
    RB = get_word(text[index])
    original_RB = RB
    if RB.isupper():
        RB = RB.lower()   # if all upper case, change to lower case
    if get_word(text[index - 1]) in sent_punct:
        RB = RB.lower() # change the word to lower case if sentence initial
    if adv_learning and RB not in adv_dict and RB not in not_wanted_adv:
        JJ = stem_adv_to_adj(RB) # stem the adverb to its corresponding adj
        if JJ in adj_dict:
            adv_dict[RB] = adj_dict[JJ] # take its SO value
            new_adv_dict[RB] = adj_dict[JJ]
    if RB in c_adv_dict:
        multiword_result = find_multiword(index, c_adv_dict[RB])
    else:
        multiword_result = False
    if RB in not_wanted_adv or (language == "English" and (RB == "too" and index < len(text) - 1 and get_word(text[index + 1]) in punct) or (RB == "well" and index < len(text) - 1 and get_word(text[index + 1]) == ",")):
        return [0,""]                    # do not count too next to punctuation
    elif RB not in adv_dict and not multiword_result:
        return [0,""]
    else:
        if multiword_result:
            (adv_SO, backcount, forwardcount, int_modifier) = multiword_result
            output = list(map(get_word, text[index - backcount:index + forwardcount + 1]))
            i = index - backcount - 1
        else:
            int_modifier = 0
            output = [original_RB]
            adv_SO = adv_dict[RB]
            i = index - 1
        if (language == "English" and get_word(text[i]) == "as") or (language == "Spanish" and get_word(text[i]) == "tan"): # look past "as" for intensification
            i -= 1
        if use_intensifiers:
            intensifier = find_intensifier(i)
            if intensifier:
                int_modifier += intensifier[1]
                for j in range (0, intensifier[0]):
                    text[i][1] = "MOD" # block modifier being used twice
                    i -= 1
                output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        negation = find_negation(i, adv_tag)
        if negation != -1:
            output = list(map(get_word, text[negation:i+1])) + output
            if use_intensifiers:
                int_modifier_negex = 0
                i = negation - 1
                if language == "English":
                    while text[i][0] in skipped["JJ"]:
                        i -= 1
                intensifier = find_intensifier(i)
                if intensifier:
                    int_modifier_negex = intensifier[1]
                    for j in range (0, intensifier[0]):
                        text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(get_word, text[i + 1:i + intensifier[0] + 1])) + output
        output.append(str(adv_SO))
        if int_modifier != 0:
            adv_SO = adv_SO *(1+int_modifier)
            output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
        elif use_blocking and find_blocker(adv_SO, index, adv_tag):
            output.append("X 0 (BLOCKED)")
            adv_SO = 0
        if use_negation and negation != -1:
            if neg_negation_nullification and adv_SO < 0:
                neg_shift = abs(adv_SO)
            elif polarity_switch_neg or (limit_shift and abs(adv_SO) * 2 < adv_neg_shift):
                neg_shift = abs(adv_SO) * 2
            else:
                neg_shift = adv_neg_shift
            if adv_SO > 0:
                adv_SO -= neg_shift
                output.append ("- "+ str(neg_shift))
            elif adv_SO < 0:
                adv_SO += neg_shift
                output.append ("+ "+ str(neg_shift))
            output.append("(NEGATED)")
            if use_intensifiers and int_modifier_negex != 0:
                adv_SO *=(1+int_modifier_negex)
                output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
        (adv_SO, new_out) = apply_other_modifiers(adv_SO, index, i)
        output += new_out
        if adv_SO != 0:
            if int_modifier != 0 and int_multiplier != 1:
                adv_SO *= int_multiplier
                output.append("X " + str(int_multiplier) + " (INT_WEIGHT)")
            if RB not in word_counts[3]:
                word_counts[3][RB] = 1
            else:
                word_counts[3][RB] += 1
                if negation == -1:
                    if use_word_counts_lower:
                        adv_SO /= word_counts[3][RB]
                        output.append("X 1/" + str(word_counts[3][RB]) + " (REPEATED)")
                    if use_word_counts_block:
                        adv_SO = 0
                        output.append("X 0 (REPEATED)")
        if adv_multiplier != 1:
            adv_SO *= adv_multiplier
            output.append("X " + str(adv_multiplier) + " (ADVERB)")
        full_output = ""
        if output_calculations:
            for word in output:
                full_output += word + " "
        if output_calculations and adv_SO == 0:
            full_output += ("= 0\n") # calucation is over
        return [adv_SO, full_output]


 ### Main script ###

### Note that there are 4 (or even 5) iterations through the text. The
### rationale for interating seperately for each part of speech (and the
### ordering of those iterations) is that adverbs and adjectives which are used
### as intensifiers of nouns, verbs, or adjectives need to be marked so they
### are not counted twice.


load_dictionaries()
fill_text_and_weights(infile)


if output_sentences:
    sentence_SO = {}

adv_count = len(adv_dict) # for determining if there are new adverbs

if output_calculations:
    richout.write("######\n---------\n" + os.path.basename(args.input) + "\n---------\nText Length: " + str(len(text)) + "\n---------\n")

if fix_cap_tags:
    fix_all_caps()

if use_nouns:
    nouns_SO = 0
    if output_calculations:
        richout.write("Nouns:\n-----\n")
    for index in range(0, len(text)):
        if len(text[index]) == 2:
            (word, tag) = text[index]
            if tag[:2] == noun_tag:
                word_SO = get_noun_SO(index)
                if word_SO != 0:
                    word_SO = apply_weights(word_SO, index)
                    nouns_SO += word_SO
                if output_sentences:
                    sentence_no = get_sentence_no(index)
                    if sentence_no not in sentence_SO:
                        sentence_SO[sentence_no] = word_SO
                    else:
                        sentence_SO[sentence_no] += word_SO
    noun_count = sum_word_counts(word_counts[0])
    if noun_count > 0:
        if output_calculations:
            richout.write("-----\nAverage SO: " + str(nouns_SO/noun_count) + "\n-----\n")
        text_SO += nouns_SO
        SO_counter += noun_count
    else:
        if output_calculations:
            richout.write("-----\nAverage SO: 0\n-----\n")


if use_verbs:
    if output_calculations:
        richout.write("Verbs:\n-----\n")
    verbs_SO = 0
    for index in range(0, len(text)):
        if len(text[index]) == 2:
            (word, tag) = text[index]
            if tag[:2] == verb_tag:
                word_SO = get_verb_SO(index)
                if word_SO != 0:
                    word_SO = apply_weights(word_SO, index)
                    verbs_SO += word_SO
                if output_sentences:
                    sentence_no = get_sentence_no(index)
                    if sentence_no not in sentence_SO:
                        sentence_SO[sentence_no] = word_SO
                    else:
                        sentence_SO[sentence_no] += word_SO
    verb_count = sum_word_counts(word_counts[1])
    if verb_count > 0:
        if output_calculations:
            richout.write("-----\nAverage SO: " + str(verbs_SO/verb_count) + "\n-----\n")
        text_SO += verbs_SO
        SO_counter += verb_count
    else:
        if output_calculations:
            richout.write("-----\nAverage SO: 0\n-----\n")

if use_adjectives:
    adjs_SO = 0
    if output_calculations:
        richout.write("Adjectives:\n-----\n")
    for index in range(0, len(text)):
        if len(text[index]) == 2:
            (word, tag) = text[index]
            if tag[:2] == adj_tag:
                word_SO = get_adj_SO(index)
                if word_SO != 0:
                    word_SO = apply_weights(word_SO, index)
                    adjs_SO += word_SO
                if output_sentences:
                    sentence_no = get_sentence_no(index)
                    if sentence_no not in sentence_SO:
                        sentence_SO[sentence_no] = word_SO
                    else:
                        sentence_SO[sentence_no] += word_SO
    adj_count = sum_word_counts(word_counts[2])
    if adj_count > 0:
        if output_calculations:
            richout.write("-----\nAverage SO: " + str(adjs_SO/adj_count) + "\n-----\n")
        text_SO += adjs_SO
        SO_counter += adj_count
    else:
        if output_calculations:
            richout.write("-----\nAverage SO: 0\n-----\n")

adv_outputs = []
if use_adverbs:
    advs_SO = 0
    if output_calculations:
        richout.write("Adverbs:\n-----\n")
    for index in range(len(text) - 1, -1, -1): # backwards iteration, since
        if len(text[index]) == 2:
            (word, tag) = text[index]             # adverbs modify adverbs
            if tag[:2] == adv_tag:
                (word_SO,output) = get_adv_SO(index)
                if word_SO != 0:
                    (word_SO,output) = apply_weights_adv(word_SO, index, output)
                    advs_SO += word_SO
                    adv_outputs.insert(0,output)
                if output_sentences:
                    sentence_no = get_sentence_no(index)
                    if sentence_no not in sentence_SO:
                        sentence_SO[sentence_no] = word_SO
                    else:
                        sentence_SO[sentence_no] += word_SO
        adv_count = sum_word_counts(word_counts[3])
    for output in adv_outputs:
        richout.write(output)
    if adv_count > 0:
        if output_calculations:
            richout.write("-----\nAverage SO: " + str(advs_SO/adv_count) + "\n-----\n")
        text_SO += advs_SO
        SO_counter += adv_count
    else:
        if output_calculations:
            richout.write("-----\nAverage SO: 0\n-----\n")


if SO_counter > 0:
    text_SO = text_SO / SO_counter #calculate the final SO for the text

basicout.write(os.path.basename(args.input) + "\t" + str(text_SO) + "\n")
if output_sentences:
    richout.write("-----\nSO by Sentence\n-----\n")
    for i in range(len(boundaries)):
        richout.write(get_sentence(boundaries[i] -1) + " ")
        if i in sentence_SO:
            richout.write(str(sentence_SO[i]) + "\n")
        else:
            richout.write("0\n")
if output_calculations:
    richout.write("---------\nTotal SO: " + str(text_SO) + "\n---------\n")

if adv_learning and new_adv_dict: # output the new adverb
    f = open(adv_dict_path, "a")  # dictionary
    for adverb in new_adv_dict:
        f.write(adverb + "\t" + str(int(adv_dict[adverb])) + "\n")
    f.close()

basicout.close()
richout.close()