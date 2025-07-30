import fnmatch
import re
import string
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from shutil import copy2
from typing import NamedTuple


class ZonaResource(NamedTuple):
    name: str
    contents: str


def get_resource(path: str) -> ZonaResource:
    """Load the packaged resource in data/path"""
    file = resources.files("zona").joinpath("data", path)
    if file.is_file():
        return ZonaResource(name=path, contents=file.read_text())
    else:
        raise FileNotFoundError(f"{path} is not a valid Zona resource!")


def get_resources(subdir: str) -> list[ZonaResource]:
    """Load the packaged resources in data/subdir"""
    out: list[ZonaResource] = []
    base = resources.files("zona").joinpath("data", subdir)

    def walk(trav: Traversable, prefix: str = ""):
        for item in trav.iterdir():
            path = f"{prefix}{item.name}"
            if item.is_dir():
                walk(item, prefix=f"{path}/")
            else:
                out.append(
                    ZonaResource(
                        name=f"{subdir}/{path}",
                        contents=item.read_text(),
                    )
                )

    walk(base)
    return out


def get_resource_dir(subdir: str) -> Path:
    dir = resources.files("zona").joinpath(f"data/{subdir}")
    with resources.as_file(dir) as path:
        assert isinstance(path, Path)
        assert path.is_dir()
        return path


def ensure_parents(target: Path):
    """Ensure the target's parent directories exist."""
    target.parent.mkdir(parents=True, exist_ok=True)


def copy_static_file(src: Path, dst: Path):
    """Copy a static file from one location to another."""
    ensure_parents(dst)
    copy2(src, dst)


def filename_to_title(path: Path) -> str:
    name = path.stem
    words = name.replace("-", " ").replace("_", " ")
    return string.capwords(words)


def normalize_url(url: str) -> str:
    if not url.startswith("/"):
        url = "/" + url
    return url


def should_ignore(path: Path, patterns: list[str], base: Path) -> bool:
    rel_path = path.relative_to(base)
    return any(
        fnmatch.fnmatch(str(rel_path), pattern) for pattern in patterns
    )


MINIFY_JS_PATTERN = re.compile(
    r"""
    //.*?$    |
    /\*.*?\*/ |
    \s+
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def minify_js(js: str) -> str:
    """Naively minifies JavaScript by stripping comments and whitespace."""
    return MINIFY_JS_PATTERN.sub(
        # replace whitespace with single space,
        # strip comments
        lambda m: " " if m.group(0).isspace() else "",
        js,
    ).strip()
