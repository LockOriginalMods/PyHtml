import http.server
import socketserver
import json
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
from typing import Optional, Union, List
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Утилита для очистки атрибутов
def clean_attributes(attributes):
    return {key.rstrip('_'): value for key, value in attributes.items()}

# Базовый класс HTML-тега
class Tag:
    def __init__(self, name: str, content: Optional[Union[str, List['Tag']]] = None,
                 is_single: bool = False, **attributes: str):
        self.name = name
        self.content = content or ""
        self.is_single = is_single
        self.attributes = clean_attributes(attributes)

    def __str__(self):
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        if attrs:
            attrs = " " + attrs
        if self.is_single:
            return f"<{self.name}{attrs} />"
        if isinstance(self.content, list):
            inner = "".join(map(str, self.content))
            return f"<{self.name}{attrs}>{inner}</{self.name}>"
        return f"<{self.name}{attrs}>{self.content}</{self.name}>"

    def render(self, indent=0) -> str:
        space = "  " * indent
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        if attrs:
            attrs = " " + attrs
        if self.is_single:
            return f"{space}<{self.name}{attrs} />"
        if isinstance(self.content, list):
            inner = "\n".join(
                child.render(indent + 1) if isinstance(child, Tag) else f"{space}  {child}"
                for child in self.content
            )
            return f"{space}<{self.name}{attrs}>\n{inner}\n{space}</{self.name}>"
        return f"{space}<{self.name}{attrs}>{self.content}</{self.name}>"


# Универсальная функция для создания HTML-тега
def tag(name: str, *children, is_single=False, **attributes) -> Tag:
    content = list(children) if children else None
    return Tag(name, content, is_single, **attributes)

# Удобные функции для создания тегов
def html(*children): return tag("html", *children)
def head(*children): return tag("head", tag("meta", is_single=True, charset="UTF-8"), *children)
def body(*children): return tag("body", *children)
def title(content): return tag("title", content)
def h1(content, **attributes): return tag("h1", content, **attributes)
def p(content, **attributes): return tag("p", content, **attributes)
def div(*children, **attributes): return tag("div", *children, **attributes)
def ul(*children, **attributes): return tag("ul", *children, **attributes)
def li(content, **attributes): return tag("li", content, **attributes)
def a(content, href="#", **attributes): return tag("a", content, href=href, **attributes)
def img(src, **attributes): return tag("img", is_single=True, src=src, **attributes)
def br(**attributes): return tag("br", is_single=True, **attributes)
def link(href, rel="stylesheet", **attributes): return tag("link", is_single=True, href=href, rel=rel, **attributes)
def script(content=None, src=None, **attributes):
    if src: return tag("script", "", src=src, **attributes)
    return tag("script", content, **attributes)
def style(content): return tag("style", content)

# Макросы (компоненты)
def card(title, content, image_src):
    return div(
        img(src=image_src, alt=title, class_="card-img"),
        h1(title, class_="card-title"),
        p(content, class_="card-content"),
        class_="card"
    )

def navbar(brand, *links, class_="navbar"):
    return div(
        tag("span", brand, class_="navbar-brand"),
        ul(*(li(a(link_text, href=href), class_="navbar-item") for href, link_text in links)),
        class_=class_
    )

# Генерация JSON
def generate_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Генерация XML
def generate_xml(root_name, data, filename):
    def build_xml_tree(parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                child = SubElement(parent, key)
                build_xml_tree(child, value)
        elif isinstance(data, list):
            for item in data:
                item_element = SubElement(parent, "item")
                build_xml_tree(item_element, item)
        else:
            parent.text = str(data)

    root = Element(root_name)
    build_xml_tree(root, data)

    xml_string = tostring(root, encoding="unicode")
    pretty_xml = xml.dom.minidom.parseString(xml_string).toprettyxml()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

# Функция для сохранения HTML в файл
def save_html(filename, content: Tag):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content.render())

# Запуск локального сервера
def start_server(directory="."):
    PORT = 8000
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logging.info(f"Сервер запущен на http://localhost:{PORT}")
        httpd.serve_forever()

# Функция для генерации CSS
def generate_css(filename, styles):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(styles)

# Функция для генерации JS
def generate_js(filename, scripts):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(scripts)

# Пример использования
if __name__ == "__main__":
    # Генерация HTML
    page = html(
        head(
            title("Моя улучшенная страница"),
            link(href="styles.css"),
            script(src="app.js")
        ),
        body(
            h1("Привет, мир!", style="color:blue;"),
            p("Это абзац.", class_="text"),
            div(
                ul(
                    li("Элемент списка 1"),
                    li("Элемент списка 2"),
                    li("Элемент списка 3")
                )
            ),
            card("Карточка 1", "Описание первой карточки", "image1.jpg"),
            card("Карточка 2", "Описание второй карточки", "image2.jpg"),
            a("Ссылка на Google", href="https://www.google.com", target="_blank"),
            img(src="image.jpg", alt="Пример изображения", width="500"),
            br(),
            p("Абзац с переносом строки.")
        )
    )
    save_html("index.html", page)

    # Генерация CSS
    styles = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}
h1 {
    color: #333;
    text-align: center;
}
p.text {
    font-size: 16px;
    color: #555;
}
.card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    margin: 16px;
    background: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.card-title {
    font-size: 20px;
    margin-bottom: 8px;
}
.card-content {
    color: #666;
}
"""
    generate_css("styles.css", styles)

    # Генерация JS
    scripts = """
document.addEventListener('DOMContentLoaded', () => {
    console.log('Страница загружена!');
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', () => {
            alert('Вы нажали на карточку!');
        });
    });
});
"""
    generate_js("app.js", scripts)

    # Генерация JSON
    api_data = {
        "status": "success",
        "data": {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }
    }
    generate_json(api_data, "api.json")

    # Генерация XML
    rss_data = {
        "channel": {
            "title": "Новости сайта",
            "link": "https://example.com",
            "description": "Последние новости нашего сайта",
            "item": [
                {"title": "Новость 1", "link": "https://example.com/news1", "pubDate": "2024-12-01"},
                {"title": "Новость 2", "link": "https://example.com/news2", "pubDate": "2024-12-02"}
            ]
        }
    }
    generate_xml("rss", rss_data, "rss.xml")

    # Запуск сервера
    start_server()
