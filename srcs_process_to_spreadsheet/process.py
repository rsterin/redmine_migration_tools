import json, os
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from srcs_process_to_spreadsheet import config, logger, save

def process_projects(input_file, progress, task_id, consolidated_data):
	"""
	Process projects, issues, and time entries from the input file(s).

	Args:
		input_file (str): The file, path and/or prefix that should be taken as input.
		progress (Progress): The progress bar object.
		task_id (int): Id of the current task.
		consolidated_data (dict): Dict that contains a list of projects.

	Returns:
		list: Processed projects.
	"""

	total = 0
	try:
		if config.INPUT_MULTIPLE_FILE:
			projects_input_file = input_file + "projects.json"
			issues_input_file =  input_file + "issues.json"
			time_entries_input_file =  input_file + "time_entries.json"
			logger.info(f"Loading projects from {projects_input_file}.")
			with open(projects_input_file, 'r') as file:
				projects = json.load(file)
			logger.info(f"Loading issues from {issues_input_file}.")
			with open(issues_input_file, 'r') as file:
				issues = json.load(file)
			logger.info(f"Loading time entries from {time_entries_input_file}.")
			with open(time_entries_input_file, 'r') as file:
				time_entries = json.load(file)
		else:
			logger.info(f"Loading data from {input_file}.")
			with open(input_file, 'r') as file:
				data = json.load(file)
			logger.debug(f"Loaded data: {data}")
			if isinstance(data, dict) and "projects" in data and "issues" in data:
				projects = data["projects"]
				issues = data["issues"]
				time_entries = data["time_entries"]
			else:
				raise ValueError("Unexpected input format. Expected a list or an object with a 'projects' and/or 'issues' key.")

		total = len(projects) + len(issues) + len(time_entries)
		logger.info(f"Total items to process: {total}.")
		progress.update(task_id, total=total)

		processed_projects = []

		task_project = progress.add_task("↪ Formatting projects", total=len(projects))
		task_issues = progress.add_task("↪ Formatting issues", total=len(issues))
		task_time_entries = progress.add_task("↪ Formatting time entries", total=len(time_entries))

		for project in projects:
			project["issues"] = []
			processed_projects.append(project)
			progress.update(task_project, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed project: {project['name']}")

		for issue in issues:
			project_id = issue["project"]["id"]
			for project in processed_projects:
				if project["id"] == project_id:
					issue["time_entries"] = []
					project["issues"].append(issue)
					break

			progress.update(task_issues, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed issue: {issue['subject']}")

		for time_entry in time_entries:
			issue_id = time_entry["issue"]["id"]
			for project in processed_projects:
				for issue in project.get("issues", []):
					if issue["id"] == issue_id:
						issue["time_entries"].append(time_entry)
						break
			progress.update(task_time_entries, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed time entry for issue ID: {issue_id}")

	except Exception as err:
		logger.error(f"Error processing projects: {err}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
	return processed_projects

def process(input_file, output_path):
	"""
	Process all data and save it into spreadsheet file(s).

	Args:
		input_file (str): The file, path and/or prefix that should be taken as input.
		output_path (str): The path and/or prefix that should be taken as output.
	"""
	logger.info("Starting to process all data.")
	process_functions = {
		"projects": process_projects
	}

	consolidated_data = {}

	with Progress(
		SpinnerColumn(),
		TextColumn("[bold blue]{task.description}"),
		BarColumn(),
		"[progress.percentage]{task.completed}/{task.total}",
		"[progress.percentage]{task.percentage:>3.0f}%",
		TimeElapsedColumn(),
	) as progress:
		for key, process_function in process_functions.items():
			task_id = progress.add_task(f"Processing {key}", total=None)
			data = process_function(input_file, progress, task_id, consolidated_data)
			consolidated_data[key] = data
			logger.info(f"Completed processing {key}.")

		if consolidated_data:
			cleaned_path = os.path.dirname(output_path)
			if cleaned_path:
				os.makedirs(cleaned_path, exist_ok=True)
				logger.info(f"Path {cleaned_path}/ has been created successfully.")
				print("Path " + config.BOLD + f"{cleaned_path}/" + config.END + " has been created")

			save.export_projects(consolidated_data["projects"], cleaned_path)
		else:
			logger.error("Data processing failed. No data to save.")
			print(config.BOLD + "Error:\n" + config.END + "\tData processing failed. No data was saved.")
