import time
import re


# abc_types  => fixed set of possible values (need to make it exhaustive)
data_types = ['int', 'integer', 'float', 'double','char', 'character', 'void', 'enum']

asgn_words = [['=', 'equal', 'equals', 'initialized', 'assigned'], 
    ['initialize', 'initializing', 'assign', 'assigning', 'setting'], ['set']]

dec_words = ['declare', 'create', 'initialize', 'define', 'make', 'insert']
dec_types = ['variable', 'function', 'struct', 'union', 'enum', 'pointer', 'array', 'constant']


cur_vars = ['x', 'y', 'z']


def check_word(document, word_set):
    st = time.time()
    res = []
    for x in range(0, len(document)):
        if document[x] in word_set:
            res.append(x)
#    print('elapsed time:', time.time() - st)
    return res


'''
- numeric assignments(numbers only) chk and if found send the numeric values as a list appended to words
- x,y = 2,3   -> X
'''
def assignment_check_1(document, words):
    word_set = asgn_words[0]                # "x assgn_words[0] y"
    res = check_word(document, word_set)
    for x in res:
        document[res[0]] = word_set[0]          #replacing "initialized" with "="
        var_idx = []
        val_idx = []
        left = x-1
        while(left > 0 and left > x-6):
            # print(document[left])
            if(document[left] in cur_vars) :
                var_idx.append(left)
                break
            left -= 1
        right = x+1
        while(right < len(document) and right < x+4):    # =5, =to 5, =to variable xyz 
            if(document[right].isnumeric() or document[right] in cur_vars) :
                val_idx.append(right)
                break
            right += 1
        words += var_idx
        words.append(res[0])
        words += val_idx


def assignment_check_2(document, words):
    word_set = asgn_words[1]                # " assgn_words[0] x y"
    res = check_word(document, word_set)

    for x in res:
        document[res[0]] = '='          #replacing "initializing" with "="        var_idx = []
        val_idx = []
        var_idx = []
        right = x+1
        flag = 0
        while(right < len(document) and flag != 2):    # =5, =to 5, =to variable xyz 
            if(document[right].isnumeric()) : 
                val_idx.append(right)
                flag += 1
            if(document[right] in cur_vars) :
                var_idx.append(right)
                flag += 1
            # if (flag and (document[right] == 'to' || document[right] == 'with')):
            #     pass
            right += 1
        if (var_idx[0] != words[-2] and var_idx[0] != words[-3]):
            # print(var_idx)
            # print(words)
            words += var_idx
        # words.append('=')
        if (val_idx[0] != words[-2] and val_idx[0] != words[-1]):
            words += val_idx


#main driver func
def assignment_check(document, words):
    for x in range(0, len(document)):
        if(document[x] == 'it') :
            document[x] = 'X'
    assignment_check_1(document,words)
    assignment_check_2(document,words)


# variable declaration type sentence
def var_type(document, words):
    # print (words)
    var_types = check_word(document, data_types)
    words += var_types
    for temp_var in var_types:
        variable_type = document[temp_var]
        var_name = 'x'
        initalizations = assignment_check(document, words)

        for x in words:
            print(document[x])
        print("-----------------------------------")


# declaration type sentence
#havent dealt with "and another var of ..." -might not need
def dec_type(document, words):
    res = check_word(document, dec_types)
    words += res
    if (document[res[0]] == 'variable') :
        var_type(document, words)
    else:
        pass   

# type of sentence tagger
def sentence_tagger(document):
    # document_set = set(document)
    res = check_word(document, dec_words)
    if len(res) :
        dec_type(document, res)
    else:
        pass


document = "declare variable y of type int equal to variable x".split()
document0 = "create a float variable y equal to 10 and int x equal to 20".split()
document1 = "declare a variable x of type int initializing x equal to 40".split()
document2 = "initialize x = 50".split()
sentence_tagger(document0)
word = []
# assignment_check(document,word)














# a+(b+c) * d













