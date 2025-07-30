
# Karman Industries - Utilities

## Installation and Setup
### General:
* [Python VSCode Setup](https://karmanindustries.sharepoint.com/sites/Engineering/_layouts/OneNote.aspx?id=%2Fsites%2FEngineering%2FSiteAssets%2FEngineering%20Notebook&wd=target%28Software%20Setup.one%7C00C51E4F-6D68-41E7-8A3C-AFA4B6B40681%2FPython%20VSCode%20Setup%7CE146EBA0-D387-4465-AE01-3EBF2BBA9C66%2F%29)
* [How to Clone a Git Repo](https://karmanindustries.sharepoint.com/sites/Engineering/_layouts/OneNote.aspx?id=%2Fsites%2FEngineering%2FSiteAssets%2FEngineering%20Notebook&wd=target%28Software%20Setup.one%7C00C51E4F-6D68-41E7-8A3C-AFA4B6B40681%2FClone%20a%20Git%20Repo%7C194A69B3-D3AF-4F01-AA40-5E20263887AD%2F%29)
* [How to Setup Git](https://karmanindustries.sharepoint.com/sites/Engineering/_layouts/OneNote.aspx?id=%2Fsites%2FEngineering%2FSiteAssets%2FEngineering%20Notebook&wd=target%28Software%20Setup.one%7C00C51E4F-6D68-41E7-8A3C-AFA4B6B40681%2FGit%20Setup%7C77DE0CC1-4366-45DF-8EC5-1043019BFBB5%2F%29)


### Install:
Please clone to the following directory, by all users using the same directory we avoid several common issues:
```commandline
C:\Code\
```

## How to contribute
### Formatting Code
Formatting is automatically done using Ruff. Ruff is a code formatter for Python which has several advantages:
-	Ruff enforces a uniform style across the codebase, making it easier for team members to read and understand each other’s code.
-	The resulting standardized format reduces code review overhead.
-	It reduces merge conflicts resulting from different styles.
-	Removes the need for a developer to do any formatting.
-	Lastly it can be integrated into CI/CD pipelines to ensure code is formatted prior to merge.

### Documentation
Documentation is done using [Sphinx](https://www.sphinx-doc.org/en/master/index.html).

The [Google style docstring format](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) is used.

To generate the documentation, run the following:
```commandline
C:\Code\ki-utils>sphinx-apidoc -o docs .
C:\Code\ki-utils>cd docs
C:\Code\ki-utils\docs>make html
# or if overwriting old:
C:\Code\ki-utils\docs>make clean html
```
