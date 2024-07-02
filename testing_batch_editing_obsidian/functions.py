from testing_batch_editing_obsidian import definitions
from pyomd import Notes, Note, metadata
from pathlib import Path
import polars as pl


def get_notes_path() -> Path:
    """
    the path to the notes directory
    """
    vault_path = Path(definitions.ROOT_DIR) / "test_vault"

    return vault_path


def get_notes(path: Path) -> Notes:
    """
    return the vault at `path` as a Notes batch object
    """
    return Notes(paths=path)


def get_cdt(note: Note) -> str:
    """
    return the creation date ('cdt') from a given `note` as a str
    """

    return note.metadata.frontmatter.get("cdt")[0]


def extract_dates(notes: Notes) -> list[str]:
    dates = []
    note: Note
    for note in notes.notes:
        dates.append(note.metadata.get("cdt")[0])

    return dates


def format_cdt(date_str: str) -> str:
    """
    given a note object, modify its cdt to match the format desired and return the note object
    """
    from dateutil.parser import parse

    dt = parse(date_str)

    return dt.isoformat()


def filter_notes_with_cdt(notes: Notes) -> Notes:
    """
    filter out notes without cdt field
    """
    # filtering on metadata contains an equality test to the MetadataType enum. As far as I can tell this looks for an enum class rather than the value itself
    # Use None because we dont care about the character of the value, only that the field exists
    notes.filter(has_meta=[("cdt", None, metadata.MetadataType.FRONTMATTER)])

    return notes


def validate_input_cdts(cdts: dict[str, str]) -> dict[str, str]:
    """
    iterate through the collected cdts and find any that are not numeric digit strings
    TODO: move this logic out to act on a polars dataframe. It will be a catch-all after a series of regex match and reformats.
    """

    not_numeric = {path: cdt for path, cdt in cdts.items() if not cdt.isnumeric()}

    not_length_12 = {path: cdt for path, cdt in cdts.items() if len(cdt) != 12}

    non_numerics = len(not_numeric) > 0
    non_length_12s = len(not_length_12) > 0
    if (non_numerics) and (non_length_12s):
        raise ValueError(
            f"non-numeric and incorrect lengths encountered:\n\nnot numeric:\n\n{not_numeric}\n\nnon-length 12:\n\n{not_length_12}"
        )
    elif non_numerics:
        raise ValueError(f"non-numerics detected:\n\n{not_numeric}")
    elif not_length_12:
        raise ValueError(f"non length 12s detected:\n\n{not_length_12}")
    else:
        return cdts


def update_cdt(
    notes: Notes, new_cdts: dict[Path, str], metadata_key: str, vault_path: Path
) -> Notes:
    """
    update the notes with the formatted creation dates
    """
    # remove the current fields
    notes.metadata.remove(metadata_key)

    # then add new ones
    for idx, note in enumerate(notes.notes):
        note_rel_path = path_from_vault_root(fullpath=note.path, vault_path=vault_path)
        notes.notes[idx].metadata.add(
            metadata_key, new_cdts[note_rel_path], metadata.MetadataType.FRONTMATTER
        )

    return notes


def write_updated_notes(notes: Notes, new_dir_path: Path) -> None:
    """
    write the notes to a new folder
    """

    notes.update_content(write=False)

    written_paths = []
    for note in notes.notes:
        out_filename = note.path.name
        out_path = new_dir_path / out_filename
        note.write(path=out_path)
        written_paths.append(str(out_path.relative_to(new_dir_path)))

    print(f"written the following to \"{new_dir_path}\":\n\n{"\n".join(written_paths)}")


def path_from_vault_root(fullpath: Path, vault_path: Path) -> Path:
    """
    remove the filepath above the vault for easy parsing using pathlibs `relative_to`
    """

    return fullpath.relative_to(vault_path)


def check_output(cdts: dict[str, str]) -> None:
    """
    print a table of the old cdts, new cdts and pathnames for visual inspection. Wait for user input, exit if told to otherwise continue.
    """
    df = pl.from_dict(cdts)

    print(df)
    inp = input("check output table, press 'y' to continue, 'n' to exit:\t")

    if inp == "y":
        pass
    if inp == "n":
        raise RuntimeError("'n' selected")
