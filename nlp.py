import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

print "\nLoading..."

debug = False
debug_commands = {"show": "Displays important internal information.\nSpecify the information after the command.\nDisplayable Information:\nkb: Displays the program's knowledgebase.\ndebug: Displays the status of the debug mode.",
                  "debug": "Enables/disables debug mode. Debug mode displays valuable debug information during runtime.",
                  "help": "Shows information about all or specific commands. To show information about a command, write 'help command_name'"}

print "\nCreating knowledgebase..."

# input text
sample_text = """The  Eiffel Tower is located in Paris and is 300 meters tall. The Washington Monument is located in 
Washington D.C. and is 169 meters tall. The Parthenon is located in Athens and is 14 meters tall."""

# tokenize input by sentences
sentences = sent_tokenize(sample_text)

# tokenize input sentences by words

tokenized_sentences = []
for sentence in sentences:
    tokenized_sentences.append(word_tokenize(sentence))

# filter out stopwords from input
stop_words = set(stopwords.words('english'))
filtered_sentences = []
for sentence in tokenized_sentences:
    filtered_sentence = []
    for word in sentence:
        if word not in stop_words:
            filtered_sentence.append(word)
    filtered_sentences.append(filtered_sentence)

# lemmatize input sentences
lemmatizer = WordNetLemmatizer()
lemmatized_sentences = []
for sentence in filtered_sentences:
    lemmatized_sentence = []
    for word in sentence:
        if word not in stop_words:
            lemmatized_sentence.append(lemmatizer.lemmatize(word))
    lemmatized_sentences.append(lemmatized_sentence)

tagged_sentences = []
for sentence in lemmatized_sentences:
    tagged_sentences.append(nltk.pos_tag(sentence))

# chunk names of monuments and locations that may be of 2 or more words
chunkGram = r"""Chunk: {<NNP>+}"""
chunkParser = nltk.RegexpParser(chunkGram)
chunked_sentences = []
for sentence in tagged_sentences:
    chunked_sentences.append(chunkParser.parse(sentence))

# create knowledgebase
knowledgebase = dict()
for sentence in chunked_sentences:
    chunks_found = 0
    numbers_found = 0
    name = ''
    height = ''
    location = ''
    for i in range(len(sentence)):
        if hasattr(sentence[i], "label"):
            if sentence[i].label() == "Chunk":
                if chunks_found > 0:
                    for word in sentence[i]:
                        location += word[0] + " "
                    location = location.strip()
                else:
                    for word in sentence[i]:
                        name += word[0] + " "
                    name = name.strip()
            chunks_found += 1
        else:
            if sentence[i][1] == "CD":
                height = float(sentence[i][0])
                numbers_found += 1
    if chunks_found == 2 and numbers_found == 1:
        knowledgebase[name.lower()] = {"name": name, "height": height, "location": location}

