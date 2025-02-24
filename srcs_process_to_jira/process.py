import json, os, isodate
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from srcs_process_to_jira import config, logger, save
from datetime import timedelta

def process_projects(input_file, progress, task_id, data):
	"""
	Processes projects and issues from the input file.

	Args:
		input_file (str): The file, path, and/or prefix that should be taken as input.
		progress (Progress): Rich progress object for displaying progress.
		task_id (int): ID of the current task.
		data (dict): Dictionary that contains a list of users.

	Returns:
		list: List of processed JIRA projects.
	"""
	logger.info("Starting to process projects and issues.")
	STATUS_MAPPING = {
		"Resolved": "Closed",
		"Feedback": "Closed",
		"In Progress": "In Progress",
		"New": "Open"
	}

	def map_status(status):
		return STATUS_MAPPING.get(status, "Open")

	def convert_hours_to_iso_duration(hours):
		"""
		Converts decimal hours to ISO 8601 duration format (e.g., PT1H50M).

		Args:
			hours (str): Number of hours to convert.

		Returns:
			str: Converted hours to ISO 8601.
		"""
		td = timedelta(hours=hours)
		return isodate.duration_isoformat(td)

	total = 0
	try:
		if config.INPUT_MULTIPLE_FILE:
			projects_input_file = input_file + "projects.json"
			issues_input_file =  input_file + "issues.json"
			time_input_file =  input_file + "time_entries.json"
			logger.info(f"Loading projects from {projects_input_file}.")
			with open(projects_input_file, 'r') as file:
				projects = json.load(file)
			logger.info(f"Loading issues from {issues_input_file}.")
			with open(issues_input_file, 'r') as file:
				issues = json.load(file)
			logger.info(f"Loading time entries from {time_input_file}.")
			with open(time_input_file, 'r') as file:
				time_entries = json.load(file)
		else:
			logger.info(f"Loading data from {input_file}.")
			with open(input_file, 'r') as file:
				data = json.load(file)
			if isinstance(data, dict) and "projects" in data and "issues" in data:
				projects = data["projects"]
				issues = data["issues"]
				time_entries = data["time_entries"]
			else:
				raise ValueError("Unexpected input format. Expected a list or an object with a 'projects' and/or 'issues' key.")

		total = len(projects) + len(issues) + len(time_entries)
		logger.info(f"Total items to process: {total}.")
		progress.update(task_id, total=total)

		jira_projects = []
		allocated_keys = set()

		task_project = progress.add_task("↪ Formatting projects", total=len(projects))
		task_issues = progress.add_task("↪ Formatting issues", total=len(issues))
		task_time_entries = progress.add_task("↪ Formatting time_entries", total=len(time_entries))

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
			progress.update(task_project, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed project: {project['name']}")

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
				"attachments": [],
				"worklogs": []
			}
			assigned_to = issue.get("assigned_to")
			if assigned_to:
				assignee_id = assigned_to["id"]
				for user in data["users"]:
					if user["id"] == assignee_id:
						issue_info["assignee"] = user["name"]
						break

			project_id = issue["project"]["id"]
			for jira_project in jira_projects:
				if jira_project["id"] == project_id:
					jira_project["issues"].append(issue_info)
					break

			progress.update(task_issues, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed issue: {issue['subject']}")

		for time_entry in time_entries:
			issue_id = time_entry["issue"]["id"]
			worklog = {
				"author": time_entry["user"]["name"],
				"comment": time_entry.get("comments", "No comment provided"),
				"startDate": time_entry["spent_on"],
				"timeSpent": convert_hours_to_iso_duration(time_entry["hours"]),
			}
			for jira_project in jira_projects:
				for jira_issue in jira_project["issues"]:
					if jira_issue["externalId"] == issue_id:
						if "worklogs" not in jira_issue:
							jira_issue["worklogs"] = []
						jira_issue["worklogs"].append(worklog)
						break
			progress.update(task_time_entries, advance=1)
			progress.update(task_id, advance=1)
			logger.info(f"Processed time entry for issue ID: {issue_id}")

	except Exception as err:
		logger.error(f"Error processing projects: {err}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
	return jira_projects

def process_users(input_file, progress, task_id, data):
	"""
	Processes users from the input file.

	Args:
		input_file (str): The file, path, and/or prefix that should be taken as input.
		progress (Progress): Rich progress object for displaying progress.
		task_id (int): ID of the current task.

	Returns:
		list: List of processed JIRA users.
	"""
	logger.info("Starting to process users.")
	total = 0
	try:
		if config.INPUT_MULTIPLE_FILE:
			input_file += "users.json"

		logger.info(f"Loading users from {input_file}.")
		with open(input_file, 'r') as file:
			data = json.load(file)

		if isinstance(data, dict) and "users" in data:
			users = data["users"]
		elif isinstance(data, list):
			users = data
		else:
			raise ValueError("Unexpected input format. Expected a list or an object with a 'users' key.")

		total = len(users)
		logger.info(f"Total users to process: {total}.")
		progress.update(task_id, total=total)

		jira_users = []
		for user in users:
			jira_user = {
				"id": user["id"],
				"name": f"{user['login']}",
				"groups": [],
				"email": user["mail"],
				"fullname": f"{user['firstname']} {user['lastname']}"
			}
			jira_users.append(jira_user)
			progress.update(task_id, advance=1)
			logger.info(f"Processed user: {user['login']}")
	except Exception as err:
		logger.error(f"Error processing users: {err}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
	return jira_users

def process_links(input_file, progress, task_id, data):
	"""
	Processes links from the input file.

	Args:
		input_file (str): The file, path, and/or prefix that should be taken as input.
		progress (Progress): Rich progress object for displaying progress.
		task_id (int): ID of the current task.

	Returns:
		list: List of processed JIRA links.
	"""
	logger.info("Starting to process links.")
	total = 0
	jira_links = []
	try:
		if config.INPUT_MULTIPLE_FILE:
			input_file += "issues.json"

		logger.info(f"Loading users from {input_file}.")
		with open(input_file, 'r') as file:
			data = json.load(file)

		if isinstance(data, dict) and "issues" in data:
			issues = data["issues"]
		elif isinstance(data, list):
			issues = data
		else:
			raise ValueError("Unexpected input format. Expected a list or an object with a 'relations' key.")

		for issue in issues:
			if isinstance(issue, dict) and "relations" in issue:
				relations_data = issue["relations"]
				if relations_data and "relations" in relations_data:
					relations = relations_data["relations"]
				else:
					relations = []
			else:
				raise ValueError("Unexpected input format. Expected a list or an object with a 'relations' key.")

			total += len(relations)

		logger.info(f"Total links to process: {total}.")
		progress.update(task_id, total=total)

		for issue in issues:
			if isinstance(issue, dict) and "relations" in issue:
				relations_data = issue["relations"]
				if relations_data and "relations" in relations_data:
					relations = relations_data["relations"]
				else:
					relations = []
			else:
				raise ValueError("Unexpected input format. Expected a list or an object with a 'relations' key.")

			for relation in relations:
				jira_link = {
					"sourceId": relation["issue_id"],
					"destinationId": relation["issue_to_id"],
					"name": relation["relation_type"]
				}
				jira_links.append(jira_link)
				progress.update(task_id, advance=1)
				logger.info(f"Processed link from {relation['issue_id']} to {relation['issue_to_id']}")
	except Exception as err:
		logger.error(f"Error processing links: {err} {issue}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
	return jira_links

def process(input_file, output_file):
	"""
	Processes all data and saves it into JSON file(s).

	Args:
		input_file (str): The file, path, and/or prefix that should be taken as input.
		output_file (str): The file, path, and/or prefix that should be taken as output.

	Returns:
		None
	"""
	logger.info("Starting to process all data.")
	process_todo = {
		"users": process_users,
		"projects": process_projects,
		"links": process_links
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
		for key, process_function in process_todo.items():
			task_id = progress.add_task(f"Processing {key}", total=None)
			data = process_function(input_file, progress, task_id, consolidated_data)
			consolidated_data[key] = data
			logger.info(f"Completed processing {key}.")

		if consolidated_data:
			cleaned_path = os.path.dirname(output_file)
			if cleaned_path:
				os.makedirs(cleaned_path, exist_ok=True)
				logger.info(f"Path {cleaned_path}/ has been created successfully.")
				print("Path " + config.BOLD + f"{cleaned_path}/" + config.END + " has been created")

			if config.OUTPUT_SINGLE_FILE:
				task_save = progress.add_task("Saving", total=1)
				logger.info("Saving data to a single output file.")
				if config.AUTO:
					try:
						save.split_and_save(consolidated_data, output_file, progress, task_save)
						logger.info("Data has been successfully split and saved in auto mode.")
						print("All data has been saved")
					except Exception as e:
						logger.error(f"Error while splitting and saving data: {e}", exc_info=True)
						print(config.BOLD + "Error:\n" + config.END + f"{e}")
				else:
					try:
						task_subsave = progress.add_task(f"↪ Saving into {output_file}", total=1)
						with open(output_file, "w", encoding="utf-8") as file:
							json.dump(consolidated_data, file, indent=4, ensure_ascii=False)
						os.chmod(output_file, 0o777)
						progress.update(task_subsave, advance=1)
						progress.update(task_save, advance=1)
						logger.info(f"All data saved to {output_file}.")
						print("All data saved to " + config.BOLD + f"{output_file}" + config.END)
					except Exception as e:
						logger.error(f"Error while saving data to {output_file}: {e}", exc_info=True)
						print(config.BOLD + "Error:\n" + config.END + f"{e}")
			else:
				to_save = {
					"projects",
					"users",
					"links"
				}
				logger.info("Saving data to separate files.")
				total = 1
				task_save = progress.add_task("Saving", total=total)
				for key in to_save:
					progress.update(task_save, total=total)
					if config.AUTO:
						try:
							save.split_and_save(consolidated_data[key], output_file, progress, task_save, key)
							logger.info(f"Data for {key} successfully split and saved in auto mode.")
							print("All of " + config.BOLD + f"{key}" + config.END + " data has been saved")
						except Exception as e:
							logger.error(f"Error while saving {key} data: {e}", exc_info=True)
							print(config.BOLD + "Error:\n" + config.END + f"{e}")
					else:
						try:
							task_subsave = progress.add_task(f"↪ Saving into {output_file + key + '.json'}", total=1)
							with open(output_file + key + '.json', "w", encoding="utf-8") as file:
								json.dump(consolidated_data[key], file, indent=4, ensure_ascii=False)
							os.chmod(output_file + key + '.json', 0o777)
							progress.update(task_subsave, advance=1)
							progress.update(task_save, advance=1)
							logger.info(f"Data for {key} saved to {output_file + key + '.json'}.")
							print("Data has been saved to " + config.BOLD + f"{output_file + key + '.json'}" + config.END)
						except Exception as e:
							logger.error(f"Error while saving {key} data to {output_file + key + '.json'}: {e}", exc_info=True)
							print(config.BOLD + "Error:\n" + config.END + f"{e}")
					total += 1
		else:
			logger.error("Data processing failed. No data to save.")
			print(config.BOLD + "Error:\n" + config.END + "\tData processing failed. No data was saved.")

