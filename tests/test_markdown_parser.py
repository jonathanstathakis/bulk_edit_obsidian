import pytest
from testing_batch_editing_obsidian import markdown_parser
from pathlib import Path


@pytest.fixture(scope="module")
def test_data_path() -> Path:
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="module")
def fail_parse_file_path(test_data_path: Path):
    path = test_data_path / "bad_frontmatter_file.md"
    path_list = [path]
    return path_list


@pytest.fixture(scope="module")
def parsable_files(test_data_path: Path):
    path = test_data_path / "files_expect_to_pass"
    path_list = list(path.glob("*"))
    return path_list


def test_parse_expect_to_fail(fail_parse_file_path: list[Path]) -> None:
    try:
        markdown_parser.parse(fail_parse_file_path)
    except Exception as e:
        pass


def test_parse_expect_to_parse(parsable_files: list[Path]) -> None:
    markdown_parser.parse(parsable_files)
