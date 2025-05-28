# Prompted Scenes Dataset

This repository provides scripts to generate synthetic datasets consisting of images with their corresponding prompts.

## Installation

1. Clone this Repository
2. Create a virtual environment with `python -m venv venv`
3. Activate the venv with `./venv/Scripts/activate` (Windows) or `source ./venv/bin/activate` (Linux/Mac)
4. Install the dependencies with `pip install -r requirements.txt`
5. Download the assets from [Nextcloud](https://nextcloud.hof-university.de/s/fCo6354cKLtXyPY) and put them in the root directory

## Usage

To generate a dataset run:

```
blenderproc run {file_path}
```

On macOS: You need to grant your code editor full disk access to allow BlenderProc to install and run a Blender instance successfully.

### Examples

Dataset of objects positioned both on and beneath a table within a room.

```
blenderproc run room.py -o {output_dir} -i {iterations}
```

## How the Code Works

All run scripts are located in the project’s root directory to ensure Blender can correctly resolve all file paths.

- The `/utils` folder contains helper functions that are used across the run scripts.

- The `/configs` folder holds configuration files for the run scripts, allowing you to easily adjust key settings and parameters.
