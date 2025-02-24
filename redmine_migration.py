import subprocess
from srcs_redmine_migration import cli, tkinter

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
UNDERLINE = "\x1B[4m"
END = "\x1B[0m"

INTRO = f"You are using the {BOLD}All In One tool{END} for a Redmine migration.\n\
This program will automatically process all the steps of the migration by using provided information.\n"

def main():
	print(INTRO)

	try:
		import tkinter as tk
		redmine_url, api_key, output_path, multiple_files, endpoints, process, auto, auto_indent = tkinter.tkinter_cli()
	except ImportError:
		redmine_url, api_key, output_path, multiple_files, endpoints, process, auto, auto_indent = cli.cli()

	print(f"Starting the {BOLD}extraction{END}.\n")
	if multiple_files:
		subprocess.run([
			"python3", "extract_from_redmine.py",
			"--url", redmine_url,
			"--api-key", api_key,
			"--multiple-files", f"{output_path}/extract/"
		] + [f'--endpoint={endpoint}' for endpoint in endpoints])
	else:
		subprocess.run([
			"python3", "extract_from_redmine.py",
			"--url", redmine_url,
			"--api-key", api_key,
			"--single-file", f"{output_path}/extract/redmine_data.json"
		] + [f'--endpoint={endpoint}' for endpoint in endpoints])

	if process == "Spreadsheet" or process == "Both":
		print(f"Starting the {BOLD}process{END} to spreadsheet.\n")
		if multiple_files:
			subprocess.run([
				"python3", "process_to_spreadsheet.py",
				"--output-path", f"{output_path}/spreadsheet/",
				"--multiple-input-files", f"{output_path}/extract/",
			])
		else:
			subprocess.run([
				"python3", "process_to_spreadsheet.py",
				"--output-path", f"{output_path}/spreadsheet/",
				"--single-input-file", f"{output_path}/extract/redmine_data.json",
			])

	if process == "Jira" or process == "Both":
		print(f"Starting the {BOLD}process{END} to jira.\n")
		if multiple_files:
			if auto:
				subprocess.run([
					"python3", "process_to_jira.py",
					"--multiple-input-files", f"{output_path}/extract/",
					"--multiple-output-files", f"{output_path}/jira/",
					"--auto", auto_indent
				])
			else:
				subprocess.run([
					"python3", "process_to_jira.py",
					"--multiple-input-files", f"{output_path}/extract/",
					"--multiple-output-files", f"{output_path}/jira/",
				])
		else:
			if auto:
				subprocess.run([
					"python3", "process_to_jira.py",
					"--single-input-file", f"{output_path}/extract/redmine_data.json",
					"--single-output-file", f"{output_path}/jira/jira_data.json",
					"--auto", auto_indent
				])
			else:
				subprocess.run([
					"python3", "process_to_jira.py",
					"--single-input-file", f"{output_path}/extract/redmine_data.json",
					"--single-output-file", f"{output_path}/jira/jira_data.json",
				])

	print("All processes completed successfully.")

if __name__ == "__main__":
	main()
