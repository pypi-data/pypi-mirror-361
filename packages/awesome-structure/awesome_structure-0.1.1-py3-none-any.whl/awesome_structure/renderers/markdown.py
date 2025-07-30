from pathlib import Path

from ..tree_builder import TreeNode
from .icons import get_icon


def render_tree(node: TreeNode, prefix: str = "", is_last: bool = True) -> list:
    lines = []

    # Представление текущего узла
    connector = "└── " if is_last else "├── "
    icon = get_icon(node)
    lines.append(f"{prefix}{connector}{icon} {node.name}")

    if node.is_dir:
        # Обновляем префикс у потомка
        new_prefix = prefix + ("    " if is_last else "│   ")
        count = len(node.children)

        # Обрабатываем потомков
        for i, child in enumerate(node.children):
            is_last_child = i == (count - 1)
            child_lines = render_tree(child, new_prefix, is_last_child)
            lines.extend(child_lines)

    return lines


def render(tree: TreeNode, output_path: Path):
    """Сохранить markdown файл с построенным ASCII деревом"""
    # Генерация структуры дерева
    tree_lines = [f"{get_icon(tree)} {tree.name}"]  # Root node
    count = len(tree.children)

    # Обработка потомков
    for i, child in enumerate(tree.children):
        is_last = i == (count - 1)
        child_lines = render_tree(child, "", is_last)
        tree_lines.extend(child_lines)

    # Форматирование в markdown
    output = [
        "# Структура каталога\n",
        "```",
        *tree_lines,
        "```",
        f"\n> Сгенерировано с помощью пакета [awesome-structure](https://gitverse.ru/dv.peskov/awesome-structure) для каталога {output_path.parent}",
    ]

    # Запись результата в файл
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
