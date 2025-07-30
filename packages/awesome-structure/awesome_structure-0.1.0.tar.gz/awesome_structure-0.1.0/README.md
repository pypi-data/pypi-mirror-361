# awesome-structure
### О пакете

---

>Всего одна команда в терминале, отделяющая вас от наслаждения прекрасной структурой вашего проекта 😌

**CLI** (_Command Line Interface_) приложение для построения красивой визуализации структуры произвольного каталога.  
Например, для этого проекта, оно генерирует следующую визуализацию:
```
📁 awesome-structure
├── 📁 src
│   ├── 📁 awesome_structure
│   │   ├── 📁 renderers
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 icons.py
│   │   │   ├── 🐍 markdown.py
│   │   │   └── 🐍 terminal.py
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 cli.py
│   │   └── 🐍 tree_builder.py
│   └── 🐍 __init__.py
├── 📁 tests
│   └── 🐍 __init__.py
├── 📄 poetry.lock
├── ⚙️ pyproject.toml
└── 📖 README.md
```
### Установка

---
Воспользуйтесь удобным для вас менеджером пакетов:  
**pip**
```shell
pip install awesome-structure
```

**poetry**
```shell
poetry add awesome-structure
```

### Использование  

---
Вызовите ту самую заветную команду ``admire`` с указанием параметра пути к каталогу для получения удовольствия, так:
```shell
awesome-structure admire "[путь к вашему каталогу]"
```
или с явным казанием параметра ``--path`` так:
```shell
awesome-structure admire --path "[путь к вашему каталогу]"
```

Пример:
```shell
awesome-structure admire "C:\Program Files"
```

**Для корректной работы, настоятельно рекомендуется заключать путь в кавычки "".** 

Результат будет выведен в терминал.   

Если вы желаете получить результат в виде файла, доступно сохранение **markdown** разметки в файл _**awesome-structure.md**_.  
Просто при вызове команды укажите соответствующее значение в параметре ``mode``  
```shell
awesome-structure admire "C:\Program Files" --mode markdown
```

Файл будет сохранён в том каталоге, для которого строится визуализация.

По умолчанию, все скрытые файлы и каталоги (те, чьё название начинается с "**.**") не попадают в вывод результата.  
К ним могут относиться ``.env``, ``.gitignore`` и т.д.
Если вы хотите включить в вывод скрытые папки и файлы, добавьте к команде флаг ``--hidden``.
```shell
awesome-structure admire "C:\Program Files" --hidden
```
Флаги можно комбинировать и использоваться совместно. Например:
```shell
awesome-structure admire "C:\Program Files" --mode markdown --hidden
```
Порядок следования флагов не важен
```shell
awesome-structure admire "C:\Program Files" --hidden --mode markdown 
```







