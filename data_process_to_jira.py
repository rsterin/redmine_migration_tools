import json, sys, getopt, os
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

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

def process_projects(input_file, progress, task_id):
	"""
	Processing projects and issues.

	Args:
		input_file (str): The file, path and/or prefix that should be taken as input.
		progress (Progress):
		task_id (id): Id of the current task.
	"""
	STATUS_MAPPING = {
		"Resolved": "Closed",
		"Feedback": "Closed",
		"In Progress": "In Progress",
		"New": "Open"
	}

	def map_status(status):
		return STATUS_MAPPING.get(status, "Open")

	total = 0
	try:
		if INPUT_MULTIPLE_FILE:
			projects_input_file = input_file + "projects.json"
			issues_input_file =  input_file + "issues.json"
			with open(projects_input_file, 'r') as file:
				projects = json.load(file)
			with open(issues_input_file, 'r') as file:
				issues = json.load(file)
		else:
			with open(input_file, 'r') as file:
				data = json.load(file)
			if isinstance(data, dict) and "projects" in data and "issues" in data:
				projects = data["projects"]
				issues = data["issues"]
			else:
				raise ValueError("Unexpected input format. Expected a list or an object with a 'projects' and/or 'issues' key.")

		total = len(projects) + len(issues)
		progress.update(task_id, total=total)

		jira_projects = []
		allocated_keys = set()

		for project in projects:
			base_key = project["identifier"][:10].upper()
			key = base_key

			if key in allocated_keys:
				counter = 1
				while f"{base_key[:9].upper()}{counter}" in allocated_keys:
					counter += 1
				key = f"{base_key[:9].upper()}{counter}"

			allocated_keys.add(key)

			jira_project = {
				"name": project["name"],
				"id": project["id"],
				"key": key,
				"description": project["description"],
				"type": "software",
				"versions": [],
				"components": [],
				"issues": []
			}
			for version in project.get("versions", []).get("versions", []):
				jira_version = {
					"name": version["name"],
					"released": version["status"] in ["closed", "locked"],
					"releaseDate": version["due_date"] + "T00:00:00.000+0000" if "due_date" in version else None
				}
				jira_project["versions"].append(jira_version)
			jira_projects.append(jira_project)
			progress.update(task_id, advance=1)

		for issue in issues:
			issue_info = {
				"priority": issue["priority"]["name"],
				"description": issue.get("description", ""),
				"status": map_status(issue["status"]["name"]),
				"reporter": issue["author"]["name"],
				"labels": [],
				"watchers": [],
				"issueType": issue["tracker"]["name"],
				"resolution": "Unresolved" if issue["status"]["id"] != 3 else "Resolved",
				"created": issue["created_on"],
				"updated": issue["updated_on"],
				"affectedVersions": [],
				"summary": issue["subject"],
				"assignee": None,
				"fixedVersions": [],
				"components": [],
				"externalId": issue["id"],
				"history": [],
				"customFieldValues": [],
				"attachments": []
			}
			project_id = issue["project"]["id"]
			for jira_project in jira_projects:
				if jira_project["id"] == project_id:
					jira_project["issues"].append(issue_info)
					break
			progress.update(task_id, advance=1)
	except Exception as err:
		print(BOLD + "Error: " + END + f"{err}")
	return jira_projects

def process_users(input_file, progress, task_id):
	"""
	Processing users.

	Args:
		input_file (str): The file, path and/or prefix that should be take as input.
		progress (Progress):
		trask_id (id): Id of the current task.
	"""
	total = 0
	try:
		if INPUT_MULTIPLE_FILE:
			input_file += "users.json"

		with open(input_file, 'r') as file:
			data = json.load(file)

		if isinstance(data, dict) and "users" in data:
			users = data["users"]
		elif isinstance(data, list):
			users = data
		else:
			raise ValueError("Unexpected input format. Expected a list or an object with a 'users' key.")

		total = len(users)
		progress.update(task_id, total=total)

		jira_users = []
		for user in users:
			jira_user = {
				"name": f"{user['login']}",
				"groups": [],
				"email": user["mail"],
				"fullname": f"{user['firstname']} {user['lastname']}"
			}
			jira_users.append(jira_user)
			progress.update(task_id, advance=1)
	except Exception as err:
		print(BOLD + "Error: " + END + f"{err}")
	return jira_users

