# Minecraft Mod Downloader

A small Python utility for automatically downloading Minecraft mods for a specific **Minecraft version** and **mod loader**.

The project started as a simple Modrinth downloader and was later expanded with a separate CurseForge downloader.

## Features

* Download mods for a specific Minecraft version
* Support for **Fabric**
* Select preferred release types
* Download multiple mods concurrently
* Show download progress
* Save mods directly to a configured folder
* Modrinth support
* CurseForge support

## Modrinth Downloader

The main downloader uses the Modrinth API to find compatible mod versions.

It checks:

* Minecraft version
* Mod loader
* Release type

Release versions are preferred, with optional support for beta versions.

Example configuration:

```python
MINECRAFT_VERSION = "26.2"
LOADER = "fabric"

DOWNLOAD_FOLDER = r"C:\Users\Username\Documents\LocationOfTheMods"

MAX_WORKERS = 5

ALLOW_BETA = True
ALLOW_ALPHA = False

PROJECTS = {
    "Fabric API": "P7dR8mSH",
}
```

The downloader then finds a compatible version for each project and downloads the mod file.

## CurseForge Downloader

`curseforge_mod_downloader.py` provides a separate downloader for CurseForge mods.

It is kept separate from the Modrinth implementation because the two platforms use different APIs and download systems.

## Installation

Clone the repository:

```bash
git clone https://github.com/TezzePP/minecraft-mod-downloader.git
cd minecraft-mod-downloader
```

Install the required Python packages:

```bash
pip install requests tqdm
```

## Usage

Configure the Minecraft version, loader, download folder and mods in the Python script.

Then run:

```bash
python download_mods.py
```

The downloader will retrieve the latest compatible version for each configured mod and save the files to the selected folder.

## Technologies

* Python
* Requests
* tqdm
* Modrinth API
* CurseForge API

## Project Status

This is a personal utility and learning project for automating Minecraft mod downloads.

The project is functional but may require updates when the Modrinth or CurseForge APIs change.
