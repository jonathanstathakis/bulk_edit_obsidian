import polars as pl
from pathlib import Path
from dateutil.parser import parse as dateutil_parse, ParserError as dateutil_ParserError
from datetime import datetime
import markdown_parser
import format_cdt
import frontmatter
import re

vault_path = Path("/Users/jonathan/001_obsidian_vault")

paths = (
    list(vault_path.glob("zettel/*.md"))
    + list(vault_path.glob("to_be_processed/*.md"))
    + list(vault_path.glob("z_literature_notes/*.md"))
)


# observe the string formats
def sort_cdts(posts):
    regexp_with_22_match_no_seconds = r"22\d{12}$"
    # 2022071900
    regexp_match_12_digits = r"^\d{12}$"

    space_colon_no_seconds_regexp = r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$"

    space_colon_with_seconds_regexp = (
        r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$"
    )

    no_space_colon_regexp = r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2}):(\d{2})$"
    all_hyphen_regexp = r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})$"

    matched_cdt_dicts = []
    for d in posts:
        path = str(d["path"])
        cdt = d["post"].get("cdt")

        if not cdt:
            matched_cdt_dicts.append({"name": "no_cdt", "path": path, "cdt": cdt})
        else:
            cdt_str = str(cdt)
            if cdt_str.isdigit():
                # prefixed by 22 but no seconds..
                if re.match(regexp_with_22_match_no_seconds, cdt_str):
                    matched_cdt_dicts.append(
                        {
                            "name": "match_regexp_22_no_seconds",
                            "path": path,
                            "cdt": cdt_str,
                        }
                    )
                    continue

                # 10 digit string
                if re.match(regexp_match_12_digits, cdt_str):
                    matched_cdt_dicts.append(
                        {"name": "digits_12", "path": path, "cdt": cdt_str}
                    )
                    continue
                # all other digit strings
                matched_cdt_dicts.append(
                    {
                        "name": "all_digits",
                        "path": path,
                        "cdt": cdt_str,
                    }
                )
                continue
            elif re.match(space_colon_no_seconds_regexp, cdt_str):
                matched_cdt_dicts.append(
                    {
                        "name": "space_colons_no_seconds",
                        "path": path,
                        "cdt": cdt_str,
                    }
                )
                continue
            elif re.match(space_colon_with_seconds_regexp, cdt_str):
                matched_cdt_dicts.append(
                    {
                        "name": "space_colons_with_seconds",
                        "path": path,
                        "cdt": cdt_str,
                    }
                )
                continue
            elif re.match(no_space_colon_regexp, cdt_str):
                matched_cdt_dicts.append(
                    {"name": "no_space_colon", "path": path, "cdt": cdt_str}
                )
                continue
            elif re.match(all_hyphen_regexp, cdt_str):
                matched_cdt_dicts.append(
                    {"name": "all_hyphen", "path": path, "cdt": cdt_str}
                )
                continue
            else:
                matched_cdt_dicts.append(
                    {"name": "other", "path": path, "cdt": cdt_str}
                )
    return matched_cdt_dicts


from datetime import datetime


def regexp_sub_to_datetime(pattern: str, repl: str, string: str) -> str:
    """
    format input string matched by pattern and substituted with repl then parse with dateutil and out to isoformat
    to confirm validity
    """
    subbed = re.sub(pattern, repl, string)
    parsed = dateutil_parse(subbed)
    formatted_string = parsed.isoformat()
    return formatted_string


def format_digits_12(string: str) -> str:
    """
    format datetime strings without delimiters, just 12 digits long, such as '2022042811'
    """
    if len(string) != 12:
        raise ValueError(f"expecting a string of length 12, got {len(string)}")
    if not string.isdigit():
        raise ValueError("expecting a string of digits")

    regexp = r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})"
    repl = r"\1-\2-\3T\4:\5:\6"
    subbed = re.sub(regexp, repl, string)
    parsed = dateutil_parse(subbed)
    formatted_string = parsed.isoformat()
    return formatted_string


def cdts_to_isoformat(matched_cdt_dicts) -> dict:
    regex_dicts = {
        "space_colons_no_seconds": {
            "pattern": r"^(.*)$",
            "repl": r"/1",
        },
        "space_colons_with_seconds": {"pattern": r"^(.*)$", "repl": r"/1"},
        "no_space_colon": {
            "pattern": r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2}):(\d{2})",
            "repl": r"\1-\2-\3T\4:\5:\6",
        },
        "digits_12": {
            "pattern": r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
            "repl": r"\1-\2-\3T\4:\5:00",
        },
        "match_regexp_22_no_seconds": {
            "pattern": r"22(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})",
            "repl": r"\1-\2-\3T\4:\5:00",
        },
        "all_hyphen": {
            "pattern": r"(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})",
            "repl": r"\1T\2:\3:\4",
        },
    }

    for cdt_dict in matched_cdt_dicts:
        try:
            regex_dict = regex_dicts[cdt_dict["name"]]
            cdt_dict["new_cdt"] = regexp_sub_to_datetime(
                pattern=regex_dict["pattern"],
                repl=regex_dict["repl"],
                string=cdt_dict["cdt"],
            )
        except KeyError as e:
            pass

    # validation
    for cdt_dict in matched_cdt_dicts:
        if "new_cdt" in cdt_dict.keys():
            try:
                datetime.fromisoformat(cdt_dict["new_cdt"])
            except ValueError as e:
                cdt_dict["validated"] = False
            else:
                cdt_dict["validated"] = True

    # observing failed cdt strings
    for cdt_dict in matched_cdt_dicts:
        if "validated" in cdt_dict.keys():
            if not cdt_dict["validated"]:
                print("not iso: ", cdt_dict["cdt"])

    return matched_cdt_dicts


