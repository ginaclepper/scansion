import cmudict
import os
import string
import re
import nltk
# nltk.download('all')
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize
import copy

# Vowels for interpreting unknown words in new_dict:
vowels = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]

# Filepath information:
path = "C:\\Users\\ginac\\Documents\\PoetryGeneration\\python-cmudict\\"
poem_path = os.path.join(path, "poems\\")

to_lookup_filename = "to_lookup.txt"
new_dict_filename = "new_dict.txt"

# For stripping punctuation from poems and replacing with ''
translator = str.maketrans('', '', string.punctuation)

# Conjunctions, determiners, and pronouns
dets_etc = ["for", "and", "nor", "but", "or", "yet", "so", "the", "a", "an", "this", "that", "these", "those", "my", "mine", "your", "yours", "his", "her", "hers", "its", "our", "ours", "their", "theirs", "all", "many", "much", "some", "enough", "several", "few", "any", "no", "none", "either", "neither", "both", "half", "each", "every", "i", "you", "he", "she", "it", "we", "they", "me", "him", "us", "them", "such", "thou", "thee", "ye", "thy", "thine", "who", "whom", "what", "which", "whose", "after", "although", "as", "because", "before", "if", "lest", "once", "since", "than", "that", "though", "till", "unless", "until", "when", "whenever", "where", "wherever", "while"]
# Sources:
# https://www.ef.com/wwen/english-resources/english-grammar/determiners/
# https://www.englishclub.com/grammar/determiners-vs-pronouns.htm
# https://grammar.yourdictionary.com/parts-of-speech/nouns/what/what-is-a-determiner.html
# https://www.englishclub.com/vocabulary/pronouns-type.php
# https://webapps.towson.edu/ows/conjunctions.htm

# UNUSED:
# Parts of speech acronyms from Penn Treebank Project, used by NLTK
# nouns = ["NN", "NNS", "NNP", "NNPS"]

# Return self-made dictionary (new_dict) of words looked up using LOGIOS
# Assign stress 2 to each vowel
def get_new_dict():
    new_dict = {}
    with open(os.path.join(path, new_dict_filename),'r') as file: 
        for l, line in enumerate(file):
            word = line.split()[0].lower() # first element: word
            value = [[]]
            for phon in line.split()[1:]: # subsequent elements: phonemes
                if phon in vowels: # append a 2 (unknown stress)
                    value[0].append(phon + "2")
                else:
                    value[0].append(phon)
            new_dict[word] = value # add to new_dict
    return new_dict

# Read in a file and return 2D array (poem) with rows=lines and cols=words
def get_poem(filename):
    poem = []
    with open(os.path.join(poem_path, filename),'r') as file: 
        for l, line in enumerate(file):
            poem.append([]) # creates new row
            for word in line.split():
                new_word = word.translate(translator).lower()
                if new_word:
                    poem[l].append(new_word)
    return poem

# # Return Boolean indicating whether word is noun according to WordNet
def is_noun(word):
    if word not in dets_etc: # if not a conjunction, determiner, pronoun, etc. (WordNet doesn't account for these)
        syn = wordnet.synsets(word)
        # UNUSED: can get POS of ith sense using syn[i].pos()
        if syn: # if WordNet entry exists, check if most occurrences are nouns:
            # sum frequencies for all senses
            freq = 0
            for s in syn:
                for l in s.lemmas():
                    freq = freq + l.count()
            # print(freq)
            # return 
            # sum frequencies for noun senses only
            freq_n = 0
            syn_n = wordnet.synsets(word, pos=wordnet.NOUN)
            if syn_n:
                for s in syn_n:
                    for l in s.lemmas():
                        freq_n = freq_n + l.count()
            # if freq information is present, and 50% or more of occurrences are for noun senses, we'll rule it a noun
            if freq and freq_n / freq >= 0.5:
                return True
    return False

# UNUSED:
# Return Boolean indicating whether word is noun according to NLTK tagger
# def is_noun(word):
#     tag = pos_tag(word_tokenize(word))
#     # Tag will be a single-item list containing a tuple: [('word', 'POS')]
#     return tag[0][1] in nouns

