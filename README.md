# Redmine Migration Tools

This repository contains a set of Python tools for extracting data from Redmine, processing it, and exporting it to either Jira or spreadsheet format. The tools are designed to work together as part of a migration pipeline.

Tested with Redmine 3.4.6 and 6.0.3.

## Table of contents

- [Main Tool](#main-tool)
- [Additional Tool](#additional-tool)
- [Detailed Documentation](#detailed-documentation)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Main program](#main-program)
  - [Additional program](#additional-program)

## Main Tool

The primary tool of this project is the all-in-one migration program that will automatically do all the steps of the migration for you:

- [`redmine_migration.py`](REDMINE_MIGRATION.md) - Automates the entire migration process from Redmine to Jira and/or spreadsheet format.

## Additional Tool

If you're having trouble with the all-in-one tool, or just want to do it step by step on your own, you can use these programs:

1. [`extract_from_redmine.py`](extract_from_redmine.py) - Extracts data from a Redmine instance via its API.
2. [`process_to_jira.py`](process_to_jira.py) - Processes the extracted Redmine data and converts it to Jira format.
3. [`process_to_spreadsheet.py`](process_to_spreadsheet.py) - Processes the extracted Redmine data and exports it to spreadsheet format.

## Detailed Documentation

For detailed information about each component, please refer to:

- [EXTRACT.md](EXTRACT.md) - Documentation for the Redmine extraction tool.
- [PROCESS_TO_JIRA.md](PROCESS_TO_JIRA.md) - Documentation for the Jira conversion tool.
- [PROCESS_TO_SPREADSHEET.md](PROCESS_TO_SPREADSHEET.md) - Documentation for the spreadsheet export tool.

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages (install via pip):
  ```
  pip install -r requirements.txt
  ```

## Usage

### Main program

To run the main program:
 ```
 python3 redmine_migration.py
 ```
It will try to use tkinter if install, and if not, you will be able to use CLI input.

### Additional program

And if you want to run each program separatelly:

1. Extract the data:
   ```bash
   python3 extract_from_redmine.py --url <redmine_url> --api-key <your_api_key>
   ```

2. Convert to Jira format:
   ```bash
   python3 process_to_jira.py
   ```

3. Export to spreadsheets:
   ```bash
   python3 process_to_spreadsheet.py
   ```
Don't forget to use the --help option to have info about how to use each tool.


