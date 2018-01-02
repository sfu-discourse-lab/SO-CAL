# SO-CAL

SO-CAL is the Semantic Orientation CALculator, a tool to extract sentiment from text. Sentiment is defined as positive or negative opinion.

SO-CAL has a long history of development, starting roughly in 2004. See below for improvements in this version. The best description of SO-CAL is in this paper:

Taboada, Maite, Julian Brooke, Milan Tofiloski, Kimberly Voll and Manfred Stede (2011) [Lexicon-Based Methods for Sentiment Analysis][3]. Computational Linguistics 37 (2): 267-307. 

Other papers about SO-CAL development:

Taboada, M., J. Brooke and M. Stede (2009) [Genre-Based Paragraph Classification for Sentiment Analysis][4]. In Proceedings of 10th Annual SIGDIAL Conference on Discourse and Dialogue. London, UK. September 2009. pp. 62-70.

Brooke, J., M. Tofiloski and M. Taboada (2009) [Cross-Linguistic Sentiment Analysis: From English to Spanish][5]. In Proceedings of RANLP 2009, Recent Advances in Natural Language Processing. Borovets, Bulgaria. September 2009. pp. 50-54. -- Poster

Voll, K. and M. Taboada (2007) [Not All Words are Created Equal: Extracting Semantic Orientation as a Function of Adjective Relevance][6]. In Proceedings of the 20th Australian Joint Conference on Artificial Intelligence. Gold Coast, Australia. December 2007. pp. 337-346.

Taboada, M., C. Anthony and K. Voll (2006) [Methods for Creating Semantic Orientation Dictionaries][7]. Proceedings of 5th International Conference on Language Resources and Evaluation (LREC). Genoa, Italy. May 2006. pp. 427-432.

Taboada, M. and J. Grieve (2004) [Analyzing Appraisal Automatically][8] American Association for Artificial Intelligence Spring Symposium on Exploring Attitude and Affect in Text. Stanford. March 2004. AAAI Technical Report SS-04-07. (pp.158-161). Download poster (pdf).


# New version of SO-CAL

The code is written in <b>Python 3.5</b> so please make sure to work with this version of Python.

* Part 1 - Install Stanford CoreNLP
* Part 2 - Data Preprocessing
* Part 3 - Sentiment Calculator

*****************************************************************************

<b>PART 1 - INSTALL STANFORD CORENLP</b>

1. Download [Newest Stanford CoreNLP][1]
2. Unzip your downloaded .zip file. For example, `unzip stanford-corenlp-full-2016-10-31.zip`
3. `cd stanford-corenlp-full-2016-10-31`
4. `java -mx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000`, this will start the server.
timeout is in milliseconds, here we set it to 10 sec above. <b>You should increase it if you pass huge blobs to the server.</b>
5. `pip3 install pycorenlp`
6. [For an example code to test your setup][2]


*****************************************************************************

<b>PART 2 - DATA PREPROCESSING</b>

* It reads a raw text file or folder and generate a folder with tagged file(s). Each token in a output file is tagged with POS tag
* We are using Stanford CoreNLP for the tokenization, sentence spliting and POS tagging
* The code file is `preprocess.py` under folder `Source_Code/text_preprocessing`
* In order to run the code, you may need to change the settings in `run_text_preprocessing.sh` by defining the paths of raw text input, preprocessed data output and which stanford annotations you need. Then in your terminal, type `cd source_code` and type `sh run_text_preprocessing.sh`
* Our sample input can be found in folder `Sample/input/Raw_Text/BOOKS`
  * If your raw text input is a <b>folder</b>, in `run_text_preprocessing.sh`, the command line should be `python3.5 text_preprocessing/preprocess.py  -i '../Sample/input/Raw_Text/BOOKS/' -o '../Sample/output/Preprocessed_Output/BOOKS/' -a 'tokenize,ssplit,pos'`
  * If your raw text input is a </b>file</b>, in `run_text_preprocessing.sh`, the command line should be `python3.5 text_preprocessing/preprocess.py  -i '../Sample/input/Raw_Text/BOOKS/no1.txt' -o '../Sample/output/Preprocessed_Output/BOOKS/' -a 'tokenize,ssplit,pos'`
  * <b>NOTE</b>: In order to make the output more organized, the output will be a folder no matter what your input is
* Sample output can be found in folder `Sample/output/Preprocessed_Output/BOOKS`


*****************************************************************************

<b>PART 3 - SENTIMENT CALCULATOR</b>

* Major features of Sentiment Calculator
  * Read 1 single text file or a folder of text files, calculate sentiment for each file (positive, negative or neutral)
  * Generate detailed lists of word sentiment as well as average Sentiment Orientation (SO) score, total SO score for each file
    * The word types here are Noun, Verb, Adjectives and Adverb
  * If your input data has sentiment classification labels (positive or negative), we call the labels `gold data` here, it will generate sentiment prediction accuracy
  
