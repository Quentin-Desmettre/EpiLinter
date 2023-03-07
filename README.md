# **EpiLinter**

### An extension to efficiently display your coding style errors.
<br>

# **Table of contents**

### **1. [What can it do ?](#what-can-it-do)**
### **2. [Important - Docker usage](#important---docker-usage)**
### **3. [Requirements](#requirements)**
### **4. [Bug reports](#you-found-a-bug-or-you-would-like-a-new-feature)**
### **5. [Improve the project](#you-want-to-improve-this-project)**
### **6. [Changelog](#epilinter-changelog)**
<br>

## **What can it do ?**
This extension currently checks every error that [Banana](https://github.com/Epitech/coding-style-checker) checks.

In fact, this extension uses Banana to find and display errors - Which make this extension *really* powerful, as it boosts your productivity by allowing you to get your coding style errors without having to run Banana through your terminal.

<br>

## **IMPORTANT - Docker usage**
In order to detect your style errors and parse your code, this extension uses Docker. If Docker is not installed, EpiLinter will use its server.

Using the Docker option, EpiLinter creates a Docker container on your computer, which will act as a server and listen on port 8081 by default. You can modify this behaviour by changing some parameters:
- To change the port on which the Docker container is listening, update the `tokenizer_port` extension's workspace/user parameter to a free port.
- To force EpiLinter to use its server, update the `use_docker` extension extension's workspace/user parameter to `true`. Please note that this is not the recommended way, as querying the EpiLinter server requires a network connection. Though, this may be a good option if your computer has limited place, as the Docker container will take roughly 500MB of disk space.

<br>

## **Requirements**

To run this extension, you will need on your computer:
* An [Internet access](https://fr.wikipedia.org/wiki/Internet) **AND/OR** [Docker](https://docs.docker.com/get-docker/) installed
* A Python interpreter

<br>

## **You found a bug, or you would like a new feature ?**
Please ask us [here!](https://github.com/Quentin-Desmettre/EpiLinter/issues/new)

<br>

## **You want to improve this project ?**
Simply [fork the repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo), make your changes, and open a pull request to the `main` branch.

<br>
<br>

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
