BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
UNDERLINE = "\x1B[4m"
END = "\x1B[0m"

def cli():
	# Extract
	redmine_url = input(f"Enter the Redmine {BOLD}URL{END} (default: {UNDERLINE}http://localhost){END}: ") or "http://localhost/"
	while True:
		api_key = input(f"Enter your Redmine {BOLD}API key{END}: ")
		if api_key:
			break
		print(f"{BOLD}API key cannot be empty. Please try again.{END}")
	output_path = input(f"Enter the {BOLD}output path{END} for the data (default: {UNDERLINE}outputs/{END}): ") or "outputs/"
	multiple_files = input(f"Do you want to use {BOLD}multiple files functionality{END} (one file per project, default: {UNDERLINE}yes{END})? (yes/no): ").lower() == 'yes' or True
	endpoint = input(f"Do you want to add specific {BOLD}endpoints{END} (default: {UNDERLINE}no{END}? (yes/no): ").lower() == 'yes' or False
	endpoints = []
	if endpoint:
		while True:
			tmp = input(f"Enter the {BOLD}endpoint{END} (give an empty when done): ")
			if not tmp:
				break
			endpoints.append(tmp)

	# Process
	process = input(f"Do you want to process to Jira, Spreadsheet or both ? (jira/spreadsheet/both): ").lower()
	auto = input(f"Do you want to enable auto indent (new file when X lines reached, default: {UNDERLINE}yes{END})? (yes/no): ").lower() == 'yes' or True
	if auto:
		auto_indent = input(f"How many lines per file (default: {UNDERLINE}10 000{END})?: ") or "10000"

	return redmine_url, api_key, output_path, multiple_files, endpoints, process, auto, auto_indent
