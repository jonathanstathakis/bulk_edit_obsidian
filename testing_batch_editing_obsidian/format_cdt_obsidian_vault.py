from pathlib import Path
import format_cdt

vault_path = Path("/Users/jonathan/001_obsidian_vault")

paths = (
    list(vault_path.glob("zettel/*.md"))
    + list(vault_path.glob("to_be_processed/*.md"))
    + list(vault_path.glob("z_literature_notes/*.md"))
)


updated_posts = format_cdt.format_cdts(paths, dryrun=False)
[(post["path"], post["post"]["cdt"]) for post in updated_posts]
