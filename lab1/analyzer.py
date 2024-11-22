import nltk
from nltk.corpus import stopwords, wordnet
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Загрузка стоп-слов
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
nltk.download('wordnet')



def analyse_text(text):
    # Токенизация
    words = word_tokenize(text)

    # Удаление стоп-слов
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    # Подсчет частотности
    fdist = FreqDist(filtered_words)

    # Подготовка данных для TF-IDF
    corpus = [' '.join(filtered_words)]

    # Расчет TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Получение списка слов и их TF-IDF значений
    word_tfidf = list(zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0]))

    # Сортировка по TF-IDF
    sorted_words = sorted(word_tfidf, key=lambda x: x[1], reverse=True)

    # Вывод списка ключевых слов
    for word, tfidf in sorted_words:
        pass
    
        # print(f'{word}: {tfidf:.4f}')
    tokens = [i[0] for i in sorted_words]
    for i in text.split():
        if i.lower() in tokens:
            tokens[tokens.index(i.lower())] = i
    return tokens


