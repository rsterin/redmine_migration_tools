import sys
from srcs_process_to_spreadsheet import config, cli, logger, process

def main():
	args = cli.parse_args(sys.argv[1:])

	logger.info(f"Parsed arguments: {args}")

	input_file = args.get("input_file", "outputs/redmine_data.json")
	output_path = args.get("output_path", "outputs/")
	config.INPUT_SINGLE_FILE = False if args["multiple_files_input"] else True
	config.INPUT_MULTIPLE_FILE = args["multiple_files_input"]

	logger.info(f"Configuration: input_file={input_file}, output_path={output_path}, "
				f"SINGLE_FILE_INPUT={config.INPUT_SINGLE_FILE}, MULTIPLE_FILE_INPUT={config.INPUT_MULTIPLE_FILE}")
	try:
		process.process(input_file, output_path)
		logger.info("Data processing completed successfully.")
	except Exception as e:
		logger.error(f"Error occurred during data processing: {e}")

if __name__ == "__main__":
	logger.info("Script started")
	try:
		main()
	except Exception as e:
		logger.error(f"Script execution failed: {e}")
