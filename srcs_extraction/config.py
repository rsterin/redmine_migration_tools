SINGLE_FILE = False
MULTIPLE_FILE = False
BASE_URL = "http://localhost/"
HEADERS = None

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
END = "\x1B[0m"

TXT_USAGE = BOLD + "Usage: " + END + "(e.g)\n\
\tpython3 extract_redmine_data.py " + ITALIC + "-h -a <API_KEY> -u <URL> -s <SINGLE_OUTPUT_FILE> -m -e <ENDPOINT>" + END + "\n\
\tOR\n\
\tpython3 extract_redmine_data.py " + ITALIC + "--help --api-key=<API_KEY> --ulr=<URL> --single-file=<SINGLE_OUTPUT_FILE> --multiple-files=<MULTIPLE_OUTPUT_FILE> --endpoint=<ENDPOINT>" + END

TXT_HELP = BOLD + "Options: " + END + "\n\
\t" + BOLD + "-h, -help" + END + "\n\
\t\tPrint this help paragraph.\n\n\
\t" + BOLD + "-a, --api_key=API-KEY" + END + " (required)\n\
\t\tUse to set the API key. To find it, you need to go on redmine, then on my account, then show the key.\n\
\t\t⚠ You need to enable the REST API in the administration tab.\n\n\
\t" + BOLD + "-u, --url=URL" + END + " (optional)\n\
\t\tUse to set the URL of your Redmine server.\n\
\t\tDefault: " + ITALIC + "http://localhost/" + END + "\n\
\t\tE.g: " + ITALIC + "--url=http://my-redmine-server:8080/" + END + "\n\n\
\t" + BOLD + "-s, --single-file=SINGLE_OUTPUT_FILE" + END + " (default)\n\
\t\tUse to choose a single output file.\n\
\t\tPrefer a JSON file as it will write it in this format.\n\
\t\tDefault: " + ITALIC + "\"redmine_data.json\"" + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "-m, --multiple-files=MULTIPLE_OUTPUT_FILE" + END + " (optional)\n\
\t\tUse to choose a multiple output file.\n\
\t\tIt will extract each categories into separate file.\n\
\t\tYou can add a prefix as argument, e.g: " + ITALIC + "--multiple-files=test_data_ will output test_data_projects.json, test_data_issues.json..." + END + "\n\
\t\t⚠ It will clear the file if already exist or create it if not existing.\n\n\
\t" + BOLD + "-e, --endpoint=ENDPOINT" + END + " (optional)\n\
\t\tUse to add an endpoint.\n\
\t\tYou can call it multiple time in the command line. E.g: -e test --endpoint sample/test will retrieve all data from /test.json and /sample/test.json\n\
\t\tBy deduction, you could also retrieve data from a specific endpoint, e.g: projects/3/issues will only retrieve issues from the project with id 3.\n\
\t\tThe program already retrieve data from these endpoint (and can not be deactivate):\n\
\t\t\t- /projects.json\n\
\t\t\t- /issues.json\n\
\t\t\t- /users.json\n\
\t\t\t- /news.json\n\
\t\t\t- /time_entries.json"
