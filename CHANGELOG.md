# **EpiLinter Changelog**

## **Release 3.0.2: February 28, 2023**
### Bug Fix
- Fixed error handling of Docker installation

## **Release 3.0.1: February 28, 2023**
### Bug Fix
- Removed debug information message

## **Release 3.0.0: February 28, 2023**
### New features
- If docker is installed on your machine, EpiLinter now hosts the tokenizer (the tool that makes it possible to parse your code) on your computer. This behaviour can be changed through the extensio'ns parameters. Please refer to the [README.md](README.md) for more informations, section `IMPORTANT - Docker usage`.

### Bug Fix
- Instead of creating a new network connection each time a file has to be checked, EpiLinter now keeps the server connection alive as long as possible.

## **Release 2.0.0: January 22, 2023**
### New features
- Ignore files matching the patterns specified in the root .gitignore.
- Ignore files matching the patterns specified inside the extension's settings (***Settings*** &rarr; ***Search*** *epilinter* &rarr; ***Edit in settings.json***). By default, it ignores everything inside the root **bonus/** and **tests/** folders.
### Bug fix
- Instead of only running the analyzer when the user modify the file, run it when the user switches file.

## **Release 1.1.0: January 19, 2023**

### Bug fix
- Updates the error detection of the extension, as banana was updated recently.

## **Release 1.0.0: November 11, 2022**

### New features
- Detects and highlights the errors detected by the banana checker.