def parse_isoformat_cdts(posts):
    """
    Format the cdts present in a list of dicts containing posts
    """

    sorted_cdts = sort_cdts(posts=posts)
    sorted_cdts = cdts_to_isoformat(matched_cdt_dicts=sorted_cdts)

    if len(posts) != len(sorted_cdts):
        raise RuntimeError(
            "somethings gone wrong in the formatting - input length differs from output length"
        )
    return sorted_cdts


def filter_no_cdts_in_cdts(cdts):
    """
    remove all elements from cdts array whose name equals 'no_cdt'
    """
    filtered_cdts = [cdt for cdt in cdts if cdt["name"] != "no_cdt"]
    return filtered_cdts


def filter_posts_without_cdt_field(posts):
    """
    remove post elements from post array if they dont have a cdt pair
    """
    filtered_posts = [post for post in posts if post["post"].get("cdt")]
    return filtered_posts


def update_cdt_in_post(cdts, posts):
    """
    update the cdts within the posts array with the string stored in the cdts dicts array
    """

    cdts_cp = cdts.copy()

    for post in posts:
        for cdt in cdts_cp:
            if post["path"] == Path(cdt["path"]):
                try:
                    post["post"]["cdt"] = cdt["new_cdt"]
                except KeyError as e:
                    e.add_note(str(cdt.keys()))
                    e.add_note(cdt["name"])
                    e.add_note(str(cdt["path"]))
                    raise e
                cdts_cp.remove(cdt)
    return posts


def validate_cdt_isoformat_in_post_array(posts):
    """
    iterate over an array of post dicts and validate the cdt within as isoformat
    """
    for post in posts:
        try:
            datetime.fromisoformat(post["post"]["cdt"])
        except ValueError as e:
            e.add_note(post["post"]["cdt"])
            e.add_note(post["path"])
            raise e


def length_filtered_cdts_eq_length_filtered_posts(filtered_cdts, filtered_posts):
    """
    validation: length of  filtered_posts  equals length of filtered_cdts
    """

    if len(filtered_posts) != len(filtered_cdts):
        raise RuntimeError(
            "something has gone wrong in the assignment of the new cdts.\n\n"
            f"len filtered_posts:{len(filtered_posts)}, len filtered_cdts: {len(filtered_cdts)}"
        )


def update_posts(posts, cdts):
    """
    Given a list of post dicts and a list of cdt dicts,replace the cdt field in the
    posts dicts with the cdt value in the cdt dicts
    """
    # dont currently support handling posts without cdt fields so filter any out of the
    # cdts and posts. Validate by checking that they are both the same length
    filtered_cdts = filter_no_cdts_in_cdts(cdts=cdts)
    filtered_posts = filter_posts_without_cdt_field(posts=posts)

    # check that they are the same length
    length_filtered_cdts_eq_length_filtered_posts(filtered_cdts, filtered_posts)

    # check that there are no paths present in posts not present in cdts, and vice versa
    if len(
        diff := set(str(cdt["path"]) for cdt in filtered_cdts).difference(
            set(str(post["path"]) for post in filtered_posts)
        )
    ):
        raise ValueError(
            f"{len(diff)} different paths detected between posts and cdts:\n\n{diff}"
        )

    filtered_posts = update_cdt_in_post(filtered_cdts, filtered_posts)

    # validate cdt in posts is isoformat
    validate_cdt_isoformat_in_post_array(filtered_posts)

    return filtered_posts


def write_posts_to_paths(posts):
    if inp := input("press 'y' to overwrite input files with updates") == "y":
        for post in posts:
            frontmatter.dump(post["post"], post["path"])
    elif inp == "n":
        raise RuntimeError("user has elected not to overwrite the files..")
    pass


def format_cdts(
    paths: list[Path], dryrun: bool = True
) -> list[dict[str, str | frontmatter.Post]]:
    """
    given a list of markdown filepaths, extract the cdts, convert to isoformat based on
    identified patterns, then update the files.

    dryrun = True does not update the physical files, allowing inspection of the updated
    files in their Post format.
    """
    posts = markdown_parser.parse(paths=paths)
    sorted_cdts = format_cdt.parse_isoformat_cdts(posts=posts)
    updated_posts = update_posts(posts=posts, cdts=sorted_cdts)

    if not dryrun:
        write_posts_to_paths(posts=updated_posts)
    return updated_posts
