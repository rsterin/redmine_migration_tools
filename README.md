# Redmine Migration Tools

This repository contains a set of Python tools for extracting data from Redmine, processing it, and exporting it to either Jira or spreadsheet format. The tools are designed to work together as part of a migration pipeline.

Tried on version 3.4.6 of Redmine.

## Components

The toolkit consists of three main scripts:

1. [`extract_from_redmine.py`](EXTRACT.md) - Extracts data from a Redmine instance via its API
2. [`process_to_jira.py`](PROCESS_TO_JIRA.md) - Processes the extracted Redmine data and converts it to Jira format
3. [`process_to_spreadsheet.py`](PROCESS_TO_SPREADSHEET.md) - Processes the extracted Redmine data and exports it to spreadsheet format

## Quick Start

1. Extract data from Redmine:
   ```bash
   python3 extract_from_redmine.py --url <redmine_url> --api-key <your_api_key>
   ```

2. Convert to Jira format:
   ```bash
   python3 process_to_jira.py
   ```

   OR

3. Export to spreadsheets:
   ```bash
   python3 process_to_spreadsheet.py
   ```

## Detailed Documentation

For detailed information about each component, please refer to:

- [EXTRACT.md](EXTRACT.md) - Documentation for the Redmine extraction tool
- [PROCESS_TO_JIRA.md](PROCESS_TO_JIRA.md) - Documentation for the Jira conversion tool
- [PROCESS_TO_SPREADSHEET.md](PROCESS_TO_SPREADSHEET.md) - Documentation for the spreadsheet export tool

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages (install via pip):
  ```
  pip install -r requirements.txt
  ```
