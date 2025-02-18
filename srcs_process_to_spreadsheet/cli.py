import getopt
import sys
from srcs_process_to_spreadsheet import config, logger

def parse_args(argv):
	"""
	Parse command-line arguments and return them as a dictionary.

	Args:
		argv (list): List of argument.

	Returns:
		dict: Parsed arguments as a dictionary.
	"""
	args = {
		"input_file": "outputs/redmine_data.json",
		"output_path": "outputs/",
		"single_file_input": False,
		"multiple_files_input": False
	}

	try:
		opts, _ = getopt.getopt(
			argv, "hi:o:",["help", "single-input-file=", "multiple-input-files=", "output-path="]
		)
	except getopt.GetoptError as e:
		logger.error(f"Argument parsing error: {e}")
		logger.info("Displaying usage information.")
		print(config.BOLD + "Error: " + config.END + str(e))
		print(config.TXT_USAGE)
		sys.exit(1)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			logger.info("Help requested. Displaying usage and help information.")
			print(config.TXT_USAGE + "\n" + config.TXT_HELP)
			sys.exit(0)
		elif opt in ("-i", "--single-input-file"):
			args["input_file"] = arg
			logger.debug(f"Single input file set to: {arg}")
		elif opt in ("--multiple-input-files"):
			args["multiple_files_input"] = True
			args["input_file"] = ''
			if arg:
				args["input_file"] = arg.removesuffix('.json')
			logger.debug(f"Multiple files input prefix set to: {args['input_file']}")
		elif opt in ("-o", "--output-path"):
			args["output_path"] = arg
			logger.debug(f"Single output path set to: {arg}")

	if (args["single_file_input"] and args["multiple_files_input"]):
		logger.error("Both single file and multiple files options set. Exiting.")
		print(config.BOLD + "Error: " + config.END + "You cannot use single file and multiple files options at the same time.")
		print(config.TXT_USAGE)
		sys.exit(2)

	logger.info("Arguments successfully parsed.")
	return args