# For a given poem, look up in full_dict and return stresses by line
#   0 = no stress
#   1 = primary stress
#   2 = secondary stress and 1 syllable words that aren't {nouns w stress 1}
# If words not in full_dict, append to to_lookup file and throw Exception
# Also return the number of syllables in each word (syllables)
# If not strict, all 1 syllable words are 2's
def get_stresses(poem, strict):
    # syllables should be same size and shape as poem
    syllables = copy.deepcopy(poem)
    for l, line in enumerate(syllables):
        for w, word in enumerate(line):
            syllables[l][w] = 0
    stresses = []
    unknown_words = False
    for l, line in enumerate(poem):
        stresses.append([]) # creates new row
        for w, word in enumerate(line):
            num_sylls = 0
            if word in full_dict: # look for stress #'s
                for syll in full_dict[word][0]:
                    if re.search(r'\d+', syll): # if contains #, add to array
                        stresses[l].append(int(re.search(r'\d+', syll).group()))
                        num_sylls = num_sylls + 1
            else: # add to file to be looked up later and added to new_dict
                unknown_words = True
                stresses[l].append(word) # put full word in output array
                with open(os.path.join(path, to_lookup_filename), "a") as fp:
                    fp.writelines(word+"\n")
            if strict[l] == 3: # most strict
                # if only 1 syllable and non-noun with stress 1, replace w stress 2
                if num_sylls == 1 and (stresses[l][len(stresses[l]) - 1] == 1 and not is_noun(word)):
                    stresses[l][len(stresses[l]) - 1] = 2
            elif strict[l] == 2:
                # if only 1 syllable and non-noun with stress 1, replace w stress 2
                if num_sylls == 1 and (stresses[l][len(stresses[l]) - 1] == 1 and not is_noun(word)):
                    stresses[l][len(stresses[l]) - 1] = 2
                # if 1 syllable w stress 0, replace w stress 2
                if num_sylls == 1 and (stresses[l][len(stresses[l]) - 1] == 0):
                    stresses[l][len(stresses[l]) - 1] = 2
            elif strict[l] == 1:
                # if 1 syllable, replace w stress 2
                if num_sylls == 1:
                    stresses[l][len(stresses[l]) - 1] = 2
            syllables[l][w] = num_sylls
    if unknown_words: # raise exception after all unknown words are identified
        raise Exception("Lookup words in list and add to new dict")
    return stresses, syllables

# Given a len 2 or 3 substring of stresses (ss) form, return all possible feet
def get_feet(ss):
    feet = []
    if len(ss) == 1:
        if ss in [[1], [2]]:
            feet.append("+")
        if ss in [[0], [2]]: # NEW
            feet.append("-")
    elif len(ss) == 2:
        if ss in [[0, 1], [2, 1], [0, 2], [2, 2]]:
            feet.append("-+")
        if ss in [[1, 0], [2, 0], [1, 2], [2, 2]]:
            feet.append("+-")
    elif len(ss) == 3:
        if ss in [[0, 0, 1], [2, 0, 1], [0, 2, 1], [0, 0, 2], [2, 2, 1], [2, 0, 2], [0, 2, 2], [2, 2, 2]]:
            feet.append("--+")
        if ss in [[0, 1, 0], [2, 1, 0], [0, 2, 0], [0, 1, 2], [2, 2, 0], [2, 1, 2], [0, 2, 2], [2, 2, 2]]:
            feet.append("-+-")
        if ss in [[1, 0, 0], [2, 0, 0], [1, 2, 0], [1, 0, 2], [2, 2, 0], [2, 0, 2], [1, 2, 2], [2, 2, 2]]:
            feet.append("+--")
    return feet