if len(knowledgebase) in range(1, len(sentences) + 1):
    stop_words.remove("where")
    print "\n"
    # retrieving knowledge form the knowledgebase with natural language questions
    while True:
        # read question, turn to lower case and tokenize by words
        query = ""
        while query == "":
            query = raw_input("Please type in your question:\n").strip()
        query = query.lower()
        if query == "exit":
            break
        query = word_tokenize(query)

        # debug command control
        if query[0] in debug_commands and len(query) < 3:
            if query[0] == "show":
                if len(query) == 2:
                    if query[1] == "kb":
                        print "\nKnowledgebase:\n", knowledgebase, "\n"
                    elif query[1] == "debug":
                        print "\nDebug mode:", debug, "\n"
                    else:
                        print "\nArgument not found! Type 'help show' to view all valid arguments.\n"
                else:
                    print "\nNow argument passed!\n"
            elif query[0] == "debug":
                if len(query) == 1:
                    debug = not debug
                    print "\nDebug mode:", debug, "\n"
                else:
                    print "\nInvalid argument! The 'debug' command takes no arguments!\n"
            elif query[0] == 'help':
                if len(query) == 1:
                    for key, value in debug_commands.items():
                        print "\n", key, ":\n", value, "\n"
                elif query[1] in debug_commands:
                    print "\n", query[1], ":\n", debug_commands[query[1]], "\n"
                else:
                    print "\nCommand passed as argument not found! Type 'help' to view all valid commands\n"
            continue

        if debug:
            print "\nTokenized Query:\n", query, "\n"

        # chunking of monument names
        chunked_query = []
        i = 0
        while i < len(query):
            j = 0
            check_string = query[i]
            while check_string not in knowledgebase:
                j += 1
                if i + j < len(query):
                    check_string += " " + query[i + j]
                else:
                    break
            if check_string in knowledgebase:
                chunked_query.append(check_string)
                i += j + 1
            else:
                chunked_query.append(query[i])
                i += 1

        if debug:
            print "\nChunked Query:\n", chunked_query, "\n"

        # filter out stopwords
        filtered_query = []
        for word in chunked_query:
            if word not in stop_words:
                filtered_query.append(word)

        if debug:
            print "\nStopword Filtered Query:\n", filtered_query, "\n"

        # correct common errors in the keywords of the question
        for i in range(len(filtered_query)):
            if filtered_query[i] in ["bigger", "higher", "talle", "bigger", "highe", "bige", "biger", "tale", "taler",
            "biggr", "bigr", "highr", "tallr", "talr"]:
                filtered_query[i] = "taller"
            elif filtered_query[i] in ["lower", "smaller", "lowe", "smalle", "smaler", "smale", "shorte", "sorter", "sorte",
            "smallr", "smalr", "lowr", "shortr", "sortr"]:
                filtered_query[i] = "shorter"
            elif filtered_query[i] in ["tal", "high", "height", "size", "heigth", "big"]:
                filtered_query[i] = "tall"
            elif filtered_query[i] == "wher":
                filtered_query[i] = "where"

        if debug:
            print "\nCorrected Query:\n", filtered_query, "\n"

        # answer the question
        try:
            if "taller" in filtered_query:
                monument1 = filtered_query[filtered_query.index("taller") - 1]
                monument2 = filtered_query[filtered_query.index("taller") + 1]
                if monument1 in knowledgebase and monument2 in knowledgebase:
                    if knowledgebase[monument1]["height"] > knowledgebase[monument2]["height"]:
                        print "\nYes.\n"
                    else:
                        print "\nNo.\n"
                else:
                    print "\nI can't understand this question.\n"
            elif "shorter" in filtered_query:
                monument1 = filtered_query[filtered_query.index("shorter") - 1]
                monument2 = filtered_query[filtered_query.index("shorter") + 1]
                if monument1 in knowledgebase and monument2 in knowledgebase:
                    if knowledgebase[monument1]["height"] < knowledgebase[monument2]["height"]:
                        print "\nYes.\n"
                    else:
                        print "\nNo.\n"
                else:
                    print "\nI do not understand this question.\n"
            elif "tall" in filtered_query:
                monument = filtered_query[filtered_query.index("tall") + 1]
                if monument in knowledgebase:
                    print "\nThe", knowledgebase[monument]["name"], "is", knowledgebase[monument]["height"], "meters tall.\n"
                else:
                    print "\nI do not understand this question.\n"
            elif "where" in filtered_query:
                monument = filtered_query[filtered_query.index("where") + 1]
                if monument in knowledgebase:
                    print "\nThe", knowledgebase[monument]["name"], "is located in", knowledgebase[monument]["location"] + ".\n"
                else:
                    print "\nI do not understand this question.\n"
            else:
                print "\nI do not understand this question.\n"
        except():
            print "\nI do not understand this question.\n"

    print "\nGoodbye!\n"
else:
    print "\nError! Invalid input syntax! Terminating program...\n"
