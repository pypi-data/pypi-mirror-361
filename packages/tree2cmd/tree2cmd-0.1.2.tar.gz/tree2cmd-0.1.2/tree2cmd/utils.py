def tree_from_shell_commands(commands: list[str]) -> str:
    from collections import defaultdict
    import os

    tree = {}
    for cmd in commands:
        if 'mkdir -p' in cmd or 'touch' in cmd:
            path = cmd.split()[-1].strip('"\'')
            parts = path.strip('/').split('/')
            current = tree
            for part in parts:
                current = current.setdefault(part, {})

    def _build_tree(d, prefix=''):
        lines = []
        entries = list(d.keys())
        for i, name in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = '└── ' if is_last else '├── '
            lines.append(f"{prefix}{connector}{name}")
            subtree = d[name]
            if subtree:
                extension = '    ' if is_last else '│   '
                lines.extend(_build_tree(subtree, prefix + extension))
        return lines

    lines = _build_tree(tree)
    root = next(iter(tree.keys()))
    count_dirs = sum(1 for c in commands if c.startswith('mkdir -p'))
    count_files = sum(1 for c in commands if c.startswith('touch'))
    return f"{root}\n" + '\n'.join(lines[1:]) + f"\n\n{count_dirs} directories, {count_files} files"
