import json
import os
from srcs_process_to_jira import config, logger

def split_and_save(data, base_filename, progress, task_id, key=None):
	"""
	Split any dictionary or list containing lists into multiple JSON files, ensuring each file does not exceed a specified number of lines.

	Args:
		data (dict or list): The data to be split and saved.
		base_filename (str): The base filename for the split files.
		progress (Progress): The progress object to update the task progress.
		task_id (int): The ID of the task to update progress.
		key (str, optional): The key to use for the data if it is a list. Defaults to None.

	Returns:
		None
	"""
	tmp = key
	try:
		logger.info("Starting split_and_save function.")

		if isinstance(data, list):
			logger.debug("Input data is a list, converting to dictionary.")
			data = {key: data}

		part = 0
		current_chunk = {}
		current_line_count = 0

		list_keys = {key: value for key, value in data.items() if isinstance(value, list)}

		if not list_keys:
			logger.warning("No lists found in the provided data to split.")
			return

		for key, values in list_keys.items():
			logger.info(f"Counting key: {key}")
			for item in values:
				chunk_data = {key: [item]}
				chunk_lines = len(json.dumps(chunk_data, indent=4, ensure_ascii=False).splitlines()) - 4

				if current_line_count + chunk_lines > int(config.AUTO_INDENT):
					if current_chunk:
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
			part += 1

		if tmp:
			task_save = progress.add_task(f"↪ Saving {key} into file of {config.AUTO_INDENT} line each", total=part)
		else:
			task_save = progress.add_task(f"↪ Saving into file of {config.AUTO_INDENT} line each", total=part)

		part = 1
		current_chunk = {}
		current_line_count = 0

		for key, values in list_keys.items():
			logger.info(f"Processing key: {key}")
			for item in values:
				chunk_data = {key: [item]}
				chunk_lines = len(json.dumps(chunk_data, indent=4, ensure_ascii=False).splitlines()) - 4

				if current_line_count + chunk_lines > int(config.AUTO_INDENT):
					if current_chunk:
						logger.debug(f"Saving chunk for part {part}.")
						save_chunk(current_chunk, base_filename, part, key)
						part += 1
						progress.update(task_save, advance=1)
					current_chunk = {key: [item]}
					current_line_count = chunk_lines
				else:
					if key in current_chunk:
						current_chunk[key].append(item)
					else:
						current_chunk[key] = [item]
					current_line_count += chunk_lines

		if current_chunk:
			logger.debug(f"Saving final chunk for part {part}.")
			save_chunk(current_chunk, base_filename, part, key)
			progress.update(task_save, advance=1)

		progress.update(task_id, advance=1)
		logger.info("Completed split_and_save function successfully.")
	except Exception as e:
		logger.error(f"An error occurred in split_and_save: {str(e)}", exc_info=True)

def save_chunk(chunk, base_filename, part, key):
	"""
	Save a chunk of data to a file.

	Args:
		chunk (dict): The chunk of data to save.
		base_filename (str): The base filename.
		part (int): The part number.
		key (str): The key associated with the chunk of data.

	Returns:
		None
	"""
	try:
		logger.debug("Starting save_chunk function.")

		base_filename = base_filename.removesuffix('.json')
		if config.OUTPUT_MULTIPLE_FILE:
			base_filename = f"{base_filename}{key}"
		filename = f"{base_filename}_part{part}.json"

		with open(filename, "w", encoding="utf-8") as file:
			json.dump(chunk, file, indent=4, ensure_ascii=False)
		os.chmod(filename, 0o777)
		logger.info(f"Chunk saved to {filename}")
	except Exception as e:
		logger.error(f"An error occurred in save_chunk: {str(e)}", exc_info=True)
