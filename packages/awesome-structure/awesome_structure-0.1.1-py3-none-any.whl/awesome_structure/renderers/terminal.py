from ..tree_builder import TreeNode
from .icons import get_icon


def render(node: TreeNode, prefix: str = "", is_last: bool = True):
    """Вывести дерево переданного каталога в терминал"""
    connector = "└── " if is_last else "├── "
    icon = get_icon(node)
    print(f"{prefix}{connector}{icon} {node.name}")

    if node.is_dir:
        prefix += "    " if is_last else "│   "
        count = len(node.children)
        for i, child in enumerate(node.children):
            is_last_child = i == (count - 1)
            render(child, prefix, is_last_child)