# Given stresses for a single line (stresses), return a list of possible metrical taggings. Each possibility is a list of strings (the feet in the line)
# In the process, fill chart of possible feet: rows = start word i (inclusive), cols = end word j (inclusive), entries = viable feet formed by that substring
def memoized_feet(stresses, i):
    # Base case:
    if len(stresses) - i == 0: # no elements left
        return []
    # Could go inside of recursive case:
    if len(stresses) - i == 1: # one element left
        # only two possible feet: "+" and "-"
        feet1 = get_feet(stresses[i:i+1]) 
        if feet1:
            chart[(i, i)] = feet1
        else: # no viable foot
            chart[(i, i)] = None 
        return chart[(i, i)] # redundant -- would get returned in last line
    # Recursive case
    j = len(stresses) - 1 # j is end word
    if (i, j) not in chart: # utilize memoization
        # Strip off len 2 foot if possible, else feet2 is []
        feet2 = get_feet(stresses[i:i+2])
        if feet2: # at least 1 len 2 foot applies
            if (i, i+1) not in chart: # initiate entry if not already there
                chart[(i, i+1)] = feet2
            else:
                chart[(i, i+1)].extend(feet2)
            # Recurse on remaining strings
            rem_feet2 = memoized_feet(stresses, i+2)
        if i+2 < len(stresses): # if len 3 foot doesn't exceed string len
            # Strip off len 3 foot if possible, else feet3 is []
            feet3 = get_feet(stresses[i:i+3])
            if feet3: # at least 1 len 3 foot applies
                if (i, i+2) not in chart: # initiate entry if not already there
                    chart[(i, i+2)] = feet3
                else:
                    chart[(i, i+2)].extend(feet3)
                # Recurse on remaining strings
                rem_feet3 = memoized_feet(stresses, i+3)
        else:
            feet3 =[]
        if (i, j) not in chart: # add substring if still not in chart
            # Must be done in order to avoid repeat additions to chart and get benefits of memoization.
            # Also allows us to ultimately return list of all possible tags
            chart[(i, j)] = []
            no_viable_foot = True # set to False when we find a viable foot
            # no viable foot/return None should happen if:
            #   - both feet2 and feet3 are []
            #   - both rem_feet2 and rem_feet3 are [] (no els left)
            # also, if just one rem, e.g. rem_feet2, is [], don't append feet2
            for first2 in feet2:
                if rem_feet2 is not None:
                    no_viable_foot = False
                    if rem_feet2:
                        for rem2 in rem_feet2:
                            possibilities2 = [first2]
                            if type(rem2) is str:
                                possibilities2.extend([rem2])
                            else:
                                possibilities2.extend(rem2)
                            chart[(i, j)].append(possibilities2)
                    else: # no els left
                        chart[(i, j)].append([first2])
            for first3 in feet3:
                if rem_feet3 is not None:
                    no_viable_foot = False
                    if rem_feet3:
                        for rem3 in rem_feet3:
                            possibilities3 = [first3]
                            if type(rem3) is str:
                                possibilities3.extend([rem3])
                            else:
                                possibilities3.extend(rem3)
                            chart[(i, j)].append(possibilities3)
                    else: # no els left
                        chart[(i, j)].append([first3])
            if no_viable_foot:
                chart[(i, j)] = None
    return chart[(i, j)] # return in either case

# Input: 3D array of possibile metric tags for all lines
# Return 3D array (histogram):
#   x: lines
#   y: metrical tagging possibilities for that line
#   z: frequency of possible feet, in order of frequency in English:
#      ["-+", "+-", "--+", "-+-", "+--", "+", "-"]
#      iambus, trochee, anapaest, ambibrach, dactyl, EOL iamb trochee with 
#      optional unstressed beat excluded, EOL unstressed as in "was the ma|tter"
def get_histogram(possibilities):
    feet = ["-+", "+-", "--+", "-+-", "+--", "+", "-"]
    hist = []
    for l, line in enumerate(possibilities):
        hist.append([])
        for p, possibility in enumerate(line):
            hist[l].append([0, 0, 0, 0, 0, 0, 0])
            for foot in possibility:
                hist[l][p][feet.index(foot)] = hist[l][p][feet.index(foot)] + 1
    return hist

# Adjust histogram so length of foot is not a factor
# A six syllable line could contain 6 len-1 feet, 3 len-2 feet, or 2 len-3 feet
# Therefore, multiply len-2 hist entries by 2 and len-3 hist entries by 3
# e.g. [0, 0, 0, 0, 0, 6, 0] --> [0, 0, 0, 0, 0, 6, 0]
#      [3, 0, 0, 0, 0, 0, 0] --> [6, 0, 0, 0, 0, 0, 0]
#      [0, 0, 2, 0, 0, 0, 0] --> [0, 0, 6, 0, 0, 0, 0]
def adjust_histogram(hist):
    adj_hist = []
    for l, line in enumerate(hist):
        adj_hist.append([])
        if line:
            for p, possibility in enumerate(line):
                adj_hist[l].append(possibility.copy())
                adj_hist[l][p][0:2] =  [x * 2 for x in adj_hist[l][p][0:2]]
                adj_hist[l][p][2:5] =  [x * 3 for x in adj_hist[l][p][2:5]]
    return adj_hist