def process(input_file, output_file):
	"""
	Process every data and save it into JSON file(s).

	Args:
		input_file (str): The file, path and/or prefix that should be take as input.
		output_file (str): The file, path and/or prefix that should be take as output.
	"""

	process_todo = {
		"projects": process_projects,
		"users": process_users,
		# "time_entries": process_time_entries,
		# "news": process_news,
	}

	consolidated_data = {}

	with Progress(
		SpinnerColumn(),
		TextColumn("[bold blue]{task.description}"),
		BarColumn(),
		"[progress.percentage]{task.percentage:>3.0f}%",
		TimeElapsedColumn(),
	) as progress:
		for key, process_function in process_todo.items():
			task_id = progress.add_task(f"Processing {key}", total=None)
			data = process_function(input_file, progress, task_id)
			consolidated_data[key] = data

	if consolidated_data:
		cleaned_path = os.path.dirname(output_file)
		if cleaned_path:
			os.makedirs(cleaned_path, exist_ok=True)
			print("Path " + BOLD + f"{cleaned_path}/" + END + " has been created")

		if OUTPUT_SINGLE_FILE:
			if AUTO:
				split_and_save(consolidated_data, output_file)
				print("All data has been saved")
			else:
				with open(output_file, "w", encoding="utf-8") as file:
					json.dump(consolidated_data, file, indent=4, ensure_ascii=False)
				os.chmod(output_file, 0o777)
				print("All data saved to " + BOLD + f"{output_file}" + END)
		else:
			to_save = {
				"projects",
				"users",
				# "time_entries",
				# "news"
			}
			for key in to_save:
				if AUTO:
					split_and_save(consolidated_data[key], output_file, key)
					print("All of " + BOLD + f"{key}" + END + " data has been saved")
				else:
					with open(output_file + key + '.json', "w", encoding="utf-8") as file:
						json.dump(consolidated_data[key], file, indent=4, ensure_ascii=False)
					os.chmod(output_file + key + '.json', 0o777)
					print("Data has been saved to " + BOLD + f"{output_file + key + '.json'}" + END)
	else:
		print(BOLD + "Error:\n" + END + "\tData fetching failed. No data was saved.")

def split_and_save(data, base_filename, key=None):
	"""
	Split any dictionary or list containing lists into multiple JSON files, ensuring each file
	does not exceed 1500 lines.

	Args:
		data (dict or list): The data to be split and saved.
		base_filename (str): The base filename for the split files.
	"""

	if isinstance(data, list):
		data = {key: data}

	part = 1
	current_chunk = {}
	current_line_count = 0

	list_keys = {key: value for key, value in data.items() if isinstance(value, list)}

	if not list_keys:
		return

	for key, values in list_keys.items():
		for item in values:
			chunk_data = {key: [item]}
			chunk_lines = len(json.dumps(chunk_data, indent=4, ensure_ascii=False).splitlines()) - 4

			if current_line_count + chunk_lines > int(AUTO_INDENT):
				if current_chunk:
					save_chunk(current_chunk, base_filename, part, key)
					part += 1
				current_chunk = {key: [item]}
				current_line_count = chunk_lines
			else:
				if key in current_chunk:
					current_chunk[key].append(item)
				else:
					current_chunk[key] = [item]
				current_line_count += chunk_lines

	if current_chunk:
		save_chunk(current_chunk, base_filename, part, key)

def save_chunk(chunk, base_filename, part, key):
	"""
	Save a chunk of data to a file.

	Args:
		chunk (dict): The chunk of data to save.
		base_filename (str): The base filename.
		part (int): The part number.
	"""
	base_filename = base_filename.removesuffix('.json')
	if OUTPUT_MULTIPLE_FILE:
		base_filename = f"{base_filename}{key}"
	filename = f"{base_filename}_part{part}.json"
	with open(filename, "w", encoding="utf-8") as file:
		json.dump(chunk, file, indent=4, ensure_ascii=False)
	os.chmod(filename, 0o777)
	print("Chunk saved to " + BOLD + f"{filename}" + END)

if __name__ == "__main__":
	input_file = 'redmine_data.json'
	output_file = 'jira_data.json'
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:a",["help", "single-input-file=", "single-output-file=", "multiple-input-files=", "multiple-output-files=", "auto="])
	except getopt.GetoptError:
		print(f"\x1B[1mUnhandle option/argument\x1B[0m (wrong option or missing required argument)\n{TXT_USAGE}")
		sys.exit(1)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(f"{TXT_USAGE}\n{TXT_HELP}")
			sys.exit(0)
		elif opt in ("-a", "--auto"):
			AUTO = True
			if arg:
				AUTO_INDENT = arg
		elif opt in ("-i", "--single-input-file"):
			if INPUT_MULTIPLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use single file input option while using multiple file option input too.\n{TXT_USAGE}")
				sys.exit(1)
			input_file = arg
			INPUT_SINGLE_FILE = True
		elif opt in ("-o", "--single-output-file"):
			if OUTPUT_MULTIPLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use single file output option while using multiple file option output too.\n{TXT_USAGE}")
				sys.exit(1)
			output_file = arg
			OUTPUT_SINGLE_FILE = True
		elif opt in ("--multiple-input-files"):
			if INPUT_SINGLE_FILE:
				print(f"\x1B[1mError:\x1B[0m You can not use multiple file input option while using single file input option too.\n{TXT_USAGE}")
				sys.exit(1)
			input_file = ''
			if arg:
				input_file = arg.removesuffix('.json')
			INPUT_MULTIPLE_FILE = True
		elif opt in ("--multiple-output-files"):
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
	process(input_file, output_file)
