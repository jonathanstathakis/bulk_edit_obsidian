# Creation Date Formatter

## Description

A package specifically for formatting creation dates 'cdt' in markdown yaml frontmatter as isoformat. 

## Background

My Obsidian vault markdown files had undergone a series of format changes throughout its development, and coupled with some errors, resulted in 1500 files with 12(?) different date formats, and ~500 files with no creation date field at all. To solve this I manually iterated through the files sorting them based on their cdt format. After identifying common formats I wrote regex patterns to capture the datetime values and format them into strings compliant with ISO standard 8601.

## Function

1. parse a list of input files using `python-frontmatter`^[1]. This divides the frontmatter and content into different containers, with the frontmatter as a dict and the contents as a string.
2. Match each identified format with a regular expression, labeling each file as one of several identified formats. Note: this has been hard coded, but I suppose with some refactoring it could be passed a dict of 'name', 'pattern', 'repl'..
3. Replace the value of the cdt field in the parsed files ('posts') with the new ISO 8601 format
4. if dryrun = True, overwrite the old files with the new values.
5. return the posts with the updated values as a Python object.

This has the added benefit of formatting the YAML nicely.


## Use

Now that the files have been updated, this package doesnt actually serve a purpose, however it could be useful as the framework for a bulk editing API. To do so I would need to generalise the regular expression input, filtering (for example it currently filters out files without a cdt field), and validation. At the moment, however, it will serve well as a reference.

[^1]: https://python-frontmatter.readthedocs.io/en/latest/index.html

