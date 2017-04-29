import argparse
import json
import csv
import os
import operator

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

    args = parser.parse_args()
    return args


def load_json(json_file_path):
    '''
    Convert a json file to dictionary.
    :param json_file_path: the path of the json file
    :return: dictionary
    '''
    with open(json_file_path) as json_file:
        dct = json.load(json_file)
    return dct


def same_lists(lst1, lst2):
    '''
    Check if 2 lists exactly the same (same elements, same order)
    :param lst1: list 1
    :param lst2: list 2
    :return: if they are exactly the same, return True, otherwise False
    '''
    return lst1 == lst2


class SentimentCalculator():
    def __init__(self, config, word_lists, richout, file_sentiment):

        # Initialize Flags
        self.language = config["Flags"]["language"]
        self.use_adjectives = config["Flags"]["use_adjectives"]
        self.use_nouns = config["Flags"]["use_nouns"]
        self.use_verbs = config["Flags"]["use_verbs"]
        self.use_adverbs = config["Flags"]["use_adverbs"]
        self.use_intensifiers = config["Flags"]["use_intensifiers"]
        self.use_negation = config["Flags"]["use_negation"]
        self.use_comparatives = config["Flags"]["use_comparatives"]
        self.use_superlatives = config["Flags"]["use_superlatives"]
        self.use_multiword_dictionaries = config["Flags"]["use_multiword_dictionaries"]
        self.use_extra_dict = config["Flags"]["use_extra_dict"]
        self.use_weight_by_location = config["Flags"]["use_weight_by_location"]
        self.use_irrealis = config["Flags"]["use_irrealis"]
        self.use_subjunctive = config["Flags"]["use_subjunctive"]
        self.use_imperative = config["Flags"]["use_imperative"]
        self.use_conditional = config["Flags"]["use_conditional"]
        self.use_highlighters = config["Flags"]["use_highlighters"]
        self.use_cap_int = config["Flags"]["use_cap_int"]
        self.fix_cap_tags = config["Flags"]["fix_cap_tags"]
        self.use_exclam_int = config["Flags"]["use_exclam_int"]
        self.use_quest_mod = config["Flags"]["use_quest_mod"]
        self.use_quote_mod = config["Flags"]["use_quote_mod"]
        self.use_definite_assertion = config["Flags"]["use_definite_assertion"]
        self.use_clause_final_int = config["Flags"]["use_clause_final_int"]
        self.use_heavy_negation = config["Flags"]["use_heavy_negation"]
        self.use_word_counts_lower = config["Flags"]["use_word_counts_lower"]
        self.use_word_counts_block = config["Flags"]["use_word_counts_block"]
        self.use_blocking = config["Flags"]["use_blocking"]
        self.adv_learning = config["Flags"]["adv_learning"]
        self.limit_shift = config["Flags"]["limit_shift"]
        self.neg_negation_nullification = config["Flags"]["neg_negation_nullification"]
        self.polarity_switch_neg = config["Flags"]["polarity_switch_neg"]
        self.restricted_neg = config["Flags"]["restricted_neg"]
        self.simple_SO = config["Flags"]["simple_SO"]
        self.use_boundary_words = config["Flags"]["use_boundary_words"]
        self.use_boundary_punct = config["Flags"]["use_boundary_punctuation"]

        # Initialize Dictionaries Paths
        self.dic_dir = config["Dictionaries"]["dic_dir"]
        self.adj_dict_path = self.dic_dir + config["Dictionaries"]["adj_dict"]
        self.adv_dict_path = self.dic_dir + config["Dictionaries"]["adv_dict"]
        self.noun_dict_path = self.dic_dir + config["Dictionaries"]["noun_dict"]
        self.verb_dict_path = self.dic_dir + config["Dictionaries"]["verb_dict"]
        self.int_dict_path = self.dic_dir + config["Dictionaries"]["int_dict"]
        if self.use_extra_dict and config["Dictionaries"]["extra_dict"]:
            self.extra_dict_path = self.dic_dir + config["Dictionaries"]["extra_dict"]
        else:
            self.extra_dict_path = ""

        # Initialize Modifiers
        self.adj_multiplier = float(config["Modifiers"]["adj_multiplier"])
        self.adv_multiplier = float(config["Modifiers"]["adv_multiplier"])
        self.verb_multiplier = float(config["Modifiers"]["verb_multiplier"])
        self.noun_multiplier = float(config["Modifiers"]["noun_multiplier"])
        self.int_multiplier = float(config["Modifiers"]["int_multiplier"])
        self.neg_multiplier = float(config["Modifiers"]["neg_multiplier"])
        self.capital_modifier = float(config["Modifiers"]["capital_modifier"])
        self.exclam_modifier = float(config["Modifiers"]["exclam_modifier"])
        self.verb_neg_shift = float(config["Modifiers"]["verb_neg_shift"])
        self.noun_neg_shift = float(config["Modifiers"]["noun_neg_shift"])
        self.adj_neg_shift = float(config["Modifiers"]["adj_neg_shift"])
        self.adv_neg_shift = float(config["Modifiers"]["adv_neg_shift"])
        self.blocker_cutoff = float(config["Modifiers"]["blocker_cutoff"])

        # Initialize Output
        self.output_calculations = config["Output"]["output_calculations"]
        self.output_sentences = config["Output"]["output_sentences"]
        self.output_unknown = config["Output"]["output_unknown"]
        self.output_used = config["Output"]["output_used"]
        self.output_used_lemma = config["Output"]["output_used_lemma"]
        self.search = config["Output"]["search"]
        self.contain_all_words = config["Output"]["contain_all_words"]

        # Initialize Lists
        self.weight_tags= config["Lists"]["weight_tags"]
        self.weights_by_location = config["Lists"]["weights_by_location"]
        self.highlighters = config["Lists"]["highlighters"]
        self.irrealis = config["Lists"]["irrealis"]
        self.boundary_words = config["Lists"]["boundary_words"]

        # Initialize Internal Word Lists
        self.not_wanted_adj = word_lists["not_wanted_adj"]
        self.not_wanted_adv = word_lists["not_wanted_adv"]
        self.not_wanted_verb = word_lists["not_wanted_verb"]
        self.negators = word_lists["negators"]
        self.punct = word_lists["punct"]
        self.sent_punct = word_lists["sent_punct"]
        self.skipped = word_lists["skipped"]
        self.comparatives = word_lists["comparatives"]
        if self.language == "English":
            self.superlatives = word_lists["superlatives"]
        self.definites = word_lists["definites"]
        if self.language == "Spanish":
            self.accents = word_lists["accents"]
        self.noun_tag = word_lists["noun_tag"]
        self.verb_tag = word_lists["verb_tag"]
        self.adj_tag = word_lists["adj_tag"]
        self.adv_tag = word_lists["adv_tag"]
        self.macro_replace = word_lists["macro_replace"]

        # Initialize Text
        self.text = [] # the text is a list of word, tag lists
        self.weights = [] # weights should be the same length as the text, one for each token
        self.word_counts = [{},{},{},{}] # keeps track of number of times each word lemma appears in the text
        self.text_SO = 0 # a sum of the SO value of all the words in the text
        self.SO_counter = 0 # a count of the number of SO carrying terms
        self.boundaries = [] # the location of newline boundaries from the input

        # Initialize Empty Dictionaries
        self.single_adj_dict = {}
        self.single_adv_dict = {}
        self.single_noun_dict = {}
        self.single_verb_dict = {}
        self.single_int_dict = {}
        self.single_extra_dict = {}
        self.multi_adj_dict = {}
        self.multi_adv_dict = {}
        self.multi_noun_dict = {}
        self.multi_verb_dict = {}
        self.multi_int_dict = {}
        self.multi_extra_dict = {}
        self.new_adv_dict = {}
        self.sentence_SO = {}

        # Output files
        self.richout = open(richout, 'a')
        self.file_sentiment = open(file_sentiment, 'a')


    def has_accent(self, word):
        '''
        For Spanish, check whether the word has accent
        :param word: a Spanish word
        :return: True or False
        '''
        for accent in self.accents:
            if accent in word:
                return True
        return False


    def remove_accents(self, word):
        '''
        Replace the accent in a Spanish word with english character
        :param word: A Spanish word
        :return: converted word
        '''
        for accent in self.accents:
            word = word.replace(accent, self.accents[accent])
        return word


    def get_multiword_entries (self, word_string):
        '''
        Coverts the multiword dictionary entry in a file to something that can be accessed by the calculator.
        In the dictionary, each word of a multi-word definition is separated by
        an underscore. The primary word (the one whose part of speech is the same
        as the phrase as a whole, except for intensifiers) should be in parentheses;
        it becomes the key (if there are multiple keys, multiple entries are created).
        The value of a multi_dict is a list of all multi-word phrases a key word
        appears in (as a key) and each of these contains a 2-ple: the list all the
        words in the phrase, with the key word removed and replaced with a #,
        and the SO value for the phrase. If a word or words is modified by an
        operator (such as ?,*,+,|, or a number), the operator should be placed in
        []--all operators but | appear outside the right bracket
        ? = optional, + = one or more, * = zero or more, 2 (3, etc.) = two of these
        | = or. INT refers to a word or words in the intensifier dictionary.
        With that key (minus the last word), together with the modifier value
        ex.: c_int_dict["little"] = [[["a", "#"], -0.5]]
        :param word_string: word string
        :return: final_entries
        '''
        if "#" in word_string:  #if there is a macro, replace
            for item in self.macro_replace:
                word_string = word_string.replace(item, self.macro_replace[item])
        words = word_string.split("_")
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


    def load_dictionary(self, dct_file_path):
        '''
        Read each dictionary, and save each word into single dictionary or multi dictionary.
        A word has no "_" is a single word, a single word and the score will be saved in single dictionary.
        A word has "_" is a multi-word, it will be divided into multiple entries,
        each entry along with the score will be saved in multi dictionary.
        :param dct_file_path: the file path of a dictionary, under folder "Resources/dictionaries"
        :return: loaded single dictionary, multi dictionary
        '''
        single_dct = {}
        multi_dct = {}

        with open(dct_file_path, encoding = "ISO-8859-1") as dct_file:
            for r in dct_file:
                r = r.strip()
                if r == "": continue
                word_score = r.split()
                if len(word_score) != 2: continue
                word = word_score[0]
                score = float(word_score[1])

                if "_" not in word:    # single word
                    if self.language == "Spanish" and self.has_accent(word):
                        single_dct[self.remove_accents(word)] = score
                    single_dct[word] = score
                elif self.use_multiword_dictionaries:   # multi-word
                    entries = self.get_multiword_entries(word)
                    for entry in entries:
                        if entry[0] not in multi_dct.keys():
                            multi_dct[entry[0]] = [[entry[1], score]]
                        else:
                            multi_dct[entry[0]].append([entry[1], score])
        return single_dct, multi_dct


    def load_extra_dict(self, extra_dct_path):
        '''
        Loads the optional dictionary, which contains entries from all the
        various types of words
        :param extra_dct_path: extra dictionary path, defined in config file
        :return: loaded extra single_dict, multi_dict
        '''
        single_dict = []
        multi_dict = []

        with open(extra_dct_path, encoding = "ISO-8859-1") as extra_dct:
            for line in extra_dct:
                line = line.strip()
                if line:
                    if line == "adjectives":
                        single_dict = self.single_adj_dict
                        multi_dict = self.multi_adj_dict
                    elif line == "nouns":
                        single_dict = self.single_noun_dict
                        multi_dict = self.multi_noun_dict
                    elif line == "verbs":
                        single_dict = self.single_verb_dict
                        multi_dict = self.multi_verb_dict
                    elif line == "adverbs":
                        single_dict = self.single_adv_dict
                        multi_dict = self.multi_adv_dict
                    elif line == "intensifiers":
                        single_dict = self.single_int_dict
                        multi_dict = self.multi_adv_dict
                    elif single_dict:
                        word, score = line.split()
                        if "_" not in word:  # single word
                            single_dict[word] = float(score)
                        elif self.use_multiword_dictionaries:   # multi-word
                            entries = self.get_multiword_entries(word)
                            for entry in entries:
                                if entry[0] not in multi_dict:
                                    multi_dict[entry[0]] = [[entry[1], float(score)]]
                                else:
                                     for old_entry in multi_dict[entry[0]]: # duplicate entry
                                        if same_lists(old_entry[0], entry[1]):
                                            multi_dict[entry[0]].remove(old_entry)
                                     multi_dict[entry[0]].append([entry[1], float(score)])
        return single_dict, multi_dict


    def load_dictionaries (self):
        '''
        Load all the empty dictionaries.
        :return: None
        '''
        self.single_adj_dict, self.multi_adj_dict = self.load_dictionary(self.adj_dict_path)
        self.single_adv_dict, self.multi_adv_dict = self.load_dictionary(self.adv_dict_path)
        self.single_verb_dict, self.multi_verb_dict = self.load_dictionary(self.verb_dict_path)
        self.single_noun_dict, self.multi_noun_dict = self.load_dictionary(self.noun_dict_path)
        self.single_int_dict, self.multi_int_dict = self.load_dictionary(self.int_dict_path)
        if self.extra_dict_path != "":
            self.single_extra_dict, self.multi_extra_dict = self.load_extra_dict(self.extra_dict_path)
        if self.simple_SO:
            for s_dict in [self.single_adj_dict,self.single_adv_dict,self.single_verb_dict,self.single_noun_dict]:
                for entry in s_dict:
                    if s_dict[entry] > 0:
                        s_dict[entry] = 2
                    elif s_dict[entry] < 0:
                        s_dict[entry] = -2
            for entry in self.single_int_dict:
                if self.single_int_dict[entry] > 0:
                    self.single_int_dict[entry] = .5
                elif self.single_int_dict[entry] < 0 and self.single_int_dict[entry] > -1:
                    self.single_int_dict[entry] = -.5
                elif self.single_int_dict[entry] < -1:
                    self.single_int_dict[entry] = -2
            for c_dict in [self.multi_adj_dict,self.multi_adv_dict,self.multi_verb_dict,self.multi_noun_dict]:
                for entry in c_dict:
                    for i in range(len(c_dict[entry])):
                        if c_dict[entry][i][1] > 0:
                            c_dict[entry][i] = [c_dict[entry][i][0], 2]
                        elif c_dict[entry][i][1] < 0:
                            c_dict[entry][i] = [c_dict[entry][i][0], -2]
            for entry in self.multi_int_dict:
                 for i in range(len(self.multi_int_dict[entry])):
                     if self.multi_int_dict[entry][i][1] > 0:
                         self.multi_int_dict[entry][i] = [self.multi_int_dict[entry][i][0], .5]
                     elif self.multi_int_dict[entry][i][1] < 0 and self.multi_int_dict[entry][i][1] > -1:
                         self.multi_int_dict[entry][i] = [self.multi_int_dict[entry][i][0], -.5]
                     elif self.multi_int_dict[entry][i][1] < -1:
                         self.multi_int_dict[entry][i] = [self.multi_int_dict[entry][i][0], -2]


    def get_range_weight_lst(self):
        '''
        Reads weights_by_location from config,
        eg. {"0-0.2":"0.3", "0.8-1":"0.3"}, convert to [[0, 0.2, 0.3], [0.8, 1, 0.3]]
        :return: list of [range_left, range_right, weight]
        '''
        range_weight_lst = []
        for range, weight in self.weights_by_location.items():
            left_right = range.split("-")
            if len(left_right) != 2: continue
            left = float(left_right[0])
            right = float(left_right[1])
            if left >= 0 and left <= 1 and right >= 0 and right <= 1 and left < right:
                range_weight_lst.append([left, right, float(weight)])
        return range_weight_lst


    def fill_text_and_weights(self, input_file):
        '''
        In the preprocessed text file, each line contains word/POS_tag pair separated by 1 single space.
        self.text will append each [word, POS_tag].
        self.weights will append the weight for each [word, POS_tag],
        the weight varies depends on whether self.use_weight_by_location.
        self.boundaries will record the length of self.text for each line in the file.
        :param input_file: an input preprocessed text file
        :return: None. But self.text, self.weights, self.boundaries will be filled
        '''
        weight = 1.0

        with open(input_file) as preprocessed_file:
            for l in preprocessed_file:
                l = l.strip()
                if l == "": continue
                word_tags = l.split()
                for word_tag in word_tags:
                    self.text.append(word_tag.split('/'))
                    self.weights.append(weight)
                self.boundaries.append(len(self.text))
        if self.use_weight_by_location:
            range_weight_lst = self.get_range_weight_lst()
            for i in range(len(self.weights)):
                for range_weight in range_weight_lst:
                    if range_weight[0] <= i/len(self.weights) and range_weight[1] > i/len(self.weights):
                        self.weights[i] *= range_weight[2]


    # ---------------------------------- ENGLISH STEMMING FUNCTIONS START ---------------------------------- #

    def stem_VB(self, wordVB, type):
        '''
        Stemming English VB words.
        :param wordVB: a VB word
        :param type: VB word type.
        "Z" means VB word ends with "s"; "G" means VB word ends with "ing"; "D" or "N" means VB word ends with "ed"
        :return: stemmed VB word
        '''
        if type == "" or type == "P" or len(wordVB) < 4 or wordVB in self.single_verb_dict or wordVB in self.multi_verb_dict:
            return wordVB
        elif type == "D" or type == "N":
            if wordVB[-1] == "d":
                wordVB = wordVB[:-1]   #  loved -> love
                if wordVB not in self.single_verb_dict and wordVB not in self.multi_verb_dict:
                    if wordVB[-1] == "e":
                        wordVB = wordVB[:-1]   # enjoyed -> enjoy
                    if wordVB not in self.single_verb_dict and wordVB not in self.multi_verb_dict:
                        if wordVB[-1] == "i":
                            wordVB = wordVB[:-1] + "y"   # tried -> try
                        elif len(wordVB) > 1 and wordVB[-1] == wordVB[-2]:
                            wordVB = wordVB[:-1]   # compelled -> compel
            return wordVB
        elif type == "G":
            wordVB = wordVB[:-3]   # obeying -> obey
            if wordVB not in self.single_verb_dict and wordVB not in self.multi_verb_dict:
                if len(wordVB) > 1 and wordVB[-1] == wordVB[-2]:
                    wordVB = wordVB[:-1]   # stopping -> stop
                else:
                    wordVB = wordVB + "e"   # amusing -> amuse
            return wordVB
        elif type == "Z" and len(wordVB) > 3:
            if wordVB[-1] == "s":
                wordVB = wordVB[:-1]  # likes -> like
                if wordVB not in self.single_verb_dict and wordVB not in self.multi_verb_dict and wordVB[-1] == "e":
                    wordVB = wordVB[:-1]  # watches -> watch
                    if wordVB not in self.single_verb_dict and wordVB not in self.multi_verb_dict and wordVB[-1] == "i":
                        wordVB = wordVB[:-1] + "y"  # flies -> fly
            return wordVB


    def stem_RB_to_JJ(self, wordRB):
        '''
        Convert an English RB word to JJ. If the adjective that is the stem of an adverb so that the adverb,
        then the adverb can be added automatically to the dictionary.
        :param wordRB: an English RB word
        :return: converted JJ word
        '''
        wordJJ = wordRB
        if len(wordJJ) > 3 and wordJJ[-2:] == "ly":
            wordJJ = wordJJ[:-2]  # sharply -> sharp
            if wordJJ not in self.single_adj_dict:
                if wordJJ + "l" in self.single_adj_dict:
                    wordJJ += "l"  # full -> fully
                elif wordJJ + "le" in self.single_adj_dict:
                    wordJJ += "le"  # simply -> simple
                elif wordJJ[-1] == "i" and wordJJ[:-1] + "y" in self.single_adj_dict:
                    wordJJ = wordJJ[:-1] + "y"  # merrily -> merry
                elif len(wordJJ) > 5 and wordJJ[-2:] == "al" and wordJJ[:-2] in self.single_adj_dict:
                    wordJJ = wordJJ[:-2]  # angelic -> angelically
        return wordJJ


    def stem_NN(self, wordNN):
        '''
        Stemming English NN word.
        :param wordNN: an NN word
        :return: stemmed NN word
        '''
        if wordNN not in self.single_noun_dict and wordNN not in self.multi_noun_dict \
                and len(wordNN) > 2 and wordNN[-1] == "s":   # boys -> boy
            wordNN = wordNN[:-1]
            if wordNN not in self.single_noun_dict and wordNN not in self.multi_noun_dict and wordNN[-1] == "e": # watches -> watch
                wordNN = wordNN[:-1]
                if wordNN not in self.single_noun_dict and wordNN not in self.multi_noun_dict and wordNN[-1] == "i": # flies -> fly
                    wordNN = wordNN[:-1] + "y"
        return wordNN


    def stem_ative_adj(self, JJ):
        '''
        This function does stemming for both comparative and superlative adjectives.
        after the suffix "er" or "est" has been removed
        :param JJ: adjectives
        :return: stemmed adjectives
        '''
        if JJ not in self.single_adj_dict:
            if JJ + "e" in self.single_adj_dict:
                JJ += "e" # abler/ablest -> able
            elif JJ[:-1] in self.single_adj_dict:
                JJ = JJ[:-1] # bigger/biggest -> big
            elif JJ[-1] == "i" and JJ[:-1] + "y" in self.single_adj_dict:
                JJ = JJ[:-1] + "y" # easier/easiest -> easy
        return JJ


    def stem_comp_JJ(self, JJ):
        '''
        This function does stemming for both comparative adjectives.
        :param JJ: adjectives
        :return: stemmed adjectives
        '''
        if JJ[-2:] == "er":
            JJ = self.stem_ative_adj(JJ[:-2]) # fairer -> fair
        return JJ


    def stem_super_JJ(self, JJ):
        '''
        This function does stemming for both superative adjectives.
        :param JJ: adjectives
        :return: stemmed adjectives
        '''
        if JJ[-3:] == "est":
            JJ = self.stem_ative_adj(JJ[:-3]) # fairest -> fair
        return JJ


    # ---------------------------------- ENGLISH STEMMING FUNCTIONS END ---------------------------------- #


    # ---------------------------------- SPANISH STEMMING FUNCTIONS START ---------------------------------- #

    def stem_AQ(self, wordAQ):
        '''
        Stem Spanish AQ.
        :param wordAQ: an AQ word
        :return: stemmed AQ word
        '''
        if wordAQ not in self.single_adj_dict and len(wordAQ) > 2 and wordAQ[-1] == "s":   # buenos -> bueno
            wordAQ = wordAQ[:-1]
        if wordAQ not in self.single_adj_dict and wordAQ not in self.multi_adj_dict and len(wordAQ) > 1:
            if wordAQ[-1] == "a":    # buena -> bueno
                wordAQ = wordAQ[:-1] + "o"
            elif wordAQ[-1] == "e":   # verde -> verd
                wordAQ = wordAQ[:-1]
        return wordAQ


    def stem_RG_to_AQ(self, wordRG):
        '''
        Convert a Spanish RG word to AQ. If the adjective that is the stem of an adverb so that the adverb,
        then the adverb can be added automatically to the dictionary.
        :param wordRG: a spanish RG word
        :return: converted AQ word
        '''
        wordAQ = wordRG
        if len(wordAQ) > 6 and wordAQ[-5:] == "mente" :
            wordAQ = wordAQ[:-5]  # felizmente -> feliz
            if wordAQ not in self.single_adj_dict and wordAQ[-1] == "a":
                wordAQ = wordAQ[:-1] + "o" # nuevamente -> nuevo
        return wordAQ


    def stem_NC(self, wordNC):
        '''
        Stemming Spanish NC word.
        :param wordNC: an NC word
        :return: stemmed NC word
        '''
        if wordNC not in self.single_noun_dict and len(wordNC) > 2 and wordNC[-1] == "s":   # diplomas -> diploma
            wordNC = wordNC[:-1]
        if wordNC not in self.single_noun_dict and wordNC not in self.multi_noun_dict and len(wordNC) > 1:
            if wordNC[-1] == "a":
                wordNC = wordNC[:-1] + "o" # hermanas -> hermano
            elif wordNC[-1] == "e": # actor -> actores
                wordNC = wordNC[:-1]
        return wordNC


    def stem_super_AQ(self, AQ):
        '''
        This function removes "isima" or "isimo" from the word
        :param AQ: an AQ word
        :return: stemmed AQ word
        '''
        if AQ not in self.single_adj_dict:
            if len(AQ) > 6 and AQ[-5:] in ["ísima", "ísimo", "isima", "isimo"]:
                AQ = AQ[:-5]
                if AQ not in self.single_adj_dict:
                    if AQ[-2:] == "qu":
                        AQ = AQ[:-2] + "co"
                    elif AQ[-2] == "gu":
                        AQ = AQ[:-1] = "o"
                    else:
                        AQ += "o"
        return AQ


    # ---------------------------------- SPANISH STEMMING FUNCTIONS END ---------------------------------- #


    # ---------------------------------- GENERAL STEMMING FUNCTIONS START ---------------------------------- #

    def stem_adv_to_adj(self, word_adverb):
        '''
        Decide to call stem_RB_to_JJ(adverb) or stem_RG_to_AQ(adverb) based on the language.
        :param adverb: an adverb word
        :return: the output of the selected function
        '''
        if self.language == "English":
            return self.stem_RB_to_JJ(word_adverb)
        elif self.language == "Spanish":
            return self.stem_RG_to_AQ(word_adverb)


    def stem_noun(self, noun):
        '''
        Decide to call stem_NN(noun) or stem_NC(noun) based on the language.
        :param noun: an NN word
        :return: the output of the selected function
        '''
        if self.language == "English":
            return self.stem_NN(noun)
        elif self.language == "Spanish":
            return self.stem_NC(noun)


    def stem_super_adj(self, adj):
        '''
        Decide to call stem_super_JJ(adj) or stem_super_AQ(adj) based on the language.
        :param adj: an adj word
        :return: the output of the selected function
        '''
        if self.language == "English":
            return self.stem_super_JJ(adj)
        elif self.language == "Spanish":
            return self.stem_super_AQ(adj)


    # ---------------------------------- GENERAL STEMMING FUNCTIONS END ---------------------------------- #


    def fix_all_caps_English(self):
        '''
        For English words with all upper cases such as "AND" tend to be tagged as NNP.
        This function is used to check whether the lowercase of the words belong to any other tags,
        if so, change the tag.
        :return: None. But the word tag in self.text may be changed.
        '''
        for i in range(len(self.text)):
            if len(self.text[i]) == 2:
                word, tag = self.text[i]
                if len(word) > 2 and word.isupper() and tag == "NNP":
                    word = word.lower()
                    if word in self.single_adj_dict or word in self.multi_adj_dict:
                        self.text[i][1] = "JJ"
                    elif word in self.single_adv_dict or word in self.multi_adv_dict:
                        self.text[i][1] = "RB"
                    else:
                        ex_tag = "" # verbs need to be stemmed
                        if word[-1] == "s":
                            word = self.stem_VB(word, "Z")
                            ex_tag = "Z"
                        elif word[-3:] == "ing":
                            word = self.stem_VB(word, "G")
                            ex_tag = "G"
                        elif word[-2:] == "ed":
                            word = self.stem_VB(word, "D")
                            ex_tag = "D"
                        if word in self.single_verb_dict or word in self.multi_verb_dict:
                            self.text[i][1] = "VB" + ex_tag


    def fix_all_caps_Spanish(self):
        '''
        For Spanish words with all upper cases such as "Y" tend to be tagged as NP.
        This function is used to check whether the lowercase of the words belong to any other tags,
        if so, change the tag.
        :return: None. But the word tag in self.text may be changed.
        '''
        for i in range(len(self.text)):
            if len(self.text[i]) == 2:
                word, tag = self.text[i]
                if len(word) > 2 and word.isupper() and tag == "NP":
                    word = word.lower()
                    alt_word = self.stem_AQ(word)
                    if alt_word in self.single_adj_dict or word in self.multi_adj_dict:
                        self.text[i][1] = "AQ"
                    else:
                        alt_word = self.stem_adv_to_adj(word)
                        if alt_word in self.single_adj_dict:
                            self.text[i][1] = "RG"


    def fix_all_caps(self):
        '''
        Decide to call fix_all_caps_English() or fix_all_caps_Spanish(), based on the language.
        :return: None
        '''
        if self.language == "English":
            self.fix_all_caps_English()
        elif self.language == "Spanish":
            self.fix_all_caps_Spanish()


    def get_word (self, word_tag_pair): return word_tag_pair[0] # get word from (word, tag) pair
    def get_tag (self, word_tag_pair) : return word_tag_pair[1] # get tag from (word, tag) pair


    def find_intensifier(self, index):
        '''
        This function determines whether the given index is the last word (or, trivially, the only word)
        in an intensifier. If so, it returns a list containing, as its first element, the length of the intensifier and,
        as its second element, the modifier from the relevant intensifier dictionary
        :param index: key word index
        :return: None or [1, modifier]
        '''
        if index < 0 or index >= len(self.text) or self.get_tag(self.text[index]) == "MOD": # already modified
            return False
        if self.get_word(self.text[index]).lower() in self.multi_int_dict:  # multi intensifier
            for word_mod_pair in self.multi_int_dict[self.get_word(self.text[index]).lower()]:
                if same_lists(word_mod_pair[0][:-1],
                              map(str.lower, map(self.get_word, self.text[index - len(word_mod_pair[0]) + 1:index]))):
                    return [len(word_mod_pair[0]), word_mod_pair[1]]
        if self.get_word(self.text[index]).lower() in self.single_int_dict: # single intensifier
            modifier = self.single_int_dict[self.get_word(self.text[index]).lower()]
            if self.get_word(self.text[index]).isupper() and self.use_cap_int: # if capitalized
                 modifier *= self.capital_modifier   # increase intensification
            return [1, modifier]
        return None


    def match_multiword_f(self, index, words):
        '''
        This function recursively matches the (partial) multi-word dictionary entry (words)
        with the corresponding part of the text (from index),
        the function returns a list containing the number of words matched (or -1
        if the match failed) and the value of any intensifier found.
        :param index: key word
        :param words: multi-word dictionary entry
        :return: number of words matched (or -1 if the match failed)
        '''
        if len (words) == 0:
            return [0, 0] #done
        else:
            current = words[0]
            if not isinstance(current,list):
                current = [1, [current]] # unmodified words should be appear once
            if current[0] == "0":
                return self.match_multiword_f(index, words[1:]) #this word done
            if current[0] == "*" or current[0] == "?": # word optional - try
                temp = self.match_multiword_f(index, words[1:]) # without first
                if temp[0] != -1:
                    return temp
            if index == len(self.text):
                return [-1, 0] # reached the end of the text
            match = False
            for word_or_tag in current[1]:
                if word_or_tag.islower(): #match by word
                    match = match or self.get_word(self.text[index]).lower() == word_or_tag
                elif word_or_tag.isupper(): #match by tag
                    if word_or_tag == "INT": # if looking for a intensifiers
                        i = 1
                        while index + i < len(self.text) and self.text[index + i][0] not in self.sent_punct:
                            intensifier = self.find_intensifier(index + i - 1)
                            if intensifier and intensifier[0] == i:
                                    result = self.match_multiword_f(index + i, words[1:])
                                    if result[0] != -1:
                                        return [result[0] + i, intensifier[1]]
                            i += 1
                    else:
                        match = match or self.get_tag(self.text[index]) == word_or_tag
            if not match:
                return [-1, 0]
            else:
                if current[0] == "*":
                    temp = self.match_multiword_f(index + 1, words)
                elif current[0] == "+":
                    temp = self.match_multiword_f(index + 1, [["*", current[1]]] + words[1:])
                elif current[0] == "?":
                    temp = self.match_multiword_f(index + 1, words[1:])
                else:
                    temp = self.match_multiword_f(index + 1, [[str(int(current[0]) - 1), current[1]]] + words[1:])
                if temp[0] == -1:
                    return temp #failed
                else:
                    return [temp[0] + 1, temp[1]] #success


    # NEED TO BE MERGE WITH match_multiword_f
    def match_multiword_b(self, index, words):
        '''
        Same as match_multiword_f, but in reverse order.
        :param index: key word
        :param words: multi-word dictionary entry
        :return: number of words matched (or -1 if the match failed)
        '''
        if len (words) == 0:
            return [0, 0]
        else:
            current = words[-1]
            if not isinstance(current,list):
                current = [1, [current]]
            if current[0] == "0":
                return self.match_multiword_b(index, words[:-1])
            if current[0] == "*" or current[0] == "?":
                temp = self.match_multiword_b(index, words[:-1])
                if temp[0] != -1:
                    return temp
            if index == -1:
                return [-1,0]
            match = False
            for word_or_tag in current[1]:
                if word_or_tag.islower():
                    match = match or self.get_word(self.text[index]).lower() == word_or_tag
                elif word_or_tag.isupper():
                    if word_or_tag == "INT":
                        intensifier = self.find_intensifier(index)
                        if intensifier:
                            i = intensifier[0]
                            result = self.match_multiword_b(index  - i, words[:-1])
                            if result[0] != -1:
                                return [result[0] + i, intensifier[1]]
                    else:
                        match = match or self.get_tag(self.text[index]) == word_or_tag
            if not match:
                return [-1, 0]
            else:
                if current[0] == "*":
                    temp = self.match_multiword_b(index - 1, words)
                elif current[0] == "+":
                    temp = self.match_multiword_b(index - 1, words[:-1] + [["*", current[1]]])
                elif current[0] == "?":
                    temp = self.match_multiword_b(index - 1, words[:-1])
                else:
                    temp = self.match_multiword_b(index - 1, words[:-1] + [[str(int(current[0]) - 1), current[1]]])
                if temp[0] == -1:
                    return temp
                else:
                    return [temp[0] + 1, temp[1]]


    def find_multiword(self, index, dict_entry_list):
        '''
        This function determines whether the words surrounding the key word at
        index match one of the dictionary definitions in dict_entry_list. If so,
        it returns a list containing the SO value, the number of words in the phrase,
        that are to the left of index, the number of words to the right, and the
        value of any intensifier. Any word specifically designated in the defintion
        will have its tag changed to "MOD" so that it will not be counted twice
        :param index: key word index
        :param dict_entry_list: a dictionary starts with "multi_"
        :return: None or [SO, countback, countforward, intensifier]
        '''

        for dict_entry in dict_entry_list:
            words = dict_entry[0]
            SO = dict_entry[1]
            start = words.index("#")
            intensifier = 0
            if start < len(words) - 1:
                countforward, int_temp = self.match_multiword_f(index + 1, words[start +1:])
                if int_temp != 0:
                    intensifier = int_temp
            else:
                countforward = 0
            if start > 0:
                countback, int_temp = self.match_multiword_b(index - 1, words[:start])
                if int_temp != 0:
                    intensifier = int_temp
            else:
                countback = 0
            if countforward != -1 and countback != -1:
                for i in range(index - countback, index + countforward + 1):
                    if self.get_word(self.text[i]) in dict_entry[0]:
                        self.text[i][1] = "MOD"
                return [SO, countback, countforward, intensifier]
        return None


    def at_boundary (self, index):
        '''
        Decide whether the key word at the index is in self.boundaries or in self.punct/self.boundary_words
        :param index: word index
        :return: True or False
        '''
        if index +1 in self.boundaries:
            return True
        elif self.use_boundary_punct and self.get_word(self.text[index]) in self.punct:
            return True
        elif self.use_boundary_words and self.get_word(self.text[index]) in self.boundary_words:
            return True
        else:
            return False


    def find_negation(self, index, word_type):
        '''
        Looks backwards for a negator and returns its index if one is found and
        there is no intervening puctuation or boundary word. If restricted negation
        is used (for the given word type), the search will only continue if each
        word or its tag is in the skipped list for its type.
        :param index: key word index
        :param word_type: word type
        :return: -1 or found index
        '''
        search = True
        found = -1
        while search and not self.at_boundary(index) and index != -1:
            current = self.get_word(self.text[index]).lower()
            if current in self.negators:
                search = False
                found = index
            if self.restricted_neg[word_type] and current not in self.skipped[word_type] \
                    and self.get_tag(self.text[index]) not in self.skipped[word_type]:
                search = False
            index -= 1
        return found


    def is_blocker(self, SO, index):
        '''
        This function tests if the item at index is a blocker.
        :param SO: SO value
        :param index: key word index
        :return: True or False
        '''
        if index > -1 and index < len(self.text) and len(self.text[index]) == 2:
            modifier, tag = self.text[index]
            if tag == self.adv_tag and modifier in self.single_adv_dict and \
                            abs(self.single_adv_dict[modifier]) >= self.blocker_cutoff:
                if abs(SO + self.single_adv_dict[modifier]) < abs(SO) + abs(self.single_adv_dict[modifier]):
                    return True
            elif tag == self.adj_tag and modifier in self.single_adj_dict and \
                            abs(self.single_adj_dict[modifier]) >= self.blocker_cutoff:
                if abs(SO + self.single_adj_dict[modifier]) < abs(SO) + abs(self.single_adj_dict[modifier]):
                    return True
            elif tag[:2] == self.verb_tag and modifier in self.single_verb_dict and \
                            abs(self.single_verb_dict[modifier]) >= self.blocker_cutoff:
                if abs(SO + self.single_verb_dict[modifier]) < abs(SO) + abs(self.single_verb_dict[modifier]):
                    return True
        return False


    def find_blocker(self, SO, index, POS):
        '''
        This function tests if the item at index is of the correct type, orientation
        and strength (as determined by blocker_cutoff) to nullify a word having the
        given SO value
        :param SO: SO value
        :param index: key word index
        :param POS: POS tag
        :return: True or False
        '''
        stop = False
        while index > 0 and not stop and not self.at_boundary(index):
            if len (self.text[index-1]) == 2:
                modifier, tag = self.text[index-1]
                if self.is_blocker(SO, index-1):
                    return True
                if modifier not in self.skipped[POS] and tag[:2] not in self.skipped[POS]:
                    stop = True
            index -= 1
        return False


    def get_sent_punct (self, index):
        '''
        Get the next sentence punctuation (e.g. ?, !, or .) after the given index
        :param index: word index
        :return: True or False
        '''
        while self.text[index][0] not in self.sent_punct:
            if index == len(self.text) - 1: #if the end of the text is reached
                return "EOF"
            index += 1
        return self.get_word(self.text[index])


    def get_sent_highlighter(self, index):
        '''
        If there is a word in the sentence prior to the index but before a boundary
        marker (including a boundary marker) in the highlighter list, return it.
        :param index: key word index
        :return: None or sent_highlighter
        '''
        while index != -1 and not self.at_boundary(index):
            if self.get_word(self.text[index]).lower() in self.highlighters:
                return self.get_word(self.text[index]).lower()
            else:
                index -= 1
        return None


    def words_within_num(self, index, words_tags, num):
        '''
        Check to see if something in words_tags is within num of index (including
        index), returns true if so.
        :param index:
        :param words_tags:
        :param num:
        :return: True or False
        '''
        while num > 0:
            if self.get_word(self.text[index]) in words_tags or self.get_tag(self.text[index]) in words_tags:
                return True
            num -= 1
            index -= 1
        return False


    def is_in_imperative(self, index):
        '''
        Tries to determine if the word at index is in an imperative based on whether
        first word in the clause is a VBP (and not a question or within the
        scope of a definite determiner)
        :param index:
        :return: True or False
        '''
        if self.get_sent_punct(index) != "?" and not (self.words_within_num(index, self.definites, 1)):
            i = index
            while i > -1 and self.get_word(self.text[i]) not in self.sent_punct:
                if self.at_boundary(index):
                    return False
                i -=1
            word, tag = self.text[i+1]
            if (tag == "VBP" or tag == "VB") and word.lower() not in ["were", "was", "am"]:
                return True
        return False


    def is_in_quotes(self, index):
        '''
        Check to see if a particular word is contained within quotation marks.
        Looks to a sentence boundary on the left, and one past the sentence
        boundary on the right; an item in quotes should have an odd number of
        quotation marks in the sentence on either sides
        :param index:
        :return: True or False
        '''
        quotes_left = 0
        quotes_right = 0
        found = False
        current = ""
        i = index
        while current not in self.sent_punct and i > -1:
            current = self.get_word(self.text[i])
            if current == '"' or current == "'":
                quotes_left += 1
            i -= 1
        if operator.mod(quotes_left,2) == 1:
            current = ""
            i = index
            while not found and current not in self.sent_punct and i < len(self.text):
                current = self.get_word(self.text[i])
                if current == '"' or current == "'":
                    quotes_right += 1
                i += 1
            if  (quotes_left - quotes_right == 1) and i < len(self.text) - 1 and self.get_word(self.text[i+1]) == '"':
                quotes_right += 1
            if operator.mod(quotes_right,2) == 1:
                found = True
        return found


    def has_sent_irrealis(self, index):
        '''
        Returns true if there is a irrealis marker in the sentence and no
        punctuation or boundary word intervenes between the marker and the index
        :param index:
        :return: True or False
        '''
        if not (self.use_definite_assertion and self.words_within_num(index, self.definites, 1)):
            while index != -1 and not self.at_boundary(index):
                if self.get_word(self.text[index]).lower() in self.irrealis:
                    return True
                if self.language == "Spanish":
                    tag = self.get_tag(self.text[index])
                    if len(tag) == 4 and tag[0] == "V" and ((tag[2] == "M" and self.use_imperative)
                                                            or (tag[2] == "S" and self.use_subjunctive)
                                                            or (tag[3] == "C" and self.use_conditional)):
                        return True
                index -= 1
        return False


    def apply_other_modifiers(self, SO, index, leftedge):
        '''
        Several modifiers that apply equally to all parts of speech based on
        their context. Words in all caps, in a sentences ending with an
        exclamation mark, or with some other highlighter are intensified,
        while words appearing in a question or quotes or with some other
        irrealis marker are nullified.
        :param SO: SO Value
        :param index: key word index
        :param leftedge: left edge
        :return: [SO, output]
        '''
        output = []
        if self.use_cap_int and self.get_word(self.text[index]).isupper():
            output.append("X " + str(self.capital_modifier) +  " (CAPITALIZED)")
            SO *= self.capital_modifier
        if self.use_exclam_int and self.get_sent_punct(index) == "!":
            output.append("X " + str(self.exclam_modifier) + " (EXCLAMATION)")
            SO *= self.exclam_modifier
        if self.use_highlighters:
            highlighter = self.get_sent_highlighter(leftedge)
            if highlighter:
                output.append("X " + self.highlighters[highlighter] + " (HIGHLIGHTED)")
                SO *= float(self.highlighters[highlighter])
        if self.use_quest_mod and self.get_sent_punct(index) == "?" \
                and not (self.use_definite_assertion and self.words_within_num(leftedge, self.definites, 1)):
            output.append("X 0 (QUESTION)")
            SO = 0
        if self.language == "English" and self.use_imperative and self.is_in_imperative(leftedge):
            output.append("X 0 (IMPERATIVE)")
            SO = 0
        if self.use_quote_mod and self.is_in_quotes(index):
            output.append("X 0 (QUOTES)")
            SO = 0
        if self.use_irrealis and self.has_sent_irrealis(leftedge):
            output.append ("X 0 (IRREALIS)")
            SO = 0
        return [SO, output]


    def get_noun_SO(self, index):
        '''
        Stem the word (if necessary) 
        Look for intensifiers 
        Look for negation
         Look for negation external intensifiers (e.g. I really didn't like it)
        Apply intensification and negation, if necessary 
        Apply other types of modifiers,
        including those relevant to capitalization,  punctuation, blocking, repitition, etc.
        :param index:
        :return: noun_SO and print out the results in rich_output.json file
        '''
        NN = self.get_word(self.text[index])
        original_NN = NN
        int_modifier_negex = 0

        if NN.isupper():
            NN = NN.lower() # if all upper case, change to lower case
        if self.get_word(self.text[index - 1]) in self.sent_punct:
            NN = NN.lower() # change the word to lower case if sentence initial
        ntype = self.get_tag(self.text[index])[2:]
        NN = self.stem_noun(NN)
        if NN in self.multi_noun_dict:
            multiword_result = self.find_multiword(index, self.multi_noun_dict[NN])
        else:
            multiword_result = None
        if NN not in self.single_noun_dict and not multiword_result:
            return 0
        else:
            if multiword_result:
                (noun_SO, backcount, forwardcount, int_modifier) = multiword_result
                output = list(map(self.get_word, self.text[index - backcount:index + forwardcount + 1]))
                i = index - backcount - 1
            else:
                int_modifier = 0
                output = [original_NN]
                noun_SO = self.single_noun_dict[NN]
                i = index - 1
            if self.use_intensifiers:
                if self.language == "Spanish": # look for post-nominal adj
                    intensifier = self.find_intensifier(index +1) # look for post-nominal adj
                    if intensifier:
                        int_modifier += intensifier[1]
                        self.text[index + 1][1] = "MOD"
                        output += [self.get_word(self.text[index+1])]
                intensifier = self.find_intensifier(i)
                if intensifier:
                    int_modifier = intensifier[1]
                    for j in range (0, intensifier[0]):
                        self.text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            negation = self.find_negation(i, self.noun_tag)
            if negation != -1:
                output = list(map(self.get_word, self.text[negation:i+1])) + output
                if self.use_intensifiers:
                    int_modifier_negex = 0
                    i = negation - 1
                    if self.language == "English":
                        while self.text[i][0] in self.skipped[self.adj_tag]:
                            i -= 1
                    intensifier = self.find_intensifier(i)
                    if intensifier:
                        int_modifier_negex = intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[i][1] = "MOD" # block modifier being used twice
                            i -= 1
                        output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            output.append(str(noun_SO))
            if int_modifier != 0:
                noun_SO = noun_SO *(1+int_modifier)
                output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
            elif self.use_blocking and self.find_blocker(noun_SO, index, self.noun_tag):
                output.append("X 0 (BLOCKED)")
                noun_SO = 0
            if self.use_negation and negation != -1:
                if self.neg_negation_nullification and noun_SO < 0:
                    neg_shift = abs(noun_SO)
                elif self.polarity_switch_neg or (self.limit_shift and abs(noun_SO) * 2 < self.noun_neg_shift):
                    neg_shift = abs(noun_SO) * 2
                else:
                    neg_shift = self.noun_neg_shift
                if noun_SO > 0:
                    noun_SO -= neg_shift
                    output.append ("- "+ str(neg_shift))
                elif noun_SO < 0:
                    noun_SO += neg_shift
                    output.append ("+ "+ str(neg_shift))
                output.append("(NEGATED)")
                if self.use_intensifiers and int_modifier_negex != 0:
                    noun_SO *=(1+int_modifier_negex)
                    output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
            (noun_SO, new_out) = self.apply_other_modifiers(noun_SO, index, i)
            output += new_out
            if noun_SO != 0 and noun_SO != "":
                if int_modifier != 0 and self.int_multiplier != 1:
                    noun_SO *= self.int_multiplier
                    output.append("X " + str(self.int_multiplier) + " (INT_WEIGHT)")
                if NN not in self.word_counts[0]:
                    self.word_counts[0][NN] = 1
                else:
                    self.word_counts[0][NN] += 1
                    if negation == -1:
                        if self.use_word_counts_lower:
                            noun_SO /= self.word_counts[0][NN]
                            output.append("X 1/" + str(self.word_counts[0][NN]) + " (REPEATED)")
                        if self.use_word_counts_block:
                            noun_SO = 0
                            output.append("X 0 (REPEATED)")
            if self.noun_multiplier != 1:
                noun_SO *= self.noun_multiplier
                output.append("X " + str(self.noun_multiplier) + " (NOUN)")
            if self.output_calculations:
                for word in output:
                    self.richout.write(word + " ")
            if self.output_calculations and noun_SO == 0:
                self.richout.write("= 0\n")
            return noun_SO


    def find_VP_boundary(self, index):
        '''
        Forward search for the index immediately preceding punctuation or a boundary
        word or punctuation. Used to find intensifiers remote from the verb.
        :param index:
        :return: index
        '''
        while not self.at_boundary(index) and index < len(self.text) - 1:
            index += 1
        return index


    def get_verb_SO(self, index):
        '''
        Stem the word (if necessary) 
        Look for intensifiers 
        Look for negation
         Look for negation external intensifiers (e.g. I really didn't like it)
        Apply intensification and negation, if necessary 
        Apply other types of modifiers,
        including those relevant to capitalization,  punctuation, blocking, repitition, etc.
        :param index:
        :return: verb_SO and print out the results in rich_output.json file
        '''
        VB = self.get_word(self.text[index])
        original_VB = VB
        int_modifier_negex = 0

        if VB.isupper():
            VB = VB.lower()   # if all upper case, change to lower case
        if self.get_word(self.text[index - 1]) in self.sent_punct:
            VB = VB.lower()  # change the word to lower case if sentence initial
        if self.language == "English":
            vtype = self.get_tag(self.text[index])[2:]
            VB = self.stem_VB(VB, vtype)
        if VB in self.multi_verb_dict:
            multiword_result = self.find_multiword(index, self.multi_verb_dict[VB])
        else:
            multiword_result = None
        if VB in self.not_wanted_verb:
            return 0
        elif VB not in self.single_verb_dict and not multiword_result:
            return 0
        else:
            if multiword_result:
                (verb_SO, backcount, forwardcount, int_modifier) = multiword_result
                output = list(map(self.get_word, self.text[index - backcount:index + forwardcount + 1]))
                i = index - backcount - 1
            else:
                int_modifier = 0
                output = [original_VB]
                verb_SO = self.single_verb_dict[VB]
                i = index - 1
            if self.use_intensifiers:
                intensifier = self.find_intensifier(i)
                if intensifier:
                    int_modifier += intensifier[1]
                    for j in range (0, intensifier[0]):
                        self.text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
                if self.use_clause_final_int: # look for clause-final modifier
                    edge = self.find_VP_boundary(index)
                    intensifier = self.find_intensifier(edge - 1)
                    if intensifier:
                        int_modifier = intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[edge - 1 - j][1] = "MOD"
                        output = output + list(map(self.get_word, self.text[index + 1: edge]))
            negation = self.find_negation(i, self.verb_tag)
            if negation != -1:
                output = list(map(self.get_word, self.text[negation:i+1])) + output
                if self.use_intensifiers:
                    int_modifier_negex = 0
                    i = negation - 1
                    if self.language == "English":
                        while self.text[i][0] in self.skipped["JJ"]:
                            i -= 1
                    intensifier = self.find_intensifier(i)
                    if intensifier:
                        int_modifier_negex = intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[i][1] = "MOD" # block modifier being used twice
                            i -= 1
                        output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            output.append(str(verb_SO))
            if int_modifier != 0:
                verb_SO = verb_SO *(1+int_modifier)
                output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
            elif self.use_blocking and self.find_blocker(verb_SO, index, self.verb_tag):
                output.append("X 0 (BLOCKED)")
                verb_SO = 0
            if self.use_negation and negation != -1:
                if self.neg_negation_nullification and verb_SO < 0:
                    neg_shift = abs(verb_SO)
                elif self.polarity_switch_neg or (self.limit_shift and abs(verb_SO) * 2 < self.verb_neg_shift):
                    neg_shift = abs(verb_SO) * 2
                else:
                    neg_shift = self.verb_neg_shift
                if verb_SO > 0:
                    verb_SO -= neg_shift
                    output.append ("- "+ str(neg_shift))
                elif verb_SO < 0:
                    verb_SO += neg_shift
                    output.append("+ " + str(neg_shift))
                output.append("(NEGATED)")
                if self.use_intensifiers and int_modifier_negex != 0:
                    verb_SO *=(1+int_modifier_negex)
                    output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
            (verb_SO, new_out) = self.apply_other_modifiers(verb_SO, index, i)
            output += new_out
            if verb_SO != 0 and verb_SO != "":
                if int_modifier != 0 and self.int_multiplier != 1:
                    verb_SO *= self.int_multiplier
                    output.append("X " + str(self.int_multiplier) + " (INT_WEIGHT)")
                if VB not in self.word_counts[1]:
                    self.word_counts[1][VB] = 1
                else:
                    self.word_counts[1][VB] += 1
                    if negation == -1:
                        if self.use_word_counts_lower:
                            verb_SO /= self.word_counts[1][VB]
                            output.append("X 1/" + str(self.word_counts[1][VB]) + " (REPEATED)")
                        if self.use_word_counts_block:
                            verb_SO = 0
                            output.append("X 0 (REPEATED)")
            if self.verb_multiplier != 1:
                verb_SO *= self.verb_multiplier
                output.append("X " + str(self.verb_multiplier) + " (VERB)")
            if self.output_calculations:
                for word in output:
                    self.richout.write(word + " ")
            if self.output_calculations and verb_SO == 0:
                self.richout.write("= 0\n") # calculation is over
            return verb_SO


    def is_in_predicate(self, index):
        '''
        Backwards search for a verb of any kind. Used to determine if a comparative
        or superlative adjective is in the predicate.
        :param index:
        :return: True or False
        '''
        while not self.at_boundary(index) and index > 0:
            index -= 1
            tag = self.get_tag(self.text[index])
            if (self.language == "English" and tag[:2] == "VB" or tag in ["AUX", "AUXG"]) \
                    or (self.language == "Spanish" and tag[0] == "V"):
                return True
        return False


    def get_adj_SO(self, index):
        '''
        Stem the word (if necessary) 
        Look for intensifiers 
        Look for negation
         Look for negation external intensifiers (e.g. I really didn't like it)
        Apply intensification and negation, if necessary 
        Apply other types of modifiers,
        including those relevant to capitalization,  punctuation, blocking, repitition, etc.
        Comparative and superlative adjectives require special stemming, and are
        treated as if they have been intensified with "more" or "most". Non-
        predicative uses of this kind of adjective are often not intended to
        express sentiment, and are therefore ignored. Adjectives often have
        more than one intensifier (e.g. really very good) so the search for
        intensifiers is iterative.
        :param index:
        :return: adj_SO and print out the results in rich_output.json file
        '''
        JJ = self.get_word(self.text[index])
        original_JJ = JJ
        int_modifier = 0
        adjtype = ""
        int_modifier_negex = 0

        if JJ.isupper():
            JJ = JJ.lower()      # if all upper case, change to lower case
        if self.get_word(self.text[index - 1]) in self.sent_punct:
            JJ = JJ.lower()    # change the word to lower case if sentence initial
        if self.language == "English":
            adjtype = self.get_tag(self.text[index])[2:]
            if not self.use_comparatives and (adjtype == "R" or self.get_word(self.text[index -1]) in self.comparatives):
                return 0
            if not self.use_superlatives and (adjtype == "S" or self.get_word(self.text[index-1]) in self.superlatives
                                              or JJ in ["best","worst"]):
                return 0
            if adjtype == "R" and JJ not in self.single_adj_dict and JJ not in self.not_wanted_adj:
                JJ = self.stem_comp_JJ(JJ)
                if self.use_intensifiers:
                    int_modifier += self.single_int_dict["more"]
            elif adjtype == "S" and JJ not in self.single_adj_dict and JJ not in self.not_wanted_adj:
                JJ = self.stem_super_adj(JJ)
                if self.use_intensifiers:
                    int_modifier += 1
        elif self.language == "Spanish":
            JJ = self.stem_AQ(JJ)
            if not self.use_comparatives and (self.get_word(self.text[index -1]) in self.comparatives):
                return 0
            if not self.use_superlatives and ((self.get_word(self.text[index-1]) in self.comparatives and
                            self.get_tag(self.text[index-2]) == "DA") or (JJ in ["mejor","pésimo"]
                            and self.get_tag(self.text[index-2]) == "DA")):
                return 0
            if JJ not in self.single_adj_dict and JJ not in self.not_wanted_adj:
                new_JJ = self.stem_super_adj(JJ)
                if self.use_intensifiers and self.use_superlatives and new_JJ != JJ:
                    JJ = new_JJ
                    int_modifier += 1
        if JJ in self.multi_adj_dict:
            multiword_result = self.find_multiword(index, self.multi_adj_dict[JJ])
        else:
            multiword_result = None
        if JJ in self.not_wanted_adj:
            return 0
        elif self.language == "English" and ((adjtype == "S" or self.get_word(self.text[index-1]) in self.superlatives)
                and (not self.words_within_num(index, self.definites, 2) or not self.is_in_predicate(index))
                or ((adjtype == "R" or self.get_word(self.text[index -1]) in self.comparatives) and not self.is_in_predicate(index))):
            return 0        # superlatives must be preceded by a definite and be in the predicate, comparatives must be in the predicate
        elif JJ not in self.single_adj_dict and not multiword_result:
            return 0
        else:
            if multiword_result:
                (adj_SO, backcount, forwardcount, int_modifier) = multiword_result
                output = list(map(self.get_word, self.text[index - backcount:index + forwardcount + 1]))
                i = index - backcount - 1
            else:
                output = [original_JJ]
                adj_SO = self.single_adj_dict[JJ]
                i = index - 1
            if (self.language == "English" and self.get_tag(self.text[i]) == "DET" or self.get_word(self.text[i]) == "as") \
                    or (self.language == "Spanish" and self.get_tag(self.text[i]) == "DA" or
                                self.get_tag(self.text[i]) == "DI" or self.get_word(self.text[i]) == "tan"): # look past determiners and "as" for intensification
                i -= 1
            if self.use_intensifiers:
                intensifier = 1
                while intensifier: # keep looking for instensifiers until no more is found
                    intensifier = self.find_intensifier(i)
                    if intensifier:
                        int_modifier += intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[i][1] = "MOD" # block modifier being used twice
                            i -= 1
                        output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            negation = self.find_negation(i, self.adj_tag)
            if negation != -1:
                output = list(map(self.get_word, self.text[negation:i+1])) + output
                if self.use_intensifiers:
                    int_modifier_negex = 0
                    i = negation - 1
                    if self.language == "English":
                        while self.text[i][0] in self.skipped["JJ"]:
                            i -= 1
                    intensifier = self.find_intensifier(i)
                    if intensifier:
                        int_modifier_negex = intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[i][1] = "MOD" # block modifier being used twice
                            i -= 1
                        output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            output.append(str(adj_SO))
            if int_modifier != 0:
                adj_SO = adj_SO *(1+int_modifier)
                output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
                if ((self.language == "English" and adjtype == "R") or self.get_word(self.text[index -1]) in self.comparatives):
                    output.append("(COMPARATIVE)")
                if (self.language == "English" and (adjtype == "S" or self.get_word(self.text[index-1]) in self.superlatives)):
                    output.append("(SUPERLATIVE)")
                elif (self.language == "Spanish" and (self.get_word(self.text[index-1]) in self.comparatives
                        and self.get_tag(self.text[index-2]) == "DA")or (JJ in ["mejor","pésimo"]
                        and self.get_tag(self.text[index-2]) == "DA")):
                    output.append("(SUPERLATIVE)")
            elif self.use_blocking and self.find_blocker(adj_SO, index, self.adj_tag):
                output.append("X 0 (BLOCKED)")
                adj_SO = 0
            if self.use_negation and negation != -1:
                if self.neg_negation_nullification and adj_SO < 0:
                    neg_shift = abs(adj_SO)
                elif self.polarity_switch_neg or (self.limit_shift and abs(adj_SO) * 2 < self.adj_neg_shift):
                    neg_shift = abs(adj_SO) * 2
                else:
                    neg_shift = self.adj_neg_shift
                if adj_SO > 0:
                    adj_SO -= neg_shift
                    output.append ("- "+ str(neg_shift))
                elif adj_SO < 0:
                    adj_SO += neg_shift
                    output.append ("+ "+ str(neg_shift))
                output.append("(NEGATED)")
                if self.use_intensifiers and int_modifier_negex != 0:
                    adj_SO *=(1+int_modifier_negex)
                    output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
            (adj_SO, new_out) = self.apply_other_modifiers(adj_SO, index, i)
            output += new_out
            if int_modifier != 0 and self.int_multiplier != 1:
                adj_SO *= self.int_multiplier
                output.append("X " + str(self.int_multiplier) + " (INT_WEIGHT)")
            if JJ not in self.word_counts[2]:
                self.word_counts[2][JJ] = 1
            else:
                self.word_counts[2][JJ] += 1
                if negation == -1:
                    if self.use_word_counts_lower:
                        adj_SO /= self.word_counts[2][JJ]
                        output.append("X 1/" + str(self.word_counts[2][JJ]) + " (REPEATED)")
                    if self.use_word_counts_block:
                        adj_SO = 0
                        output.append("X 0 (REPEATED)")
            if self.adj_multiplier != 1:
                adj_SO *= self.adj_multiplier
                output.append("X " + str(self.adj_multiplier) + " (ADJECTIVE)")
            if self.output_calculations:
                for word in output:
                    self.richout.write(word + " ")
            if self.output_calculations and adj_SO == 0:
                self.richout.write("= 0\n") # calculation is over
            return adj_SO


    def get_adv_SO(self, index):
        '''
        Stem the word (if necessary) 
        Look for intensifiers 
        Look for negation
         Look for negation external intensifiers (e.g. I really didn't like it)
        Apply intensification and negation, if necessary 
        Apply other types of modifiers,
        including those relevant to capitalization,  punctuation, blocking, repitition, etc.
        There are two special things to note about dealing with adverbs: one is that
        their SO value can be derived automatically from the lemma in the
        adjective dictionary. The other is the special handling of "too", which
        is counted only when it does not appear next to punctuation (which rules out
        most cases of "too" in the sense of "also").
        :param index:
        :return: [adv_SO, full_output]
        '''
        RB = self.get_word(self.text[index])
        original_RB = RB
        int_modifier_negex = 0

        if RB.isupper():
            RB = RB.lower()   # if all upper case, change to lower case
        if self.get_word(self.text[index - 1]) in self.sent_punct:
            RB = RB.lower() # change the word to lower case if sentence initial
        if self.adv_learning and RB not in self.single_adv_dict and RB not in self.not_wanted_adv:
            JJ = self.stem_adv_to_adj(RB) # stem the adverb to its corresponding adj
            if JJ in self.single_adj_dict:
                self.single_adv_dict[RB] = self.single_adj_dict[JJ] # take its SO value
                self.new_adv_dict[RB] = self.single_adj_dict[JJ]
        if RB in self.multi_adv_dict:
            multiword_result = self.find_multiword(index, self.multi_adv_dict[RB])
        else:
            multiword_result = None
        if RB in self.not_wanted_adv or (self.language == "English" and (RB == "too" and index < len(self.text) - 1
                    and self.get_word(self.text[index + 1]) in self.punct) or (RB == "well" and index < len(self.text) - 1
                                                                  and self.get_word(self.text[index + 1]) == ",")):
            return [0,""]                    # do not count too next to punctuation
        elif RB not in self.single_adv_dict and not multiword_result:
            return [0,""]
        else:
            if multiword_result:
                (adv_SO, backcount, forwardcount, int_modifier) = multiword_result
                output = list(map(self.get_word, self.text[index - backcount:index + forwardcount + 1]))
                i = index - backcount - 1
            else:
                int_modifier = 0
                output = [original_RB]
                adv_SO = self.single_adv_dict[RB]
                i = index - 1
            if (self.language == "English" and self.get_word(self.text[i]) == "as") or \
            (self.language == "Spanish" and self.get_word(self.text[i]) == "tan"): # look past "as" for intensification
                i -= 1
            if self.use_intensifiers:
                intensifier = self.find_intensifier(i)
                if intensifier:
                    int_modifier += intensifier[1]
                    for j in range (0, intensifier[0]):
                        self.text[i][1] = "MOD" # block modifier being used twice
                        i -= 1
                    output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1])) + output
            negation = self.find_negation(i, self.adv_tag)
            if negation != -1:
                output = list(map(self.get_word, self.text[negation:i+1])) + output
                if self.use_intensifiers:
                    int_modifier_negex = 0
                    i = negation - 1
                    if self.language == "English":
                        while self.text[i][0] in self.skipped["JJ"]:
                            i -= 1
                    intensifier = self.find_intensifier(i)
                    if intensifier:
                        int_modifier_negex = intensifier[1]
                        for j in range (0, intensifier[0]):
                            self.text[i][1] = "MOD" # block modifier being used twice
                            i -= 1
                        output = list(map(self.get_word, self.text[i + 1:i + intensifier[0] + 1]))
            output.append(str(adv_SO))
            if int_modifier != 0:
                adv_SO = adv_SO *(1+int_modifier)
                output.append("X " + str(1 + int_modifier) + " (INTENSIFIED)")
            elif self.use_blocking and self.find_blocker(adv_SO, index, self.adv_tag):
                output.append("X 0 (BLOCKED)")
                adv_SO = 0
            if self.use_negation and negation != -1:
                if self.neg_negation_nullification and adv_SO < 0:
                    neg_shift = abs(adv_SO)
                elif self.polarity_switch_neg or (self.limit_shift and abs(adv_SO) * 2 < self.adv_neg_shift):
                    neg_shift = abs(adv_SO) * 2
                else:
                    neg_shift = self.adv_neg_shift
                if adv_SO > 0:
                    adv_SO -= neg_shift
                    output.append ("- "+ str(neg_shift))
                elif adv_SO < 0:
                    adv_SO += neg_shift
                    output.append ("+ "+ str(neg_shift))
                output.append("(NEGATED)")
                if self.use_intensifiers and int_modifier_negex != 0:
                    adv_SO *=(1+int_modifier_negex)
                    output.append("X " + str(1 + int_modifier_negex) + " (INTENSIFIED)")
            (adv_SO, new_out) = self.apply_other_modifiers(adv_SO, index, i)
            output += new_out
            if adv_SO != 0:
                if int_modifier != 0 and self.int_multiplier != 1:
                    adv_SO *= self.int_multiplier
                    output.append("X " + str(self.int_multiplier) + " (INT_WEIGHT)")
                if RB not in self.word_counts[3]:
                    self.word_counts[3][RB] = 1
                else:
                    self.word_counts[3][RB] += 1
                    if negation == -1:
                        if self.use_word_counts_lower:
                            adv_SO /= self.word_counts[3][RB]
                            output.append("X 1/" + str(self.word_counts[3][RB]) + " (REPEATED)")
                        if self.use_word_counts_block:
                            adv_SO = 0
                            output.append("X 0 (REPEATED)")
            if self.adv_multiplier != 1:
                adv_SO *= self.adv_multiplier
                output.append("X " + str(self.adv_multiplier) + " (ADVERB)")
            full_output = ""
            if self.output_calculations:
                for word in output:
                    full_output += word + " "
            if self.output_calculations and adv_SO == 0:
                full_output += ("= 0\n") # calucation is over
            return [adv_SO, full_output]


    def sum_word_counts (self, word_count_dict):
        '''
        Gives the total count in a word count dictionary.
        :param word_count_dict: word count dictionary
        :return: word count
        '''
        count = 0
        for word in word_count_dict:
            count+= word_count_dict[word]
        return count


    def apply_weights(self, word_SO, index):
        '''
        This is the last step in the calculation, external weights and negation weights are applied
        :param word_SO:
        :param index:
        :return: word_SO with applied external weights and negation weights
        '''
        if self.use_heavy_negation and word_SO < 0: # weighing of negative SO
            word_SO *= self.neg_multiplier          # items
            if self.output_calculations:
                self.richout.write(" X " + str(self.neg_multiplier) + " (NEGATIVE)")
        word_SO *= self.weights[index] # apply weights
        if self.weights[index] != 1:
            if self.output_calculations:
                self.richout.write (" X " + str(self.weights[index]) + " (WEIGHTED)")
        if self.output_calculations:
            self.richout.write (" = " + str(word_SO) + "\n")
        return word_SO


    def get_sentence_num(self, index):
        '''
        Returns the sentence number, based on the orignal text newlines
        :param index:
        :return:
        '''
        while index not in self.boundaries:
            index += 1
        return self.boundaries.index(index)


    def get_richout_f(self):
        words_SO = 0
        word_count = 0
        word_SO = 0

        for index in range(len(self.text)):
            if len(self.text[index]) == 2:
                word, tag = self.text[index]
                if tag[:2] == self.noun_tag:
                    if self.output_calculations:
                        self.richout.write("Nouns:\n-----\n")
                    word_SO = self.get_noun_SO(index)
                    word_count = self.sum_word_counts(self.word_counts[0])
                elif tag[:2] == self.verb_tag:
                    if self.output_calculations:
                        self.richout.write("Verbs:\n-----\n")
                    word_SO = self.get_verb_SO(index)
                    word_count = self.sum_word_counts(self.word_counts[1])
                elif tag[:2] == self.adj_tag:
                    if self.output_calculations:
                        self.richout.write("Adjectives:\n-----\n")
                    word_SO = self.get_adj_SO(index)
                    word_count = self.sum_word_counts(self.word_counts[2])

                if word_SO != 0 and word_SO != "":
                    word_SO = self.apply_weights(word_SO, index)
                    words_SO += word_SO
                if self.output_sentences and word_SO != "":
                    sentence_no = self.get_sentence_num(index)
                    if sentence_no not in self.sentence_SO:
                        self.sentence_SO[sentence_no] = word_SO
                    else:
                        self.sentence_SO[sentence_no] += word_SO
        if word_count > 0:
            if self.output_calculations:
                self.richout.write("-----\nAverage SO: " + str(words_SO/word_count) + "\n-----\n")
            self.text_SO += words_SO
            self.SO_counter += word_count
        else:
            if self.output_calculations:
                self.richout.write("-----\nAverage SO: 0\n-----\n")


    def apply_weights_adv (self, word_SO, index, output):
        '''
        This is the last step in the calculation, external weights and negation
        weights are applied to adv words.
        :param word_SO:
        :param index:
        :param output: output from get_adv_SO(index)
        :return: [word_SO, output] which applied external weights and negation weights
        '''
        if self.use_heavy_negation and word_SO < 0: # weighing of negative SO
            word_SO *= self.neg_multiplier          # items
            if self.output_calculations:
                output += " X " + str(self.neg_multiplier) + " (NEGATIVE)"
        word_SO *= self.weights[index] # apply weights
        if self.weights[index] != 1:
            if self.output_calculations:
                output += " X " + str(self.weights[index]) + " (WEIGHTED)"
        if self.output_calculations:
            output += (" = " + str(word_SO) + "\n")
        return [word_SO, output]


    def get_richout_b(self):
        words_SO = 0
        word_count = 0
        word_outputs = []

        if self.output_calculations:
            self.richout.write("Adverbs:\n-----\n")
        for index in range(len(self.text) - 1, -1, -1): # backwards iteration, since
            if len(self.text[index]) == 2:
                word, tag = self.text[index]             # adverbs modify adverbs
                if tag[:2] == self.adv_tag:
                    word_SO,output = self.get_adv_SO(index)
                    word_count = self.sum_word_counts(self.word_counts[3])
                    if word_SO != 0 and word_SO != "":
                        word_SO,output = self.apply_weights_adv(word_SO, index, output)
                        words_SO += word_SO
                        word_outputs.insert(0,output)
                    if self.output_sentences and word_SO != "":
                        sentence_no = self.get_sentence_num(index)
                        if sentence_no not in self.sentence_SO:
                            self.sentence_SO[sentence_no] = word_SO
                        else:
                            self.sentence_SO[sentence_no] += word_SO
        for output in word_outputs:
            self.richout.write(output)
        if word_count > 0:
            if self.output_calculations:
                self.richout.write("-----\nAverage SO: " + str(words_SO/word_count) + "\n-----\n")
            self.text_SO += words_SO
            self.SO_counter += word_count
        else:
            if self.output_calculations:
                self.richout.write("-----\nAverage SO: 0\n-----\n")


    def generate_rich_output(self):
        if self.fix_cap_tags:
            self.fix_all_caps()
        if self.use_nouns:
            self.get_richout_f()
        if self.use_verbs:
            self.get_richout_f()
        if self.use_adjectives:
            self.get_richout_f()
        if self.use_adverbs:
            self.get_richout_b()


