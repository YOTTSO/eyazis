import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import re
from collections import Counter
import os
import math


file_path = '/home/yottso/Projects/EYAZIIS-2/files'
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('russian'))
words = {}
words_weight = {}

def parse_site(url):
    try:
        # Получаем HTML-код страницы
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, что запрос выполнен успешно

        # Используем BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Извлекаем только текст страницы
        page_text = soup.get_text(separator='\n', strip=True)

        filename = f"file{len(os.listdir(file_path))+1}.txt"
        # Сохраняем текст в файл
        with open(f"../files/{filename}", "w", encoding="utf-8") as file:
            file.write(url)
            file.write("\n"+page_text)

        print(f"Текст успешно сохранен в {filename}.txt")

        analyse(page_text, f"{filename}.txt")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")


def analyse(text, filename):
    text_words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in text_words if word not in stop_words]
    word_count = Counter(filtered_words)

    global words_weight
    words_weight[filename] = {}
    file_count = sum(1 for entry in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, entry)))

    for word, count in word_count.items():
        words_weight[filename][word] = count * math.log10(file_count / len([1 for file in words_weight if word in words_weight[file]]))
