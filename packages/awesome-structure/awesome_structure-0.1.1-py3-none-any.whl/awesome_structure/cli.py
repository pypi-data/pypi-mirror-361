from pathlib import Path

import click

from .renderers import markdown, terminal
from .tree_builder import build_tree


@click.group()
def cli():
    """Невероятная визуализация структуры произвольного каталога"""
    pass


@cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
)
@click.option(
    "--mode",
    type=click.Choice(["terminal", "markdown"], case_sensitive=False),
    default="terminal",
    help="Вывод результата. По умолчанию terminal, соответственно результат будет выведен в терминал. "
    "Так же доступен вариант markdown, в выбранном каталоге будет создан файл awesome_structure.md "
    "содержащий структуру каталога.",
)
@click.option(
    "--hidden",
    is_flag=True,
    default=False,
    help="Добавить в выводимый результат скрытые файлы и папки (те, имя которых начинается с символа .)",
)
def admire(path: str, mode: str, hidden: bool):
    """Построить визуализацию структуры каталога"""
    root = Path(path)
    tree = build_tree(root, include_hidden=hidden)

    if mode == "terminal":
        terminal.render(tree)
    elif mode == "markdown":
        output_path = root / "awesome_structure.md"
        markdown.render(tree, output_path)
        click.echo(f"Markdown файл сохранен в {output_path}")


if __name__ == "__main__":
    cli()
