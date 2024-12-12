import os
import nltk
import logging
logging.basicConfig(level=logging.DEBUG)
import math
from collections import defaultdict
from lab1.analyzer import analyse_text

words_weight = {}
path = '/home/yottso/Projects/EYAZIIS-2/files'
nltk.download('punkt_tab')
queries = {}

str_to_tok = {'1': True,
              '0': False,
              'И': lambda left, right: left and right,
              'ИЛИ': lambda left, right: left or right,
              'НЕ': lambda right: not right,
              '(': '(',
              ')': ')'}

empty_re = True


def tokenize():
    dox = {}
    os.chdir(path)
    for root, dirs, files in os.walk(path, topdown=False):
        for index, name in enumerate(files, start=1):
            with open(os.path.join(root, name), "r", encoding="utf-8") as file:
                words = analyse_text(file.read())
                for word in words:
                    if dox.get(word) and index not in dox[word]:
                        dox[word].append(index)
                    elif dox.get(word) and index in dox[word]:
                        continue
                    else:
                        dox[word] = [index]

    return dox


def create_token_lst(s, str_to_token=str_to_tok):
    s = s.replace('(', ' ( ')
    s = s.replace(')', ' ) ')

    return [str_to_token[it] for it in s.split()]


def find(lst, what, start=0):
    return [i for i, it in enumerate(lst) if it == what and i >= start]


def parens(token_lst):
    left_lst = find(token_lst, '(')

    if not left_lst:
        return False, -1, -1

    left = left_lst[-1]

    if token_lst[left + 1] != 0 and token_lst[left + 1] != 1:
        right = find(token_lst, ')', left + 3)[0]
    else:
        right = find(token_lst, ')', left + 4)[0]

    return True, left, right


def bool_eval(token_lst):
    if len(token_lst) == 2:
        return token_lst[0](token_lst[1])
    else:
        return token_lst[1](token_lst[0], token_lst[2])


def formatted_bool_eval(token_lst, empty_res=empty_re):
    if not token_lst:
        return empty_res

    if len(token_lst) == 1:
        return token_lst[0]

    has_parens, l_paren, r_paren = parens(token_lst)

    if not has_parens:
        return bool_eval(token_lst)

    token_lst[l_paren:r_paren + 1] = [bool_eval(token_lst[l_paren + 1:r_paren])]

    return formatted_bool_eval(token_lst, bool_eval)


def nested_bool_eval(s):
    return formatted_bool_eval(create_token_lst(s))


num = 0


def find_word(word, words_list):

    dox = tokenize()
    result = 0
    for key, val in dox.items():
        if word == key:
            if num in val:
                words_list.append(word)
                result = 1
    return str(result)


def calculate_tf_idf(docs, term):
    """
    Рассчитывает TF-IDF для заданного термина во всех документах.
    """
    tf = {doc: words_weight[doc].get(term, 0) for doc in docs}  # Частота термина в документе
    idf = math.log10(len(docs) / (1 + sum(1 for doc in docs if term in words_weight[doc])))  # IDF
    tf_idf = {doc: tf[doc] * idf for doc in docs}
    return tf_idf