* Code Structure
  * All the source code for sentiment calculator is located under folder `Source_Code/sentiment_calculator`
  * `SO_Calc.py`
    * It process 1 file each time and does all the sentiment calculation
    * For each file, it adds the basic sentiment output, our sample is `output.txt` under folder `Sample/output/SO_CAL_Output/BOOKS`. For each file, there are file name and SO score
    * For each file, it also adds detailed sentiment output for each file, our sample is `richout.txt` under folder `Sample/output/SO_CAL_Output/BOOKS`. For each file, there are total text length; word sentiment & SO score for each Noun, Verb, Adjective and Adverb; Average SO score for Nouns, Verbs, Adjectives and Adverbs; and Total SO score for the file
  * `SO_Run.py`
    * It can read 1 single text file or a folder that contains text files. For each file, it calls `SO_Calc.py`
    * The input text file has to be preprocessed text. Check our sample preprocessed files under folder `Sample/output/Preprocessed_Output/BOOKS`. To preprocess your raw text files, check our <b>PART 2 - DATA PREPROCESSING</b> above
    * After `SO_Calc.py` has generated the output for all the files, `SO_Run.py` reads `output.txt` and `richout.txt`, in order to generate formatted `file_sentiment.csv` and `rich_output.json`
    * `file_sentiment.csv` is generated from `output.txt`, our sample is under folder `Sample/output/SO_CAL_Output/BOOKS`. For each file, it has file name, sentiment and SO score
    * `rich_output.json` is generated from `richout.txt`, our sample in under folder `Sample/output/SO_CAL_Output/BOOKS`. It contains the same data in the same order as `richout.txt`, but in JSON format which is easier to read and load data
    * If there is gold data, `prediction_accuracy.txt` generates the sentiment prediction accuracy, our sample can be found under folder `Sample/output/SO_CAL_Output/BOOKS`
    * There are 2 ways to create gold data:
      * Start your input text file name with 'yes' or 'no'. For example, `yes7.txt`, `no7.txt`. When the code is running, a gold file will be generated automatically under folder `Resources/gold`
      * Create a gold file with file name and sentiment label, check our sample in 'gold.txt' under folder `Sample/gold`. With a gold file, you don't need to worry about naming the text files, but the file names have to match each input text file
    * Without any gold data is also fine, you just won't generate `prediction_accuracy.txt` file, won't influence other output

* How to Run the Code
  * In your terminal, under the folder of this project
    * Type `cd Source_Code`
    * Then type `sh run_sentiment_calculator.sh`
    * If you want to change the setteings of the command line input, go to `run_sentiment_calculator.sh` under folder `Source_Code`, and edit the command line
  * Command line arguments:
    * Use `-i` to indicate your input
    * Use `-o` to indicate your output folder. <b>The output has to be a folder</b>, so that all the output files can be generated there
    * Use `-c` to indicate your config files. Our config sample `en_SO_Calc.ini` for English, `Spa_SO_Calc.ini` for Spanish can be found under folder `Resources/config_files`
    * Use `-cf` to indicate your cutoff value
    * Use `-g` to indicate your gold file path. This argument is <b>optional</b>
    * `-i`, `-o`, `-c`, `-cf` are required, and we all have default values for them in this project
  * Sample Command line
    * Command line with default values: `Python3.5 sentiment_calculator/SO_Run.py`
    * Command line with full settings: `Python3.5 sentiment_calculator/SO_Run.py -i "../Sample/output/Preprocessed_Output/BOOKS" -o "../Sample/output/SO_CAL_Output/BOOKS" -c "../Resources/config_files/en_SO_Calc.ini" -cf 0.0 -g "../Sample/gold/gold.txt"`


[1]:http://stanfordnlp.github.io/CoreNLP/
[2]:http://stackoverflow.com/questions/32879532/stanford-nlp-for-python
[3]:http://www.mitpressjournals.org/doi/abs/10.1162/COLI_a_00049
[4]:http://www.sfu.ca/~mtaboada/docs/publications/Taboada_Brooke_Stede_SIGDIAL_2009.pdf
[5]:http://www.sfu.ca/~mtaboada/docs/publications/Brooke_et_al_RANLP_2009.pdf
[6]:http://www.sfu.ca/~mtaboada/docs/publications/Voll_Taboada_AusAI.pdf
[7]:http://www.sfu.ca/~mtaboada/docs/publications/Taboada_et_al_LREC_2006.pdf
[8]:http://www.sfu.ca/~mtaboada/docs/publications/TaboadaGrieveAppraisal.pdf
