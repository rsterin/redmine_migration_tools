# Redmine to Spreadsheet Export Tool

This document details the usage and functionality of `process_to_spreadsheet.py`, which exports Redmine data to spreadsheet format.

## Overview

The spreadsheet export tool takes data extracted from Redmine and generates xslx files (Excel) for easy viewing, sharing, and analysis. The tool organizes the data into appropriate sheets and formats the content for readability.

## Usage

### Basic Command

```bash
python3 process_to_spreadsheet.py [OPTIONS]
```

### Optional Parameters

- `-h`, `--help`: Print an helpful paragraph
- `-i`, `--single-input-file`: Path to input Redmine data file (default: `outputs/redmine_data.json`)
- `-o`, `--output-path`: Directory path for output spreadsheets (default: `outputs/`)
- `--multiple-input-files`: Use multiple input files instead of a single file

### Examples

Basic usage with defaults:
```bash
python3 process_to_spreadsheet.py
```

With custom input file and output directory:
```bash
python3 process_to_spreadsheet.py --single-input-file outputs/my_project_data.json --output-path outputs/spreadsheets/
```

Using multiple input files:
```bash
python3 process_to_spreadsheet.py --multiple-files-input multiple_path/my_
```

## How It Works

1. The script parses command-line arguments to configure the export process
2. It loads Redmine data from the input file(s)
3. It processes and organizes the data into appropriate structures for spreadsheet format
4. It creates and formats spreadsheets for different data types (issues, users, projects, etc.)
5. The spreadsheets are saved to the specified output directory

### Multiple Files Input Mode

When `--multiple-input-files` is specified, the script expects multiple JSON files in the input directory, each containing data from a different Redmine endpoint. This allows for more organized processing and can help with large datasets.

### Spreadsheet Organization

The export creates several file for each project with inside a sheet for:
- Project details
- Issues
- Memberships
- Versions
- Time entries

## Spreadsheet Features

The generated spreadsheets include:

- Appropriate column formatting for different data types
- Filtered views for easier navigation
- Data validation where applicable
- Header rows and column width optimization
- Conditional formatting for status fields

## Integration with Other Tools

This tool is designed to work with input from [`extract_from_redmine.py`](EXTRACT.md), taking the JSON data and converting it to human-readable spreadsheets.

## Troubleshooting

### Logs

The script uses a logger that outputs at `./logs/` detailed information about the export process, which can help diagnose issues.
