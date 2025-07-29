from pathlib import Path


def import_path(path: str | Path):
    """将路径转换成导入名"""
    path = Path(path).resolve() if isinstance(path, str) else path.resolve()
    return ".".join(path.relative_to(Path()).parts)


def list_modules(path: str | Path) -> list[str]:
    """获取路径下的模块名"""
    path = Path(path) if isinstance(path, str) else path
    import_path = ".".join(path.relative_to(Path()).parts)
    namelist = []
    for x in path.iterdir():
        name = x.stem if x.is_file() and x.name.endswith(".py") else x.name
        if name.startswith("_"):
            continue
        namelist.append(f"{import_path}.{name}")
    return namelist
