# Redmine Data Extraction Tool

This document details the usage and functionality of `extract_from_redmine.py`, which extracts data from a Redmine instance via its API.

## Overview

The extraction tool connects to a Redmine instance, authenticates using an API key, and downloads data from specified endpoints. The data is saved as JSON for further processing by other tools in the migration pipeline.

## Usage

### Basic Command

```bash
python3 extract_from_redmine.py --url <redmine_url> --api-key <your_api_key> [OPTIONS]
```

### Required Parameters

- `-u`, `--url`: Base URL of your Redmine instance
- `-a`, `--api-key`: Your Redmine API key, can be found on your profile page (need to be enable in redmine's settings)

### Optional Parameters

- `-h`, `--help`: Print an helpful paragraph
- `-s`, `--single-file`: Export data in a unique file with custom filename and path (default: `outputs/redmine_data.json`)
- `-m`, `--multiple-files`: Export data to multiple files instead of a single file with custom filename and path
- `-e`, `--endpoints`: Additional endpoints to fetch data from

### Examples

Basic usage:
```bash
python3 extract_from_redmine.py --url https://redmine.example.com --api-key abcd1234
```

With custom output file:
```bash
python3 extract_from_redmine.py --url https://redmine.example.com --api-key abcd1234 --single-file single_path/my_project_data.json
```

Using multiple files output:
```bash
python3 extract_from_redmine.py --url https://redmine.example.com --api-key abcd1234 --multiple-files multiple_path/my_
```

## How It Works

1. The script parses command-line arguments to configure the extraction process
2. It establishes a connection to the Redmine server using the provided URL and API key
3. It fetches data from standard and/or custom endpoints
4. The data is processed and saved to the specified output location

### Multiple Files Mode

When `--multiple-files` is specified, the script creates separate JSON files for each endpoint in the output directory, allowing for more organized data storage and easier post-processing.

### Adding Custom Endpoints

The tool comes with a set of default endpoints for common Redmine data, but you can add custom endpoints:

1. Use the `--endpoints` command-line option to add endpoints at runtime
2. Modify the `srcs_extraction/endpoints.py` file to add permanent custom endpoints

Defaults:
	- /projects.json
	- /issues.json
	- /users.json
	- /news.json
	- /time_entries.json

## Integration with Other Tools

The output from this extraction tool (`outputs/redmine_data.json`) serves as input for:

- [`process_to_jira.py`](PROCESS_TO_JIRA.md) - For migration to Jira
- [`process_to_spreadsheet.py`](PROCESS_TO_SPREADSHEET.md) - For export to spreadsheets

## Troubleshooting

### Logs

The script uses a logger at that outputs at `./logs/` detailed information about the extraction process, which can help diagnose issues.
