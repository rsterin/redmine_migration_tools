# Redmine to Jira Conversion Tool

This document details the usage and functionality of `process_to_jira.py`, which converts Redmine data to Jira-compatible format.

## Overview

The Jira conversion tool takes data extracted from Redmine and transforms it into a format that can be imported into Jira. This includes mapping Redmine fields to their Jira equivalents, converting issue types, and preserving relationships between issues.

## Usage

### Basic Command

```bash
python3 process_to_jira.py [OPTIONS]
```

### Optional Parameters

- `-h`, `--help`: Print an helpful paragraph
- `-i`, `--single-input-file`: Path to input Redmine data file (default: `outputs/redmine_data.json`)
- `-o`, `--single-output-file`: Path to output Jira data file (default: `outputs/jira_data.json`)
- `--multiple-files-input`: Use multiple input files instead of a single file, type the same path and file prefix as for the extraction
- `--multiple-files-output`: Use multiple output files instead of a single file (recommended)
- `-a`, `--auto`: Enable automatic indentation in JSON output (default: 10 000 lines per file) (recommended)

### Examples

Basic usage with defaults:
```bash
python process_to_jira.py
```

With custom input and output files:
```bash
python process_to_jira.py --single-input-file single_path/my_project_data.json --single-output-file outputs/my_project_jira.json
```

Using multiple files for both input and output:
```bash
python process_to_jira.py --multiple-files-input multiple_path/my_ --multiple-files-output multiple_path/jira_
```

Enabling indentation:
```bash
python process_to_jira.py --auto
```

## How It Works

1. The script parses command-line arguments to configure the conversion process
2. It loads Redmine data from the input file(s)
3. It applies transformation rules to convert Redmine objects to Jira format
4. The converted data is saved to the output file(s)

### Multiple Files Mode

When using multiple files mode:

- **Input**: The script expects multiple JSON files in the specified directory, each containing data from a different Redmine endpoint
- **Output**: The script will generate separate JSON files for different types of Jira objects (issues, users, projects, etc.)

## Integration with Other Tools

This tool is designed to work with:

- Input from [`extract_from_redmine.py`](EXTRACT.md)
- The output can be used for importing into Jira via its REST API or using the manual importer

## Troubleshooting

### Logs

The script uses a logger that outputs at `./logs/` detailed information about the conversion process, which can help diagnose issues.
