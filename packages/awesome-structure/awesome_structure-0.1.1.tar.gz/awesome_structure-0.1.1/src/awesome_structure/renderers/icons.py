ICON_MAP = {
    # Директории
    "dir": "📁",
    # Основные типы файлов
    "default": "📄",
    "text": "📝",
    "markdown": "📖",
    "image": "🖼️",
    "pdf": "📑",
    "archive": "🗜️",
    "audio": "🔊",
    "video": "🎬",
    "code": "💻",
    "config": "⚙️",
    "binary": "🔢",
    "presentation": "📊",
    "spreadsheet": "📈",
    "document": "📃",
    "database": "🗄️",
    "executable": "⚡",
    "font": "🔤",
    # Конкретные расширения файлов
    ".py": "🐍",
    ".ipynb": "📓",
    ".js": "📜",
    ".ts": "📜",
    ".jsx": "⚛️",
    ".tsx": "⚛️",
    ".java": "☕",
    ".class": "☕",
    ".html": "🌐",
    ".css": "🎨",
    ".scss": "🎨",
    ".sass": "🎨",
    ".php": "🐘",
    ".rb": "💎",
    ".go": "🐹",
    ".rs": "🦀",
    ".swift": "🐦",
    ".kt": "☕",
    ".dart": "🎯",
    ".lua": "🌙",
    ".sh": "🐚",
    ".bat": "🪟",
    ".ps1": "🪟",
    ".c": "🔧",
    ".cpp": "🔧",
    ".h": "🔧",
    ".hpp": "🔧",
    ".cs": "♯",
    ".sql": "🗃️",
    ".yml": "⚙️",
    ".yaml": "⚙️",
    ".json": "🔣",
    ".xml": "📦",
    ".toml": "⚙️",
    ".ini": "⚙️",
    ".cfg": "⚙️",
    ".conf": "⚙️",
    ".env": "⚙️",
    ".gitignore": "🐙",
    ".dockerfile": "🐳",
    ".dockerignore": "🐳",
    ".md": "📖",
    ".txt": "📝",
    ".log": "📋",
    ".csv": "📊",
    ".tsv": "📊",
    ".pdf": "📑",
    ".doc": "📃",
    ".docx": "📃",
    ".odt": "📃",
    ".xls": "📈",
    ".xlsx": "📈",
    ".ods": "📈",
    ".ppt": "📊",
    ".pptx": "📊",
    ".odp": "📊",
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".png": "🖼️",
    ".gif": "🖼️",
    ".svg": "🖼️",
    ".bmp": "🖼️",
    ".tiff": "🖼️",
    ".webp": "🖼️",
    ".mp3": "🎵",
    ".wav": "🎵",
    ".flac": "🎵",
    ".ogg": "🎵",
    ".mp4": "🎬",
    ".avi": "🎬",
    ".mov": "🎬",
    ".mkv": "🎬",
    ".flv": "🎬",
    ".webm": "🎬",
    ".zip": "🗜️",
    ".tar": "🗜️",
    ".gz": "🗜️",
    ".7z": "🗜️",
    ".rar": "🗜️",
    ".bz2": "🗜️",
    ".exe": "⚡",
    ".msi": "⚡",
    ".dmg": "🍎",
    ".pkg": "🍎",
    ".app": "🍎",
    ".deb": "🐧",
    ".rpm": "🐧",
    ".apk": "📱",
    ".jar": "☕",
    ".war": "☕",
    ".ear": "☕",
    ".dat": "🗄️",
    ".db": "🗄️",
    ".sqlite": "🗄️",
    ".sqlite3": "🗄️",
    ".dump": "🗄️",
    ".bak": "🗄️",
    ".iso": "💿",
    ".vmdk": "💿",
    ".ova": "💿",
    ".ovf": "💿",
    ".ttf": "🔤",
    ".otf": "🔤",
    ".woff": "🔤",
    ".woff2": "🔤",
}


def get_icon(node) -> str:
    """Возвращает иконку для файла или директории"""
    if node.is_dir:
        return ICON_MAP["dir"]

    # Получаем все расширения файла (для случаев типа file.tar.gz)
    suffixes = node.path.suffixes
    if not suffixes:
        return ICON_MAP["default"]

    # Пробуем найти полное расширение (включая точки)
    full_extension = "".join(suffixes).lower()

    # Проверяем сначала полное расширение
    if full_extension in ICON_MAP:
        return ICON_MAP[full_extension]

    # Проверяем последнее расширение
    last_extension = suffixes[-1].lower()
    if last_extension in ICON_MAP:
        return ICON_MAP[last_extension]

    # Категории по типу файла
    if any(ext in full_extension for ext in [".doc", ".docx", ".odt"]):
        return ICON_MAP["document"]
    if any(ext in full_extension for ext in [".xls", ".xlsx", ".ods"]):
        return ICON_MAP["spreadsheet"]
    if any(ext in full_extension for ext in [".ppt", ".pptx", ".odp"]):
        return ICON_MAP["presentation"]
    if any(
        ext in full_extension
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".webp"]
    ):
        return ICON_MAP["image"]
    if any(
        ext in full_extension
        for ext in [".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm"]
    ):
        return ICON_MAP["video"]
    if any(ext in full_extension for ext in [".mp3", ".wav", ".flac", ".ogg"]):
        return ICON_MAP["audio"]
    if any(
        ext in full_extension for ext in [".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"]
    ):
        return ICON_MAP["archive"]
    if any(
        ext in full_extension
        for ext in [
            ".py",
            ".js",
            ".ts",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".dart",
            ".lua",
            ".php",
            ".sh",
            ".bat",
            ".ps1",
        ]
    ):
        return ICON_MAP["code"]
    if any(
        ext in full_extension
        for ext in [".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf", ".env"]
    ):
        return ICON_MAP["config"]

    return ICON_MAP["default"]
