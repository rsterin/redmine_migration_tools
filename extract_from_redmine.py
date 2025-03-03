import sys
from srcs_extraction import config, cli, endpoints, fetcher, logger

def main():
	args = cli.parse_args(sys.argv[1:])

	logger.info(f"Parsed arguments: {args}")

	config.BASE_URL = args.get("url", config.BASE_URL)
	config.HEADERS = {"X-Redmine-API-Key": args["api_key"]}

	output_file = args.get("output", "outputs/redmine_data.json")
	config.SINGLE_FILE = False if args["multiple_files"] else True
	config.MULTIPLE_FILE = args["multiple_files"]

	logger.info(f"Configuration: BASE_URL={config.BASE_URL}, output_file={output_file}, "
				f"SINGLE_FILE={config.SINGLE_FILE}, MULTIPLE_FILE={config.MULTIPLE_FILE}")

	for endpoint in args.get("endpoints", []):
		endpoints.add_custom_endpoint(endpoint)
		logger.info(f"Custom endpoint added: {endpoint}")

	try:
		fetcher.fetch_all_data(output_file)
		logger.info("Data fetching completed successfully.")
	except Exception as e:
		logger.error(f"Error occurred during data fetching: {e}")

if __name__ == "__main__":
	logger.info("Script started")
	try:
		main()
	except Exception as e:
		logger.error(f"Script execution failed: {e}")
