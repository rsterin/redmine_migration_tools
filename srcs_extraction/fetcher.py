import os
import json
import requests
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from srcs_extraction import config, endpoints, logger

def fetch_data(endpoint, params=None):
	"""
	Fetch data from an endpoint using parameters.

	Args:
		endpoint (str): The endpoint to fetch data from.
		params (dict, optional): Dictionary of parameters, e.g., offset and limit. Defaults to None.

	Returns:
		dict: The response data in JSON format, or None if an error occurs.
	"""
	url = f"{config.BASE_URL}{endpoint}"
	try:
		logger.info(f"Fetching data from {url} with params {params}")
		response = requests.get(url, headers=config.HEADERS, params=params)
		response.raise_for_status()
		logger.info(f"Data fetched successfully from {url}")
		return response.json()
	except requests.exceptions.HTTPError as http_err:
		if response.status_code == 403:
			logger.warning(f"Failed to fetch data from {url}: Unauthorized access")
			print(config.BOLD + "Warning: " + config.END + f"Unauthorized access to \"{url}\" (closed project?)")
		else:
			logger.error(f"HTTP error occurred: {http_err}")
			print(config.BOLD + "Error: " + config.END + f"{http_err}")
		return None
	except Exception as err:
		logger.error(f"Failed to fetch data from {url}: {err}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
		return None

def fetch_endpoint_data(endpoint, progress, task_id):
	"""
	Fetch all data from a given endpoint.

	Args:
		endpoint (str): The endpoint to fetch data from.
		progress (Progress): The progress object to update the task progress.
		task_id (TaskID): The ID of the task to update progress.

	Returns:
		dict: All of the fetched data.
	"""
	all_data = []
	offset = 0
	limit = 100
	total = None

	logger.info(f"Starting fetch for endpoint: {endpoint}")
	key = endpoint.strip("/").split(".")[0]

	while True:
		params = {"offset": offset, "limit": limit}
		data = fetch_data(endpoint, params)
		if data:
			if total is None and "total_count" in data:
				total = data["total_count"]
				if key in ["projects", "issues"]:
					total *= 7
				progress.update(task_id, total=total)

			fetched_data = data.get(key, [])
			all_data.extend(fetched_data)
			progress.update(task_id, advance=len(fetched_data))

			if len(fetched_data) < limit:
				break
			offset += limit
		else:
			logger.warning(f"No data returned for {endpoint} at offset {offset}")
			break

	logger.info(f"Completed fetch for endpoint: {endpoint}, total records: {len(all_data)}")
	return all_data

def fetch_project_data(project_id, progress, task_id, output_file):
	"""
	Fetch all related data for a given project, including downloading files.

	Args:
		project_id (int): The ID of the source project.
		progress (Progress): The progress object to update the task progress.
		task_id (TaskID): The ID of the task to update progress.
		output_file (str): The directory to store downloaded files.

	Returns:
		dict: All of the associated data from the project.
	"""
	offset = 0
	limit = 100
	params = {"offset": offset, "limit": limit}

	logger.info(f"Fetching project-related data for project ID: {project_id}")

	task_memberships = progress.add_task("↪ Fetching memberships", total=None)
	task_versions = progress.add_task("↪ Fetching versions", total=None)
	task_issue_categories = progress.add_task("↪ Fetching issues categories", total=None)
	task_files = progress.add_task("↪ Fetching files", total=None)
	task_wikis = progress.add_task("↪ Fetching wikis", total=None)

	project_data = {
		"memberships": fetch_data(f"/projects/{project_id}/memberships.json", params),
		"versions": fetch_data(f"/projects/{project_id}/versions.json", params),
		"issue_categories": fetch_data(f"/projects/{project_id}/issue_categories.json", params),
		"files": fetch_data(f"/projects/{project_id}/files.json", params),
	}
	progress.update(task_id, advance=4)
	progress.update(task_memberships, total=len(project_data["memberships"]) if project_data["memberships"] else 0, advance=len(project_data["memberships"]) if project_data["memberships"] else 0)
	progress.update(task_versions, total=len(project_data["versions"]) if project_data["versions"] else 0, advance=len(project_data["versions"]) if project_data["versions"] else 0)
	progress.update(task_issue_categories, total=len(project_data["issue_categories"]) if project_data["issue_categories"] else 0, advance=len(project_data["issue_categories"]) if project_data["issue_categories"] else 0)
	progress.update(task_files, total=len(project_data["files"]) + 1 if project_data["files"] else 0, advance=1 if project_data["files"] else 0)
	logger.info(f"Completed fetching project data for project ID: {project_id}")

	if "files" in project_data and isinstance(project_data["files"], dict):
		logger.info(f"Files data: {project_data['files']}")
		files_data = project_data.get("files")
		files = files_data["files"]
		for file in files:
			logger.debug(f"{file}")
			content_url = file["content_url"]
			if not content_url:
				logger.warning(f"File {file} does not have a 'content_url'.")
			else:
				cleaned_path = os.path.join(os.path.dirname(output_file), "attachements", str(project_id))
				if cleaned_path:
					os.makedirs(cleaned_path, exist_ok=True)
					logger.info(f"Created directory path: {cleaned_path}")
				file_name = file["filename"]
				file_path = os.path.join(cleaned_path, file_name)
				try:
					logger.info(f"Downloading file from {content_url}")
					file_response = requests.get(content_url, headers=config.HEADERS)
					if file_response.status_code == 200:
						with open(file_path, 'wb') as f:
							f.write(file_response.content)
						logger.info(f"Successfully downloaded {file_name}")
						progress.update(task_files, advance=1)
					else:
						logger.error(f"Failed to download file from {content_url}: Status Code {file_response.status_code}")
				except Exception as e:
					logger.error(f"Error downloading file from {content_url}: {e}")
	progress.update(task_id, advance=1)
	progress.remove_task(task_memberships)
	progress.remove_task(task_versions)
	progress.remove_task(task_issue_categories)
	progress.remove_task(task_files)

	try:
		logger.info(f"Fetching Wiki index for project ID: {project_id}")
		wiki_index = fetch_data(f"/projects/{project_id}/wiki/index.json", params)
		project_data["wiki"] = {"pages": []}

		if wiki_index and "wiki_pages" in wiki_index:
			progress.update(task_wikis, total=len(wiki_index["wiki_pages"]))
			for page in wiki_index["wiki_pages"]:
				page_title = page.get("title")
				if page_title:
					try:
						logger.info(f"Fetching Wiki page: {page_title}")
						page_content = fetch_data(f"/projects/{project_id}/wiki/{page_title}.json", params)
						project_data["wiki"]["pages"].append(page_content)
						progress.update(task_wikis, advance=1)
					except Exception as e:
						logger.error(f"Error fetching Wiki page {page_title} for project ID {project_id}: {e}")
		else:
			logger.warning(f"No Wiki pages found for project ID: {project_id}")
	except Exception as e:
		logger.error(f"Error fetching Wiki index for project ID {project_id}: {e}")
		project_data["wiki"] = None
	progress.update(task_id, advance=1)
	progress.remove_task(task_wikis)
	return project_data


def fetch_issue_data(issue_id, progress, task_id):
	"""
	Fetch all related data for a given issue.

	Args:
		issue_id (int): The ID of the source issue.
		progress (Progress): The progress object to update the task progress.
		task_id (TaskID): The ID of the task to update progress.

	Returns:
		dict: All of the associated data from the issue.
	"""
	offset = 0
	limit = 100
	params = {"offset": offset, "limit": limit}

	task_relations = progress.add_task("↪ Fetching relations", total=None)

	logger.info(f"Fetching issue-related data for issue ID: {issue_id}")
	relations = fetch_data(f"/issues/{issue_id}/relations.json", params)
	progress.update(task_relations, total=len(relations) if relations else 0, advance=len(relations) if relations else 0)
	progress.update(task_id, advance=6)
	logger.info(f"Completed fetching issue data for issue ID: {issue_id}")
	progress.remove_task(task_relations)
	return {"relations": relations}

def fetch_all_data(output_file):
	"""
	Fetch all data from key endpoints and save it into JSON file(s).

	Args:
		output_file (str): The file, path, and/or prefix that should be used as output.

	Returns:
		None
	"""
	consolidated_data = {}

	with Progress(
		SpinnerColumn(),
		TextColumn("[bold blue]{task.description}"),
		BarColumn(),
		"[progress.percentage]{task.percentage:>3.0f}%",
		TimeElapsedColumn()
	) as progress:
		for key, endpoint in endpoints.endpoints.items():
			logger.info(f"Starting to fetch data for endpoint: {key}")
			task_id = progress.add_task(f"Fetching {key}", total=None)
			consolidated_data[key] = fetch_endpoint_data(endpoint, progress, task_id)

			if key == "projects":
				for project in consolidated_data["projects"]:
					project_data = fetch_project_data(project["id"], progress, task_id, output_file)
					project.update(project_data)

			if key == "issues":
				for issue in consolidated_data["issues"]:
					issue_data = fetch_issue_data(issue["id"], progress, task_id)
					issue.update(issue_data)

			logger.info(f"Completed fetching data for endpoint: {key}")
			save_data(output_file, consolidated_data)

def save_data(output_file, data):
	"""
	Save the extracted data to JSON files.

	Args:
		output_file (str): The file, path, and/or prefix that should be used as output.
		data (dict): All of the data that has been extracted.

	Returns:
		None
	"""
	if data:
		cleaned_path = os.path.dirname(output_file)
		if cleaned_path:
			os.makedirs(cleaned_path, exist_ok=True)
			logger.info(f"Created directory path: {cleaned_path}")

		if config.SINGLE_FILE:
			with open(output_file, "w", encoding="utf-8") as file:
				json.dump(data, file, indent=4, ensure_ascii=False)
			logger.info(f"All data saved to {output_file}")
		else:
			for key, value in data.items():
				file_path = f"{output_file}{key}.json"
				with open(file_path, "w", encoding="utf-8") as file:
					json.dump(value, file, indent=4, ensure_ascii=False)
				logger.info(f"Data for {key} saved to {file_path}")
	else:
		logger.error("No data fetched. No files were saved.")
