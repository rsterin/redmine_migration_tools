from srcs_extraction import logger

endpoints = {
	"projects": "/projects.json",
	"issues": "/issues.json",
	"users": "/users.json",
	"time_entries": "/time_entries.json",
	"news": "/news.json"
}

def add_custom_endpoint(endpoint):
	"""
	Add a custom endpoint dynamically.

	Args:
		endpoint (list): List of endpoint to add to the default one.
	"""
	try:
		original_endpoint = endpoint
		endpoint = endpoint.removeprefix("/").removesuffix(".json")
		endpoints[endpoint] = f"/{endpoint}.json"
		logger.info(f"Custom endpoint '{original_endpoint}' added as '{endpoints[endpoint]}'.")
	except Exception as e:
		logger.error(f"Failed to add custom endpoint '{endpoint}': {e}")
		raise
