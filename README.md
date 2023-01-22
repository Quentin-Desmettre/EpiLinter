# EpiLinter

### An extension to efficiently display your coding style errors.

## **What can it do ?**
This extension currently checks every error that [Banana](https://github.com/Epitech/coding-style-checker) checks.

In fact, this extension uses Banana to find and display errors - Which make this extension *really* powerful, as it boosts your productivity by allowing you to get your coding style errors without having to run Banana through your terminal.

## **Requirements**

To run this extension, you will need on your computer:
* An Internet access
* A Python interpreter

## **You found a bug, or you would like a new feature ?**
Please ask us [here!](https://github.com/Quentin-Desmettre/EpiLinter/issues/new)


## **You want to improve this project ?**
Simply [fork the repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo), make your changes, and open a pull request to the `main` branch.

<br>
<br>

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