import os
import re
import math
from collections import Counter
from tkinter import Tk, filedialog, messagebox, Text, Label, Button
from tooltip import Tooltip
from PyPDF2 import PdfReader
import webbrowser
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

STOP_WORDS = {
    "в", "и", "на", "с", "по", "из", "за", "от", "для", "как", "то", "о",
    "до", "это", "та", "у", "а", "или", "еще", "уже", "их", "ему", "ее", "ей",
    "он", "она", "они", "мы", "вы", "тот", "также", "этот", "эти", "их",
    "bei", "mit", "auf", "von", "zu", "für", "aus", "ist", "im", "als", "des",
    "die", "der", "den", "und", "das", "er", "sie", "wir", "es", "du", "ein"
}


# Извлечение текста из PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


# Обновленный preprocess_text с удалением стоп-слов
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zа-яё]', ' ', text)
    text = remove_stop_words(text)  # Удаляем стоп-слова
    return text




# Разделение текста на предложения (с сохранением исходного формата)
def split_into_sentences(text):
    return sent_tokenize(text)


# Вычисление TF-IDF для слов
def compute_tf_idf(sentences):
    tf_scores = []
    word_document_count = Counter()
    total_documents = len(sentences)

    # Подсчет TF для каждого предложения
    for sentence in sentences:
        words = re.findall(r'\w+', sentence.lower())  # Извлечение слов
        word_count = Counter(words)
        total_words = sum(word_count.values())
        tf = {word: count / total_words for word, count in word_count.items()}
        tf_scores.append(tf)

        # Подсчет документов, содержащих каждое слово
        unique_words = set(words)
        for word in unique_words:
            word_document_count[word] += 1

    # Подсчет IDF
    idf = {
        word: math.log(total_documents / (1 + doc_count))
        for word, doc_count in word_document_count.items()
    }

    return tf_scores, idf


# Вычисление веса предложений
def compute_sentence_weights(sentences, tf_scores, idf):
    sentence_weights = []
    total_chars = sum(len(sentence) for sentence in sentences)  # Общее количество символов в документе

    for i, sentence in enumerate(sentences):
        words = re.findall(r'\w+', sentence.lower())
        tf_idf_sum = sum(tf_scores[i].get(word, 0) * idf.get(word, 0) for word in words)

        # Позиционная функция: менее важным предложениям в начале или конце даётся меньше веса
        position_doc = 1 - abs(i - (len(sentences) / 2)) / (len(sentences) / 2)
        position_paragraph = 1 / (1 + i % 5)  # Пример: больше вес для начала абзаца

        # Итоговый вес предложения
        weight = tf_idf_sum * position_doc * position_paragraph
        sentence_weights.append((weight, sentence))

    return sentence_weights

# Генерация классического реферата
def generate_summary(sentence_weights, sentences, num_sentences=10):
    # Сортируем предложения по весу, затем выбираем топ-n предложений
    sorted_sentences = sorted(sentence_weights, key=lambda x: x[0], reverse=True)
    summary_sentences = [sentence for _, sentence in sorted_sentences[:num_sentences]]

    # Сортируем выбранные предложения по их порядку в тексте
    return sorted(summary_sentences, key=lambda s: sentences.index(s))


# Генерация N-грамм с учётом значимых слов
def generate_ngrams(text, n=2):
    words = text.split()
    words = [word for word in words if word not in STOP_WORDS]  # Фильтруем стоп-слова
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]


# Вычисление TF-IDF для N-грамм
def compute_tf_idf_ngrams(sentences, n=2):
    tf_scores = []
    ngram_document_count = Counter()
    total_documents = len(sentences)

    # Подсчет TF для каждого предложения
    for sentence in sentences:
        ngrams = generate_ngrams(sentence, n)
        ngram_count = Counter(ngrams)
        total_ngrams = sum(ngram_count.values())
        tf = {ngram: count / total_ngrams for ngram, count in ngram_count.items()}
        tf_scores.append(tf)

        # Подсчет документов, содержащих каждую N-грамму
        unique_ngrams = set(ngrams)
        for ngram in unique_ngrams:
            ngram_document_count[ngram] += 1

    # Подсчет IDF
    idf = {
        ngram: math.log(total_documents / (1 + doc_count))
        for ngram, doc_count in ngram_document_count.items()
    }

    return tf_scores, idf

