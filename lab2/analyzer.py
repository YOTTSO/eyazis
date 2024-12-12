import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from collections import Counter
from langdetect import detect
from PyPDF2 import PdfReader
import re
import webbrowser  # Для открытия ссылки


# Предыдущие функции анализа
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zа-яё]', ' ', text)
    words = text.split()
    return words


def frequency_words_method(words, language_profiles):
    text_profile = Counter(words)
    results = {}
    for lang, profile in language_profiles.items():
        similarity = sum((text_profile & profile).values())
        results[lang] = similarity
    return max(results, key=results.get)


def short_words_method(words, language_profiles):
    short_words = [word for word in words if len(word) <= 5]
    text_profile = Counter(short_words)
    results = {}
    for lang, profile in language_profiles.items():
        similarity = sum((text_profile & profile).values())
        results[lang] = similarity
    return max(results, key=results.get)


def neural_network_method(text):
    return detect(text)


def build_language_profiles(training_texts):
    language_profiles = {}
    for lang, texts in training_texts.items():
        words = []
        for text in texts:
            words += preprocess_text(text)
        language_profiles[lang] = Counter(words)
    return language_profiles


# Интерфейс
class LanguageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор языка текста")
        self.root.geometry("700x500")

        # Настройка интерфейса
        self.label = tk.Label(root, text="Выберите PDF-файл для анализа:", font=("Arial", 14))
        self.label.pack(pady=10)

        self.file_entry = tk.Entry(root, width=50, font=("Arial", 12))
        self.file_entry.pack(pady=5)

        self.browse_button = tk.Button(root, text="Обзор", command=self.browse_file, font=("Arial", 12))
        self.browse_button.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Анализировать", command=self.analyze_file, font=("Arial", 14),
                                        bg="green", fg="white")
        self.analyze_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Сохранить результаты", command=self.save_results, font=("Arial", 12),
                                     bg="blue", fg="white")
        self.save_button.pack(pady=5)

        self.result_text = ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), height=10)
        self.result_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # Тренировочные данные
        self.training_texts = {
            "russian": ["Это пример текста на русском языке.", "Другой русский текст."],
            "german": ["Das ist ein Beispieltext auf Deutsch.", "Noch ein deutscher Text."]
        }
        self.language_profiles = build_language_profiles(self.training_texts)
        self.results = []  # Для хранения результатов

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def analyze_file(self):
        file_path = self.file_entry.get()
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не найден!")
            return

        try:
            test_text = extract_text_from_pdf(file_path)
            preprocessed_words = preprocess_text(test_text)

            freq_result = frequency_words_method(preprocessed_words, self.language_profiles)
            short_result = short_words_method(preprocessed_words, self.language_profiles)
            neural_result = neural_network_method(test_text)

            # Сохранение результатов анализа
            result_data = {
                "file_path": file_path,
                "freq_result": freq_result,
                "short_result": short_result,
                "neural_result": neural_result
            }
            self.results.append(result_data)

            # Отображение результатов
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Результаты анализа:\n")
            self.result_text.insert(tk.END, f"Файл: {file_path}\n")
            self.result_text.insert(tk.END, f"Метод частотных слов: {freq_result}\n")
            self.result_text.insert(tk.END, f"Метод коротких слов: {short_result}\n")
            self.result_text.insert(tk.END, f"Нейросетевой метод: {neural_result}\n")

            # Создание кликабельной ссылки
            self.result_text.insert(tk.END, "Ссылка на документ: ")
            link_start = self.result_text.index(tk.END)
            self.result_text.insert(tk.END, f"{file_path}\n")
            link_end = self.result_text.index(tk.END)
            self.result_text.tag_add("link", link_start, link_end)
            self.result_text.tag_config("link", foreground="blue", underline=True)
            self.result_text.tag_bind("link", "<Button-1>", lambda e: self.open_file(file_path))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при анализе: {e}")

    def open_file(self, file_path):
        # Открытие файла с помощью системы
        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    def save_results(self):
        if not self.results:
            messagebox.showinfo("Сохранение", "Нет результатов для сохранения.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as file:
                for result in self.results:
                    file.write(f"Файл: {result['file_path']}\n")
                    file.write(f"Метод частотных слов: {result['freq_result']}\n")
                    file.write(f"Метод коротких слов: {result['short_result']}\n")
                    file.write(f"Нейросетевой метод: {result['neural_result']}\n")
                    file.write(f"Ссылка на документ: file://{os.path.abspath(result['file_path'])}\n\n")
            messagebox.showinfo("Сохранение", "Результаты успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении: {e}")


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageAnalyzerApp(root)
    root.mainloop()
