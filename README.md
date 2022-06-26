# flash-invaders-oracle

## Introduction

This app is a modified version of the original and awesome [Flash Invaders](https://space-invaders.com/flashinvaders/), making it easier to find ALL hidden mosaics.

The concept can be extended to any street art, making you become a real hunter.

## Table of Contents

**[Installation](#installation)**
**[Usage](#usage)**

## Installation

The prototype version of the app is aimed at being used with [Termux](https://github.com/termux/termux-app) (Android Terminal Emulator).

### Install Termux

* Go to phone settings -> Security -> unknown source installations -> toggle favourite browser (you download the apk from) and file manager if necessary
* Open your browser -> go to [github releases for Termux](https://github.com/termux/termux-app/releases) -> download latest version -> install the .apk
* Open the Termux app on Android
  * run `apt update`
  * run `apt upgrade`
  * if issues during update: run `apt purge game-repo -y` or `apt remove science-repo game-repo`
* Get the pkg upgrades from the terminal:   
  * run `pkg update`
  * run `pkg upgrade`
  * run `pkg install termux-tools`

### Setup file access from Termux

* In terminal, run `termux-setup-storage`
* (Optional) Install vim editor from terminal, run `pkg install vim`

### Setup SSH access (from remote to local)

* In terminal, run `apt install git openssh`
* In terminal, run `ssh-keygen -t ed25519 -C "NAME@example.com"` (where your email is the same as your Github account)
* Grab your created key from `.ssh/id_ed25519.pub`
* Open your github account and go to Settings → SSH key → New Key
* Enter a title and the content of  `.ssh/id_ed25519.pub`
* In the terminal, run `ssh -T git@github.com`
* Confirm that you can authenticate to your Github account: you can now use `git clone <repo>`

### Clone the repo

* In terminal, run `mkdir -p /storage/emulated/0/Python/projects`
* In terminal, run `cd <project_path>` where `<project_path>` is `/storage/emulated/0/Python/projects`
* In terminal, run `git clone git@github.com:achille-martin/<repo_name>.git`

### Setup Termux APIs (access to Android tools and functionalities)

* Install the [Termux:API app from Github](https://github.com/termux/termux-api/releases) -> download and install the .apk
* In terminal, run `pkg install termux-api` to enable the api calls

### Setup python environment

* In terminal, run `pkg install python` to obtain python3 in Termux
* In terminal, run `pip install virtualenv` to obtain the virtual environment tool (safer and more reliable)
* In terminal, run `mkdir -p ~/venv` to create a structure for the various virtual environments (only home directory available for Termux)
* In terminal, run `cd ~/venv` then `virtualenv <repo_name>-venv -p python` to initialise the virtual environment
* In terminal, run `source ~/venv/<repo_name>-venv/bin/activate` every time you want to enter the virtual environment
* In terminal, run `pip install -r <repo_path>/requirements.txt` where `<repo_path>` is `<project_path>/<repo_name>`, to install the python package dependencies
* In terminal, run `deactivate` to exit the current virtual environment

### Set extra permissions for the app

* Go to Settings -> App management -> app list -> Termux -> Permissions -> Allow storage access
* Go to Settings -> App management -> app list -> Termux:API -> Permissions -> Allow gps access

### Setup SSH access (from local to remote)

To push changes to a repo, you need to configure termux and the target repo.

* In terminal, run `cd <repo_path>`
* In terminal, run `git status`
* if repo is unsafe: tell git it is safe with the command prompted
* configure git and you will be able to push to the repo with `git push <repo_name>`
 * `git config --global user.name "FIRST_NAME LAST_NAME"`
 * `git config --global user.email "NAME@example.com"`

## Usage

### Start the app

To start using the prototype app, run `python <repo_path>/main.py`.

_Note: make sure that you are inside your python virtual environment.
Please refer to [Setup python environment](#setup-python-environment) for venv activation._

### Stop the app

To stop the prototype app, enter `Ctrl + C` in Termux.

_Note: you can exit your python virtual environment if desired.
Please refer to [Setup python environment](#setup-python-environment) for venv deactivation._
