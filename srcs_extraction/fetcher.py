import os
import json
import requests
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from srcs_extraction import config, endpoints, logger

def fetch_data(endpoint, params=None):
	"""
	Fetch data from an endpoint using parameters.

	Args:
		endpoint (str): Endpoint to fetch.

	Returns:
		json: Response in JSON format.
	"""
	url = f"{config.BASE_URL}{endpoint}"
	try:
		logger.info(f"Fetching data from {url} with params {params}")
		response = requests.get(url, headers=config.HEADERS, params=params, timeout=10)
		response.raise_for_status()
		logger.info(f"Data fetched successfully from {url}")
		return response.json()
	except Exception as err:
		logger.error(f"Failed to fetch data from {url}: {err}")
		print(config.BOLD + "Error: " + config.END + f"{err}")
		return None

def fetch_endpoint_data(endpoint, progress, task_id):
	"""
	Fetch all data from a given endpoint.

	Args:
		endpoint (str): Endpoint to fetch.
		progress (Progress): Progress bar.
		task_id (TaskID): Id of the current task.

	Returns:
		dict: All of the fetched data.
	"""
	all_data = []
	offset = 0
	limit = 100
	total = None

	logger.info(f"Starting fetch for endpoint: {endpoint}")
	while True:
		params = {"offset": offset, "limit": limit}
		data = fetch_data(endpoint, params)
		if data:
			key = endpoint.strip("/").split(".")[0]
			if total is None and "total_count" in data:
				total = data["total_count"]
				if key in ["projects", "issues"]:
					total *= 7
				progress.update(task_id, total=total)

			all_data.extend(data.get(key, []))
			progress.update(task_id, advance=len(data.get(key, [])))

			if len(data.get(key, [])) < limit:
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
		project_id (int): Id of the source project.
		progress (Progress): Progress bar.
		task_id (TaskID): Id of the current task.
		output_file (str): Directory to store downloaded files.

	Returns:
		dict: All of the associated data from a project.
	"""
	logger.info(f"Fetching project-related data for project ID: {project_id}")
	project_data = {
		"memberships": fetch_data(f"/projects/{project_id}/memberships.json"),
		"versions": fetch_data(f"/projects/{project_id}/versions.json"),
		"issue_categories": fetch_data(f"/projects/{project_id}/issue_categories.json"),
		"files": fetch_data(f"/projects/{project_id}/files.json"),
	}
	progress.update(task_id, advance=4)
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
					else:
						logger.error(f"Failed to download file from {content_url}: Status Code {file_response.status_code}")
				except Exception as e:
					logger.error(f"Error downloading file from {content_url}: {e}")
	progress.update(task_id, advance=1)

	try:
		logger.info(f"Fetching Wiki index for project ID: {project_id}")
		wiki_index = fetch_data(f"/projects/{project_id}/wiki/index.json")
		project_data["wiki"] = {"pages": []}

		if wiki_index and "wiki_pages" in wiki_index:
			for page in wiki_index["wiki_pages"]:
				page_title = page.get("title")
				if page_title:
					try:
						logger.info(f"Fetching Wiki page: {page_title}")
						page_content = fetch_data(f"/projects/{project_id}/wiki/{page_title}.json")
						project_data["wiki"]["pages"].append(page_content)
					except Exception as e:
						logger.error(f"Error fetching Wiki page {page_title} for project ID {project_id}: {e}")
		else:
			logger.warning(f"No Wiki pages found for project ID: {project_id}")
	except Exception as e:
		logger.error(f"Error fetching Wiki index for project ID {project_id}: {e}")
		project_data["wiki"] = None
	progress.update(task_id, advance=1)
	return project_data


def fetch_issue_data(issue_id, progress, task_id):
	"""
	Fetch all related data for a given issue.

	Args:
		issue_id (int): Id of the source issue.
		progress (Progress): Progress bar.
		task_id (TaskID): Id of the current task.

	Returns:
		dict: All of the associated data from a issue.
	"""
	logger.info(f"Fetching issue-related data for issue ID: {issue_id}")
	relations = fetch_data(f"/issues/{issue_id}/relations.json")
	progress.update(task_id, advance=4)
	logger.info(f"Completed fetching issue data for issue ID: {issue_id}")
	return {"relations": relations}

def fetch_all_data(output_file):
	"""
	Fetch all data from key endpoints and save it into JSON file(s).

	Args:
		output_file (str): The file, path and/or prefix that should be take as output.
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
	Managing what to do with the extracted data.

	Args:
		output_file (str): The file, path and/or prefix that should be take as output.
		data (dict): All of the data that as been extracted.
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
				file_path = f"{output_file}_{key}.json"
				with open(file_path, "w", encoding="utf-8") as file:
					json.dump(value, file, indent=4, ensure_ascii=False)
				logger.info(f"Data for {key} saved to {file_path}")
	else:
		logger.error("No data fetched. No files were saved.")
