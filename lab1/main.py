from fastapi import FastAPI, Form, Cookie
from typing import Optional

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles

from urllib.parse import  unquote
import json
from logic_search import find_in_dir,  queries
import os
from pathlib import Path

from parser import parse_site

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

app = FastAPI()
file_path = os.getcwd() + '/files'
# Указываем путь к шаблонам
# Подключаем папку со статическими файлами
app.mount("/static", StaticFiles(directory="static"), name="static")


def read_first_lines():
    global file_path
    result = []
    # Проходим по всем файлам в указанной папке
    for filename in os.listdir(file_path):
        # Проверяем, является ли файл текстовым (например, заканчивается на .txt)
        if filename.endswith(".txt"):
            path = os.path.join(file_path, filename)

            # Открываем файл и читаем первую строку
            with open(path, 'r', encoding='utf-8') as file:
                first_line = file.readline().strip()  # Читаем первую строку и удаляем лишние пробелы
                second_line = file.readline().strip()  # Читаем вторую строку и удаляем лишние пробелы
                result.append([first_line, second_line])
    return result

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    links = read_first_lines()
    return templates.TemplateResponse(name="main.html",
                                      request=request,
                                        context={"links":links}
    )


@app.get("/upload", response_class=HTMLResponse)
async def get_text(request: Request):
    return templates.TemplateResponse(name="upload.html",
                                      request=request
    )


@app.post("/upload", response_class=RedirectResponse, status_code=303)
async def upload_text(url: str = Form(...)):
    parse_site(url)
    return RedirectResponse(url="/", status_code=303)



@app.get("/logical_search", response_class=HTMLResponse)
async def logical_search(request: Request, flag: Optional[str] = None, query: Optional[str] = None, result: str = Cookie(None)):
    if result:
        data = json.loads(result)
        result = [[unquote(key), value[0], unquote(value[1])] for key, value in data.items()]
        response = templates.TemplateResponse(name="search.html",
                                      request=request,
                                      context={"result":result,
                                               "flag":flag,
                                               "query":query})
        response.delete_cookie(key="result")
        return response
    return templates.TemplateResponse(name="search.html",
                                      request=request,
                                      context={"result":result,
                                               "flag":flag}
    )


@app.post("/logical_search", response_class=RedirectResponse, status_code=303)
async def logical_search(query: str = Form(...)):
    try:
        if query.replace(" ", "") != "":
            result = find_in_dir(query)
        else:
            # Код, который выполняется, если query пустой
            flag = 'Пожалуйста, введите запрос для поиска.'
            return RedirectResponse(url=f"/logical_search?flag={flag}", status_code=303)
    except Exception:
        flag = 'Неккоректный ввод'
        return RedirectResponse(url=f"/logical_search?flag={flag}&query={query}", status_code=303)
    if result:
        flag = 'Результат запроса:'
        response = RedirectResponse(url=f"/logical_search?flag={flag}&query={query}", status_code=303)
        response.set_cookie(key="result", value=json.dumps(result))
        return response
    else:
        flag = 'Ничего не было найдено!'
        return RedirectResponse(url=f"/logical_search?flag={flag}&query={query}", status_code=303)

@app.get("/test", response_class=HTMLResponse)
async def logical_search(request: Request, flag: Optional[str] = None, query: Optional[str] = None, result: str = Cookie(None)):
    return templates.TemplateResponse(name="new_search.html",
                                      request=request,
                                      context={"result":result,
                                               "flag":flag}
    )

@app.get("/metrics", response_class=HTMLResponse)
async def metrics(request: Request):
    result = get_metrics()

    return templates.TemplateResponse(name="metrics.html",
                                      request=request,
                                      context={"result":result}
    )



def precision(a, b):
    return a / (a + b) if (a + b) > 0 else 0

def recall(a, c):
    return a / (a + c) if (a + c) > 0 else 0

def accuracy(a, b, c, d):
    return (a + d) / (a + b + c + d)

def f_measure(p, r):
    return (2 * p * r) / (p + r) if (p + r) > 0 else 0

def error(a, b, c, d):
    return (b + c) / (a + b + c + d) if (a + b + c + d) > 0 else 0

def get_metrics():
    requests = queries
    results = {'a':[],
               'b':[],
               'c':[],
               'd':[],
               'r':[],
               'p':[],
               'accurancy':[],
               'e':[],
               'f':[]}
    for request, relevant in requests.items():
        results["a"].append(len(relevant))
        results["b"].append(0)
        results["c"].append(0)
        results["d"].append(len(os.listdir(file_path)) - len(relevant))
        results["r"].append(recall(results["a"][-1], results["c"][-1]))
        results["p"].append(precision(results["a"][-1], results["b"][-1]))
        results["accurancy"].append(accuracy(results["a"][-1],results["b"][-1],results["c"][-1],results["d"][-1]))
        results["e"].append(error(results["a"][-1],results["b"][-1],results["c"][-1],results["d"][-1]))
        results["f"].append(f_measure(results["p"][-1], results["r"][-1]))
    if queries:
        average_a=sum(results["a"]) / len(results)
        average_b=sum(results["b"]) / len(results)
        average_c=sum(results["c"]) / len(results)
        average_d=sum(results["d"]) / len(results)
        return ['Macroaverage:',
         f'recall = {sum(results["r"]) / len(results["r"])}',
         f'precision = {sum(results["p"]) / len(results["p"])}',
         f'accurancy = {sum(results["accurancy"]) / len(results["accurancy"])}',
         f'error = {sum(results["e"]) / len(results["e"])}',
         f'F-measure = {sum(results["f"]) / len(results["f"])}',
         'Microaverage:',
         f'recall = {recall(average_a, average_c)}',
         f'precision = {precision(average_a, average_b)}',
         f'accurancy = {accuracy(average_a, average_b, average_c, average_d)}',
         f'error = {error(average_a, average_b, average_c, average_d)}',
         f'F-measure = {f_measure(precision(average_a, average_b), recall(average_a, average_c))}',
                  ]

    else:
        return ["NONE"]