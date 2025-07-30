from pathlib import Path
from typing import Any, Dict, List


class TreeNode:
    def __init__(self, name: str, path: Path, is_dir: bool):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children: List["TreeNode"] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": str(self.path),
            "is_dir": self.is_dir,
            "children": [child.to_dict() for child in self.children],
        }


def build_tree(root: Path, include_hidden: bool = False) -> TreeNode:
    """Рекурсивный обход корневого каталога и построение дерева"""
    node = TreeNode(root.name, root, root.is_dir())

    if root.is_dir():
        for path in sorted(
            root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
        ):
            # Если пользователь хочет исключить скрытые файла / папки и элемент является скрытым
            if not include_hidden and path.name.startswith("."):
                continue
            child_node = build_tree(path, include_hidden)
            node.children.append(child_node)

    return node
