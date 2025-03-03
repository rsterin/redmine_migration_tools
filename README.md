# Redmine Migration Tools

This repository contains a set of Python tools for extracting data from Redmine, processing it, and exporting it to either Jira or spreadsheet format. The tools are designed to work together as part of a migration pipeline.

Tested on version 3.4.6 of Redmine.

## Main Tool

The primary tool of this project is the all-in-one migration program that will automatically do all the steps of the migration for you:

- [`redmine_migration.py`](REDMINE_MIGRATION.md) - Automates the entire migration process from Redmine to Jira and/or spreadsheet format.

## Quick Start

1. Run the all-in-one migration tool:
   ```bash
   python3 redmine_migration.py
   ```

## Additional Tool

If you're having trouble with the all-in-one tool, or just want to do it step by step on your own, you can use these programs:

1. [`extract_from_redmine.py`](srcs_extraction/extract_from_redmine.py) - Extracts data from a Redmine instance via its API.
2. [`process_to_jira.py`](srcs_process_to_jira/process_to_jira.py) - Processes the extracted Redmine data and converts it to Jira format.
3. [`process_to_spreadsheet.py`](srcs_process_to_spreadsheet/process_to_spreadsheet.py) - Processes the extracted Redmine data and exports it to spreadsheet format.

## Detailed Documentation

For detailed information about each component, please refer to:

- [EXTRACT.md](srcs_extraction/EXTRACT.md) - Documentation for the Redmine extraction tool.
- [PROCESS_TO_JIRA.md](PROCESS_TO_JIRA.md) - Documentation for the Jira conversion tool.
- [PROCESS_TO_SPREADSHEET.md](PROCESS_TO_SPREADSHEET.md) - Documentation for the spreadsheet export tool.

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages (install via pip):
  ```
  pip install -r requirements.txt
  ```
