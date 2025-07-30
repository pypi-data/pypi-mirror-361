[![](https://img.shields.io/pypi/v/foliantcontrib.checksources.svg)](https://pypi.org/project/foliantcontrib.checksources/) [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.checksources.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.checksources)

# CheckSources

CheckSources is a preprocessor that checks the project’s `chapters` for missing and unmentioned files in the sources directory.

## Installation

```bash
$ pip install foliantcontrib.checksources
```

## Usage

To enable the preprocessor, add `checksources` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - checksources
```

### Options

- `not_in_chapters` –  a list of files not mentioned in the the chapters.
  No warnings will be displayed for the specified files.
  This option is useful if you don't need to add some files to the table of contents.
- `strict_check` – if a critical error is detected, the build will be failed after applying the preprocessor.
  Several checks are supported:
    - `not_exist` – checking the existence of the file.
      Checks if the file specified in chapters exists (enabled by default);
    - `duplicate` – checking for duplicate in the chapters.

  To disable strict check, use `strict_check: false`. And in order to enable all available checks, use `strict_check: true`.
- `disable_warnings` – disabling the output of warnings, just like `strict_check` supports: `not_exist` and `duplicate`.

**Example of options:**
```yaml
preprocessors:
    - checksources:
        not_in_chapters:
          - tags.md
        strict_check:
          - not_exist
        disable_warnings:
          - duplicate
```
