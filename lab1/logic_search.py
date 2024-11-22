import os
import re
from itertools import groupby


from analyzer import analyse_text
import nltk
from urllib.parse import quote


path = "/files"  # for Windows
path = os.getcwd() + path
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


def find_in_dir(text):
    queries[text]=[]
    print(queries)
    os.chdir(path)
    global num
    num = 0
    result, res = [], {}
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            words_list = []
            pattern = re.compile('\"(.*?)\"', re.S)
            num += 1

            file_search_str = re.sub(pattern, lambda m: find_word(m.group()[1:-1], words_list=words_list), text)
            RSV = nested_bool_eval(file_search_str)

            new_words_list = [el for el, _ in groupby(words_list)]
            if RSV:
                with open(os.path.join(root, name), 'r') as file:
                    link = file.readline()
                    nm = file.readline()

                result.append([
                    
                    "Файл: " + os.path.abspath(os.path.join(root, name)) + "\nСписок присутствующих слов: " + str(
                        new_words_list), link])

                res["Список присутствующих слов: " + str(
                        new_words_list)] =  [link, nm]
                queries[text].append(name)

    result = {quote(key): [value[0], quote(value[1])] for key, value in res.items()}
    return result

