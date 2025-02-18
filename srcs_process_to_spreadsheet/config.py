INPUT_SINGLE_FILE = False
INPUT_MULTIPLE_FILE = False

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
END = "\x1B[0m"

TXT_USAGE = BOLD + "Usage: " + END + "(e.g)\n\
\tpython3 process_to_spreadsheet.py " + ITALIC + "-h -i <SINGLE_INPUT_FILE> -o <OUTPUT_PATH>" + END + "\n\
\tOR\n\
\tpython3 process_to_spreadsheet.py " + ITALIC + "--help --multiple-input-files=<MULTIPLE_INPUT_FILES> --output-path=<OUTPUT_PATH>" + END

TXT_HELP = BOLD + "Options: " + END + "\n\
\t" + BOLD + "-h, -help" + END + "\n\
\t\tPrint this help paragraph.\n\n\
\t" + BOLD + "-i, --single-input-file=SINGLE_INPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single input file.\n\
\t\tDefault: " + ITALIC + "\"redmine_data.json\"" + END + "\n\n\
\t" + BOLD + "--multiple-input-files=MULTIPLE_INPUT_FILES" + END + " (optional)\n\
\t\tUse to choose a multiple input file.\n\
\t\tArgument is only use for the path and prefix.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--multiple-input-files=test/xyz_ will take as input ./test/xyz_projects.json..." + END + "\n\n\
\t" + BOLD + "-o, --output-path=OUTPUT_PATH" + END + " (default)\n\
\t\tUse to choose an output path.\n\
\t\tDefault: " + ITALIC + "\"outputs/\"" + END + "."