# Фильтрация текста от стоп-слов
def remove_stop_words(text):
    words = text.split()
    return ' '.join(word for word in words if word not in STOP_WORDS)


# Генерация ключевых слов
def generate_keywords_ngrams(idf, tf_scores, top_n=10):
    # Суммируем TF-IDF по всем предложениям
    ngram_scores = Counter()
    for tf in tf_scores:
        for ngram, tf_value in tf.items():
            ngram_scores[ngram] += tf_value * idf.get(ngram, 0)

    # Сортируем по значимости
    sorted_keywords = sorted(ngram_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords[:top_n]


# Основной анализ текста
def analyze_document(file_path):
    original_text = extract_text_from_pdf(file_path)
    sentences = split_into_sentences(original_text)
    sentences_formatted = []
    for sentence in sentences:
         sentences_formatted.append(sentence.replace('\n', ''))
    processed_sentences = [preprocess_text(sentences_formatted) for sentences_formatted in sentences_formatted]
    tf_scores, idf = compute_tf_idf(processed_sentences)
    sentence_weights = compute_sentence_weights(sentences_formatted, tf_scores, idf)
    print(sentence_weights)

    summary = generate_summary(sentence_weights, sentences_formatted)
    keywords = generate_keywords_ngrams(idf, tf_scores, top_n=10)
    str_keywords = ''
    for keyword in keywords:
        word, weight = keyword
        str_keywords = str_keywords + word + ' --- ' + str(weight) +'\n'
    return summary, str_keywords


# Интерфейс приложения
class DocumentSummarizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматическое реферирование документов")
        self.root.geometry("800x700")

        # Заголовок
        self.label = Label(root, text="Выберите PDF-документ для анализа:", font=("Arial", 14))
        self.label.pack(pady=10)

        # Кнопка выбора файла
        self.file_button = Button(root, text="Выбрать файл", command=self.browse_file, font=("Arial", 12))
        self.file_button.pack(pady=5)
        Tooltip(self.file_button, "Выберите PDF-документ для анализа")

        # Поле для отображения пути файла
        self.file_label = Label(root, text="", font=("Arial", 10), fg="blue", cursor="hand2")
        self.file_label.pack(pady=5)

        # Поле для вывода результатов
        self.text_display = Text(root, wrap="word", font=("Arial", 12))
        self.text_display.pack(pady=10, fill="both", expand=True)

        # Кнопка для сохранения результатов
        self.save_button = Button(root, text="Сохранить результаты", command=self.save_results, font=("Arial", 12))
        self.save_button.pack(pady=5)
        Tooltip(self.save_button, "Сохраните результаты анализа в текстовый файл")

        # Инициализация
        self.file_path = None
        self.results = None

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=file_path)
            self.file_label.bind("<Button-1>", lambda e: webbrowser.open(f"file://{os.path.abspath(file_path)}"))
            self.analyze_file()

    def analyze_file(self):
        if not self.file_path:
            messagebox.showerror("Ошибка", "Файл не выбран!")
            return

        try:
            summary, keywords = analyze_document(self.file_path)
            self.results = {
                "file_path": self.file_path,
                "summary": summary,
                "keywords": keywords
            }

            # Отображение результатов
            self.text_display.delete("1.0", "end")
            self.text_display.insert("end", "Классический реферат:\n")
            for sentence in summary:
                self.text_display.insert("end", f"- {sentence}\n")
            self.text_display.insert("end", "\nСписок ключевых слов:\n")
            self.text_display.insert("end", keywords)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при анализе: {e}")

    def save_results(self):
        if not self.results:
            messagebox.showerror("Ошибка", "Нет данных для сохранения!")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(f"Файл: {self.results['file_path']}\n\n")
                file.write("Классический реферат:\n")
                for sentence in self.results["summary"]:
                    file.write(f"- {sentence}\n")
                file.write("\nСписок ключевых слов:\n")
                file.write(self.results["keywords"])
            messagebox.showinfo("Сохранение", "Результаты успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении: {e}")


# Запуск приложения
if __name__ == "__main__":
    root = Tk()
    app = DocumentSummarizerApp(root)
    root.mainloop()