def main():
    args = get_command_arguments()
    print(args)  # TEST
    config_file = args.config
    word_lists_file = args.word_lists
    cutoff = args.cutoff
    input_path = args.input
    output_folder = args.output

    file_sentiment = os.path.abspath(output_folder) + "/file_sentiment.csv"
    # richout = os.path.abspath(output_folder) + "/rich_output.json"
    richout = os.path.abspath(output_folder) + "/rich_output.txt"

    config = load_json(config_file)
    word_lists = load_json(word_lists_file)


    if os.path.isfile(input_path):   # your input data is a single file
        sc = SentimentCalculator(config, word_lists, richout, file_sentiment)
        sc.load_dictionaries()
        sc.fill_text_and_weights(input_path)
        sc.generate_rich_output()
    elif os.path.isdir(input_path):  # your input data is a folder
        for file_name in os.listdir(input_path):
            file_path = os.path.abspath(input_path) + "/" + file_name
            if os.path.isfile(file_path) == False: continue

            sc = SentimentCalculator(config, word_lists, richout, file_sentiment)
            sc.load_dictionaries()
            sc.fill_text_and_weights(file_path)
            sc.generate_rich_output()
    else:
        print("Your input data" + os.path.abspath(input_path) + "is neither a file nor a folder.")

if __name__ == "__main__":
    main()