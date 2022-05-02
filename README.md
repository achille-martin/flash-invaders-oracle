# flash-invaders-oracle

This app is a modified version of the original and awesome [Flash Invaders](https://space-invaders.com/flashinvaders/), making it easier to find ALL hidden mosaics.

The concept can be extended to any street art, making you become a real hunter.

## Installation

The prototype version of the app is aimed at being used with [Termux](https://github.com/termux/termux-app) (Android Terminal Emulator).

To install Termux:
* Go to phone settings -> Security -> unknown source installations -> toggle favourite browser (you download the apk from) and file manager if necessary
* Open your browser -> go to [github releases for Termux](https://github.com/termux/termux-app) -> download latest version -> install the .apk
* Open the Termux app on Android
  * run `apt update`
  * run `apt upgrade`
  * if issues: run `apt purge game-repo -y` or `apt remove science-repo game-repo`
* Get the pkg upgrades from the terminal:   
  * run `pkg update`
  * run `pkg upgrade`
  * run `pkg install termux-tools`

To setup file access from Termux:
* In terminal, run `termux-setup-storage`
* Install vim editor from terminal, run `pkg install vim`

To setup SSH access (from remote to local):
* In terminal, run `apt install git openssh`
* In terminal, run `ssh-keygen -t ed25519 -C "NAME@example.com"` (where your email is the same as your Github account)
* Grab your created key from `.ssh/id_ed25519.pub`
* Open your github account and go to Settings → SSH key → New Key
* Enter a title and the content of  `.ssh/id_ed25519.pub`
* In the terminal, run `ssh -T git@github.com`
* Confirm that you can authenticate to your Github account: you can now use `git clone <repo>`

To clone this repo:
* In terminal, run `mkdir -p /storage/emulated/0/Python/projects`
* In terminal, run `cd <project_path>` where `<project_path>` is `/storage/emulated/0/Python/projects`
* In terminal, run `git clone git@github.com:achille-martin/flash-invaders-oracle.git`

To setup Termux APIs (for access to Android tools and functionalities):
* Install the [Termux:API app from Github](https://github.com/termux/termux-api/releases) -> download and install the .apk

To install all python packages required:
* In terminal, run `pkg install python` to obtain python in Termux
* In terminal, run `pip install -r <repo_path>/requirements.txt` where `<repo_path>` is `<project_path>/<repo_name>`

To set extra permissions for the app to work properly:
* Go to Settings -> App management -> app list -> Termux -> Permissions -> Allow storage access
* Go to Settings -> App management -> app list -> Termux:API -> Permissions -> Allow gps access

To setup SSH access (from local to remote):
To push changes to a repo, you need to configure termux and the target repo
* try `git status` in terminal (at the repo level)
* if repo is unsafe → tell git it is safe with the command prompted
* configure git:
 * `git config --global user.name "FIRST_NAME LAST_NAME"`
 * `git config --global user.email "NAME@example.com"`
* you can now push to your repo with `git push <repo_name>`

## Usage

To start using the prototype app, run `python <repo_path>/main.py`.

To stop the prototype app, enter `Ctrl + C` in Termux.
