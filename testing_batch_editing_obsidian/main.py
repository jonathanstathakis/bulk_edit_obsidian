from testing_batch_editing_obsidian import functions
from pathlib import Path
from testing_batch_editing_obsidian import definitions


def format_cdt_to_iso_seperators(vault_path: str, check_output: bool = False):
    vault_path_ = Path(vault_path)
    notes = functions.get_notes(vault_path_)
    notes_with_cdt = functions.filter_notes_with_cdt(notes=notes)

    # first get the input cdt fields
    metadata_key = "cdt"

    input_cdts = {}
    for note in notes.notes:
        path = functions.path_from_vault_root(
            fullpath=note.path, vault_path=vault_path_
        )
        input_cdts[path] = note.metadata.get(metadata_key)[0]

    # validate input cdts
    functions.validate_input_cdts(cdts=input_cdts)

    cdts = {}
    cdts["path"] = []
    cdts["input_cdt"] = []
    cdts["output_cdt"] = []
    for path, cdt in input_cdts.items():
        cdts["path"].append(path)
        cdts["input_cdt"].append(cdt)
        cdts["output_cdt"].append(functions.format_cdt(cdt))

    if check_output:
        functions.check_output(cdts=cdts)

    functions.update_cdt(
        notes=notes_with_cdt,
        new_cdts=dict(zip(cdts["path"], cdts["output_cdt"])),
        vault_path=vault_path_,
        metadata_key=metadata_key,
    )

    new_dir_path = Path(definitions.ROOT_DIR) / "updated_notes"
    functions.write_updated_notes(notes=notes_with_cdt, new_dir_path=new_dir_path)

    pass
