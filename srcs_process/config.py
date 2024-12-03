INPUT_SINGLE_FILE = False
OUTPUT_SINGLE_FILE = False
INPUT_MULTIPLE_FILE = False
OUTPUT_MULTIPLE_FILE = False
AUTO = False
AUTO_INDENT = 5000

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
END = "\x1B[0m"

TXT_USAGE = BOLD + "Usage: " + END + "(e.g)\n\
\tpython3 data_process_to_jira.py " + ITALIC + "-h -i <SINGLE_INPUT_FILE> -o <SINGLE_OUTPUT_FILE> -a" + END + "\n\
\tOR\n\
\tpython3 data_process_to_jira.py " + ITALIC + "--help --multiple-input-files=<MULTIPLE_INPUT_FILES> --multiple-output-files=<MULTIPLE_OUTPUT_FILES> --auto=<LINE_PER_FILE>" + END

TXT_HELP = BOLD + "Options: " + END + "\n\
\t" + BOLD + "-h, -help" + END + "\n\
\t\tPrint this help paragraph.\n\n\
\t" + BOLD + "-i, --single-input-file=SINGLE_INPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single input file.\n\
\t\tDefault: " + ITALIC + "\"redmine_data.json\"" + END + "\n\n\
\t" + BOLD + "-o, --single-output-file=SINGLE_OUTPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single output file.\n\
\t\tPrefer a JSON file as it will write it in this format.\n\
\t\tDefault: " + ITALIC + "\"jira_data.json\"" + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "--multiple-input-files=MULTIPLE_INPUT_FILES" + END + " (optional)\n\
\t\tUse to choose a multiple input file.\n\
\t\tArgument is only use for the path and prefix.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--multiple-input-files=test/xyz_ will take as input ./test/xyz_projects.json..." + END + "\n\n\
\t" + BOLD + "--multiple-output-files=MULTIPLE_OUTPUT_FILES" + END + " (optional)\n\
\t\tUse to choose a multiple output file.\n\
\t\tIt will process each categories into separate file.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--multiple-output-files=test/xyz_ will output test/xyz_projects.json..." + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "-a, --auto=LINE_PER_FILE" + END + " (recommended)\n\
\t\tUse to split data in different file.\n\
\t\tDefault: " + ITALIC + "5000 lines per file" + END + "."
