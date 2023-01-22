# **EpiLinter Changelog**

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