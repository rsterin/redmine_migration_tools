import json, requests, sys, getopt, os
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

HEADERS = None
MULTIPLE_FILE = False
BASE_URL = "http://localhost/"

BOLD = "\x1B[1m"
ITALIC = "\x1B[3m"
END = "\x1B[0m"

TXT_USAGE = BOLD + "Usage: " + END + "(e.g)\n\
\tpython3 extract_redmine_data.py " + ITALIC + "-h -a <API_KEY> -s <SINGLE_OUTPUT_FILE>" + END + "\n\
\tOR\n\
\tpython3 extract_redmine_data.py " + ITALIC + "--help --api-key=<API_KEY> --multiple-files=<MULTIPLE_OUTPUT_FILE>" + END

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
\t\t⚠ It will clear the file if already exist or create it if not existing."

def fetch_data(endpoint, params=None):
	"""
	Fetch data from a Redmine API endpoint using parameters.
	"""
	url = f"{BASE_URL}{endpoint}"
	try:
		response = requests.get(url, headers=HEADERS, params=params, timeout=10)
		response.raise_for_status()
		return response.json()
	except Exception as err:
		print(BOLD + "Error: " + END + f"{err}")
	return None

def fetch_endpoint_data(endpoint, progress, task_id):
	"""
	Fetch all data from a given endpoint.
	"""
	all_data = []
	offset = 0
	limit = 100
	total = None

	while True:
		params = {"offset": offset, "limit": limit}
		data = fetch_data(endpoint, params)
		if data:
			key = endpoint.strip("/").split(".")[0]

			if total is None and "total_count" in data:
				total = data["total_count"]
				if key in ["projects", "issues"]:
					total *= 5
				progress.update(task_id, total=total)

			all_data.extend(data.get(key, []))
			progress.update(task_id, advance=len(data.get(key, [])))

			if len(data.get(key, [])) < limit:
				break
			offset += limit
		else:
			break
	return all_data


def fetch_project_data(project_id, progress, task_id):
	"""
	Fetch all related data for a given project.
	"""
	memberships = fetch_data(f"/projects/{project_id}/memberships.json")
	progress.update(task_id, advance=1)
	versions = fetch_data(f"/projects/{project_id}/versions.json")
	progress.update(task_id, advance=1)
	issue_categories = fetch_data(f"/projects/{project_id}/issue_categories.json")
	progress.update(task_id, advance=1)
	files = fetch_data(f"/projects/{project_id}/files.json")
	progress.update(task_id, advance=1)

	return {
		"memberships": memberships,
		"versions": versions,
		"issue_categories": issue_categories,
		"files": files
	}

def fetch_issue_data(issue_id, progress, task_id):
	"""
	Fetch all related data for a given issue.
	"""
	relations = fetch_data(f"/issues/{issue_id}/relations.json")
	progress.update(task_id, advance=4)

	return {"relations": relations}

def fetch_all_data(output_file):
	"""
	Fetch all data from key endpoints and save it into a single JSON file.
	"""
	endpoints = {
		"projects": "/projects.json",
		"issues": "/issues.json",
		"users": "/users.json",
		"time_entries": "/time_entries.json",
		"news": "/news.json"
	}

	consolidated_data = {
		"gantt": [],
		"calendar": []
	}

	with Progress(
		SpinnerColumn(),
		TextColumn("[bold blue]{task.description}"),
		BarColumn(),
		"[progress.percentage]{task.percentage:>3.0f}%",
		TimeElapsedColumn(),
	) as progress:
		for key, endpoint in endpoints.items():
			task_id = progress.add_task(f"Fetching {key}", total=None)
			data = fetch_endpoint_data(endpoint, progress, task_id)
			consolidated_data[key] = data

			if key == "projects":
				for project in data:
					project_id = project["id"]
					project_data = fetch_project_data(project_id, progress, task_id)
					project.update(project_data)

			if key == "issues":
				for issue in data:
					issue_id = issue["id"]
					issue_data = fetch_issue_data(issue_id, progress, task_id)
					issue.update(issue_data)

				for issue in data:
					if "start_date" in issue and "due_date" in issue:
						consolidated_data["gantt"].append({
							"task": issue["subject"],
							"start_date": issue["start_date"],
							"due_date": issue["due_date"],
							"assigned_to": issue.get("assigned_to", {}).get("name", "Unassigned")
						})
					if "start_date" in issue:
						consolidated_data["calendar"].append({
							"event": issue["subject"],
							"start_date": issue["start_date"],
							"end_date": issue.get("due_date", issue["start_date"])
						})

	if consolidated_data:
		cleaned_path = os.path.dirname(output_file)
		if cleaned_path:
			os.makedirs(cleaned_path, exist_ok=True)
			print("Path " + BOLD + f"{cleaned_path}/" + END + " as been created")
		if not MULTIPLE_FILE:
			with open(output_file, "w", encoding="utf-8") as file:
				json.dump(consolidated_data, file, indent=4, ensure_ascii=False)
			print("All data saved to " + BOLD + f"{output_file}" + END)
		else:
			to_save = {
				"projects",
				"issues",
				"users",
				"time_entries",
				"news",
				"gantt",
				"calendar"
			}
			for key in to_save:
				with open(output_file + key + '.json', "w", encoding="utf-8") as file:
					json.dump(consolidated_data[key], file, indent=4, ensure_ascii=False)
				print("Data as been saved to " + BOLD + f"{output_file + key + '.json'}" + END)
	else:
		print(BOLD + "Error:\n" + END + "\tData fetching failed. No data was saved.")

if __name__ == "__main__":
	output_file = 'redmine_data.json'
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hu:s:ma:",["help", "url=", "single-file=", "multiple-files=", "api-key="])
	except getopt.GetoptError:
		print(f"\x1B[1mUnhandle option/argument\x1B[0m (wrong option or missing required argument)\n{TXT_USAGE}")
		sys.exit(1)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(f"{TXT_USAGE}\n{TXT_HELP}")
			sys.exit(0)
		elif opt in ("-a", "--api-key"):
			api_key = arg
			HEADERS = {'X-Redmine-API-Key': api_key}
		elif opt in ("-u", "--url"):
			BASE_URL = arg
		elif opt in ("-s", "--single-file"):
			output_file = arg
		elif opt in ("-m", "--multiple-files"):
			output_file = ''
			MULTIPLE_FILE = True
			if arg:
				output_file = arg.removesuffix('.json')
	if HEADERS == None:
		print(f"\x1B[1mMissing API key\x1B[0m\n{TXT_USAGE}")
		sys.exit(2)
	fetch_all_data(output_file)