# Input: hist for all possibilities of a single line (hist_line)
# Output: index of the most likely hist entry
# That is, the one containing the overall max
# If there is a tie, returns the entry where the max is left-most in the hist
# Repeat until the best is found
def get_best_hist(hist_line):
    # Find max # overall (max_max) and the indices where it occurs (max_max_idx)
    max_max = 0
    max_max_idx = []
    max_max_left_pos = []
    for idx, hist in enumerate(hist_line):
        curr_max = max(hist)
        if curr_max > max_max: # new max found; get rid of old indices
            max_max = curr_max
            max_max_idx = [idx]
            max_max_left_pos = [hist.index(curr_max)]
        elif curr_max == max_max: # append index to list
            max_max_idx.append(idx)
            max_max_left_pos.append(hist.index(curr_max))
    if len(max_max_idx) == 1: # if max occurs only once, return its index
        return max_max_idx[0]
    # If still multiple results:
    # Find leftmost position of max (leftmost_pos) and indices of hist_line where it occurs (leftmost_idx)
    leftmost_pos = min(max_max_left_pos)
    leftmost_idx = []
    for p, pos in enumerate(max_max_left_pos):
        if pos == leftmost_pos:
            leftmost_idx.append(max_max_idx[p])
    if len(leftmost_idx) == 1: # if max occurs only once, return its index
        return leftmost_idx[0]
    # If *still* multiple results:
    # Check they aren't identical, which would lead to endless recursion
    first = True
    first_hist = None
    first_hist_idx = None
    identical = True
    for idx, hist in enumerate(hist_line):
        if idx in leftmost_idx:
            if first:
                first = False
                first_hist = hist
                first_hist_idx = idx
            else:
                if hist != first_hist:
                    identical = False
    if identical:
        return first_hist_idx
    # Else, remove maxes and recur for the remaining few elements
    new_hist_line = []
    for idx, hist in enumerate(hist_line):
        if idx in leftmost_idx:
            new_hist = hist.copy()
            new_hist[leftmost_pos] = 0
            new_hist_line.append(new_hist)
        else:
            new_hist_line.append([0,0,0,0,0,0,0])
    return get_best_hist(new_hist_line)

# Find best hists per line and return list ranking the feet indices
# Input: 3D arrays of histograms
# Output: list ranking the feet indices
def get_ranked_feet(hist):
    # Find best histogram for each line
    # new_stresses = []
    sum_hists = [0, 0, 0, 0, 0, 0, 0]
    for h, hist_line in enumerate(hist):
        if hist_line:
            idx = get_best_hist(hist_line)
            # print(idx)
            sum_hists = [x + y for x, y in zip(sum_hists, hist_line[idx])]
    # Find ranking of feet across whole poem, using sum of best hists
    # print(sum_hists)
    sorted_tuples = sorted((e,i) for i,e in enumerate(sum_hists))
    sorted_tuples.reverse()
    ranking = [x[1] for x in sorted_tuples]
    return ranking, sum_hists

# Input: hist for all possibilities of a single line and foot ranking
# Output: index of the most likely hist entry
# That is, the one containing the max of the ranked 1 foot
# If there's a tie, find the max for the ranked 2 foot, and so forth
def get_best_hist_whole_poem(orig_hist_line, ranking):
    hist_line = copy.deepcopy(orig_hist_line)
    for foot_idx in ranking:
        max_for_foot = 0
        max_for_foot_idx = []
        new_hist_line = [[] for i in range(len(orig_hist_line))]
        for h, hist in enumerate(hist_line):
            if hist: # bypass [] elements
                if hist[foot_idx] > max_for_foot: # new max
                    max_for_foot = hist[foot_idx]
                    max_for_foot_idx = [h]
                    # Re-initialize new_hist_line
                    new_hist_line = [[] for i in range(len(orig_hist_line))]
                    new_hist_line[h] = hist.copy()
                elif hist[foot_idx] == max_for_foot: # tie w current max
                    max_for_foot_idx.append(h)
                    new_hist_line[h] = hist.copy()
        if len(max_for_foot_idx) == 1: # exactly one max
            return max_for_foot_idx[0]
        else:
            hist_line = new_hist_line # only loop through tied hists next time
    # If loop ends without a single winner, any one will do
    return max_for_foot_idx[0]

