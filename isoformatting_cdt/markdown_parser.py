import frontmatter
from pathlib import Path
from yaml import parser, scanner


def parse(paths: list[Path] | list[str]) -> list[dict[Path, frontmatter.Post]]:
    """
    Parse markdown files into Post objects. Expect markdown files with frontmatter. If there are parsing errors, i.e. invalid frontmatter, lazily collect errors and report.
    """
    loaded_notes = []

    errors = []
    for path in paths:
        path_ = Path(path)
        # possible errors
        # 1. file doesnt exist
        # 2. not a markdown file
        if not path_.exists():
            raise ValueError(f"{path_} doesnt exist")
        if not path_.suffix == ".md":
            raise ValueError(f"expecting markdown file, got {path_}")
        try:
            loaded_notes.append({"path": path_, "post": frontmatter.load(str(path_))})
        except (parser.ParserError, scanner.ScannerError) as e:
            errors.append({"path": path_, "error": e})
        else:
            continue

    if errors:
        error_strs = []
        for idx, d in enumerate(errors):
            error_strs.append(f"{idx} {d['path']}\n{d['error']}")

        error_str = "\n".join(error_strs)

        raise RuntimeError(error_str)

    return loaded_notes
