import json, sys, getopt, os
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

INPUT_SINGLE_FILE = False
OUTPUT_SINGLE_FILE = False
INPUT_MULTIPLE_FILE = False
OUTPUT_MULTIPLE_FILE = False
AUTO = False

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
END = "\x1B[0m"

TXT_USAGE = BOLD + "Usage: " + END + "(e.g)\n\
\tpython3 data_process_to_jira.py " + ITALIC + "-h -i <SINGLE_INPUT_FILE> -o <SINGLE_OUTPUT_FILE> -a" + END + "\n\
\tOR\n\
\tpython3 data_process_to_jira.py " + ITALIC + "--help --input-multiple-files=<MULTIPLE_INPUT_FILES> --output-multiple-files=<MULTIPLE_OUTPUT_FILE> --auto" + END

TXT_HELP = BOLD + "Options: " + END + "\n\
\t" + BOLD + "-h, -help" + END + "\n\
\t\tPrint this help paragraph.\n\n\
\t" + BOLD + "-i, --input-single-file=SINGLE_INPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single input file.\n\
\t\tDefault: " + ITALIC + "\"redmine_data.json\"" + END + "\n\n\
\t" + BOLD + "-o, --output-single-file=SINGLE_OUTPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single output file.\n\
\t\tPrefer a JSON file as it will write it in this format.\n\
\t\tDefault: " + ITALIC + "\"jira_data.json\"" + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "--input-multiple-files=MULTIPLE_INPUT_FILE" + END + " (optional)\n\
\t\tUse to choose a multiple input file.\n\
\t\tArgument is only use for the path and prefix.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--input-multiple-files=test/xyz_ will take as input ./test/xyz_projects.json..." + END + "\n\n\
\t" + BOLD + "--output-multiple-files=MULTIPLE_OUTPUT_FILE" + END + " (optional)\n\
\t\tUse to choose a multiple output file.\n\
\t\tIt will process each categories into separate file.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--output-multiple-files=test/xyz_ will output test/xyz_projects.json..." + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "-a, --auto" + END + " (recommended)\n\
\t\tUse to split data in different file that contain approximately 1500 lines."

def process_users(input_file, output_file):
	"""
	Processing users.
	"""
	try:
		with open(input_file, 'r') as file:
			users = json.load(file)

		jira_users = []
		for user in users:
			jira_user = {
				"name": f"{user['login']}",
				"groups": [],
				"email": user["mail"],
				"fullname": f"{user['firstname']} {user['lastname']}"
			}
			jira_users.append(jira_user)

		with open(output_file, 'w') as file:
			json.dump({"users": jira_users}, file, indent=4)

		print(f"Processed users saved to {output_file}")
	except Exception as e:
		print(f"An error occurred: {e}")

if __name__ == "__main__":
	input_file = 'redmine_data.json'
	output_file = 'jira_data.json'
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:a",["help", "input-single-file=", "output-single-file=", "input-multiple-files=", "output-multiple-files=", "auto"])
	except getopt.GetoptError:
		print(f"\x1B[1mUnhandle option/argument\x1B[0m (wrong option or missing required argument)\n{TXT_USAGE}")
		sys.exit(1)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(f"{TXT_USAGE}\n{TXT_HELP}")
			sys.exit(0)
		elif opt in ("-a", "--auto"):
			AUTO = True
		elif opt in ("-i", "--input-single-file"):
			if INPUT_MULTIPLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use single file input option while using multiple file option input too.\n{TXT_USAGE}")
				sys.exit(1)
			input_file = arg
			INPUT_SINGLE_FILE = True
		elif opt in ("-o", "--output-single-file"):
			if OUTPUT_MULTIPLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use single file output option while using multiple file option output too.\n{TXT_USAGE}")
				sys.exit(1)
			output_file = arg
			OUTPUT_SINGLE_FILE = True
		elif opt in ("--input-multiple-files"):
			if INPUT_SINGLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use multiple file input option while using single file input option too.\n{TXT_USAGE}")
				sys.exit(1)
			input_file = ''
			if arg:
				input_file = arg.removesuffix('.json')
			INPUT_MULTIPLE_FILE = True
		elif opt in ("--output-multiple-files"):
			if OUTPUT_SINGLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use multiple file output option while using single file output option too.\n{TXT_USAGE}")
				sys.exit(1)
			output_file = ''
			if arg:
				output_file = arg.removesuffix('.json')
			OUTPUT_MULTIPLE_FILE = True

	if not INPUT_MULTIPLE_FILE:
		INPUT_SINGLE_FILE = True
	if not OUTPUT_MULTIPLE_FILE:
		OUTPUT_SINGLE_FILE = True
	process_users(input_file, output_file)