# Converts feet into printable form:
# turns a list of lists of strings into a list of lists of characters, adding foot marks (|)
def printer_format(stresses):
    printable = []
    for l, line in enumerate(stresses):
        printable.append([])
        if line: # not blank
            for string in line:
                list_version = list(string)
                list_version[-1] = list_version[-1] + "|"
                printable[l].extend(list_version)
    return printable

# UNUSED
# Return best stresses -- only uses line-by-line hists, not whole poem
# Input: 3D arrays of possibilities and corresponding histogram
# Output: most likely stresses for each line
# def get_best_stresses(hist, possibilities):
#     # Find best histogram for each line
#     new_stresses = []
#     for h, hist_line in enumerate(hist):
#         if hist_line:
#             idx = get_best_hist(hist_line)
#             # print(idx)
#             new_stresses.append(possibilities[h][idx])
#         else: # blank line
#             new_stresses.append([])
#     return printer_format(new_stresses)

# Return best stresses using whole poem
# Input: 3D arrays of possibilities, corresponding histogram, and foot ranking
# Output: most likely stresses for each line
def get_best_stresses_whole_poem(hist, possibilities, ranking):
    # Find best histogram for each line
    new_stresses = []
    best_hists = []
    for h, hist_line in enumerate(hist):
        if hist_line:
            idx = get_best_hist_whole_poem(hist_line, ranking)
            # print(idx)
            new_stresses.append(possibilities[h][idx])
            best_hists.append(hist_line[idx])
        else: # blank line
            new_stresses.append([])
            best_hists.append([])
    return printer_format(new_stresses), best_hists

# Print poem line by line with stresses above words and tabs between words.
# Uses stress notation given -- {0, 1, 2} or {+, -}, for example
def print_stresses(poem, stresses, syllables):
    for l, line in enumerate(poem):
        # print stresses
        stress_str = ""
        stress_idx = 0
        for w, word in enumerate(line):
            for syll_num in range(syllables[l][w]):
                stress_str = stress_str + str(stresses[l][stress_idx]) + ' '
                stress_idx = stress_idx + 1
            stress_str = stress_str + '\t\t'
        print(stress_str)
        # print line
        line_str = ""
        for word in line:
            if len(word) < 8: # Warning: tab lengths may vary
                line_str = line_str + word + '\t\t'
            else:
                line_str = line_str + word + '\t'
        print(line_str)
        print()

cmu_dict = cmudict.dict()
new_dict = get_new_dict()
full_dict = {**cmu_dict, **new_dict}

poem_files = ["shakespeare_xviii.txt", "dickinson_hope.txt", "moore_visit_1.txt", "frost_road.txt", "carroll_jabberwocky.txt", "poe_annabel.txt"]
# "sylvia_planets_1.txt", "sylvia_sorrow_1.txt"

for pf in poem_files:
    poem = get_poem(pf)
    # print(poem)
    # for line in poem:
    #     for word in line:
    #         if is_noun(word):
    #             print(word)

    successful = False
    strict = [3]*len(poem)
    while not successful:
        stresses, syllables = get_stresses(poem, strict)
        # print(stresses)
        # print(syllables)
        # print_stresses(poem, stresses, syllables)

        possibilities = []
        for line_num, stress_line in enumerate(stresses):
            chart = {}
            possibilities.append(memoized_feet(stress_line, 0))
            # print(chart)
            # print(possibilities[line_num])
        none_present = False
        for pl, poss_line in enumerate(possibilities):
            if poss_line is None:
                none_present = True
                strict[pl] = strict[pl] - 1
                # relax requirements on initial stresses
        if not none_present:
            successful = True

    raw_hist = get_histogram(possibilities)
    # print(raw_hist)
    hist = adjust_histogram(raw_hist)
    ranking, sum_hists = get_ranked_feet(hist)
    # print(ranking)
    # print(sum_hists)
    # new_stresses = get_best_stresses(hist, possibilities)
    # print_stresses(poem, new_stresses, syllables)
    new_stresses, best_hists = get_best_stresses_whole_poem(hist, possibilities, ranking)
    print_stresses(poem, new_stresses, syllables)
    print()