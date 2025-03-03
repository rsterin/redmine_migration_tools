import sys
from srcs_process_to_jira import config, cli, logger, process

def main():
	args = cli.parse_args(sys.argv[1:])

	logger.info(f"Parsed arguments: {args}")

	input_file = args.get("input_file", "outputs/redmine_data.json")
	output_file = args.get("output_file", "outputs/jira_data.json")
	config.INPUT_SINGLE_FILE = False if args["multiple_files_input"] else True
	config.INPUT_MULTIPLE_FILE = args["multiple_files_input"]
	config.OUTPUT_SINGLE_FILE = False if args["multiple_files_output"] else True
	config.OUTPUT_MULTIPLE_FILE = args["multiple_files_output"]

	config.AUTO = args["auto"]
	config.AUTO_INDENT = args["auto_indent"]

	logger.info(f"Configuration: input_file={input_file}, output_file={output_file}, "
				f"SINGLE_FILE_INPUT={config.INPUT_SINGLE_FILE}, MULTIPLE_FILE_INPUT={config.INPUT_MULTIPLE_FILE}, "
				f"SINGLE_FILE_OUTPUT={config.OUTPUT_SINGLE_FILE}, MULTIPLE_FILE_OUTPUT={config.OUTPUT_MULTIPLE_FILE}, "
				f"AUTO={config.AUTO}, AUTO_INDENT={config.AUTO_INDENT}")

	try:
		process.process(input_file, output_file)
		logger.info("Data processing completed successfully.")
	except Exception as e:
		logger.error(f"Error occurred during data processing: {e}")

if __name__ == "__main__":
	logger.info("Script started")
	try:
		main()
	except Exception as e:
		logger.error(f"Script execution failed: {e}")
