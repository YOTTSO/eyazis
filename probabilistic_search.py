from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class ProbabilisticSearch:
    def __init__(self, data_dir):
        """
        Инициализация системы поиска.
        :param data_dir: Путь к папке с текстовыми файлами.
        """
        self.data_dir = data_dir
        self.documents = self._load_documents()
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)

    def _load_documents(self):
        """
        Загружает текстовые файлы из указанной директории.
        :return: Список строк, каждая строка — содержимое одного файла.
        """
        documents = []
        for filename in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    documents.append(file.read())
        return documents

    def search(self, query):
        """
        Выполняет вероятностный поиск по запросу.
        :param query: Строка запроса.
        :return: Отсортированный список релевантных документов.
        """
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        ranked_indices = similarities.argsort()[::-1]  # Сортируем по убыванию релевантности
        return [(self.documents[i], similarities[i]) for i in ranked_indices if similarities[i] > 0]
