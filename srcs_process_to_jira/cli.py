import getopt
import sys
from srcs_process_to_jira import config, logger

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
		"output_file": "outputs/jira_data.json",
		"single_file_input": False,
		"multiple_files_input": False,
		"single_file_output": False,
		"multiple_files_output": False,
		"auto": False,
		"auto_indent": 10000
	}

	try:
		opts, _ = getopt.getopt(
			argv, "hi:o:a",["help", "single-input-file=", "single-output-file=", "multiple-input-files=", "multiple-output-files=", "auto="]
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
		elif opt in ("-a", "--auto"):
			args["auto"] = True
			if arg:
				args["auto_indent"] = arg
			logger.debug(f"Auto set to: {arg}")
		elif opt in ("-i", "--single-input-file"):
			args["input_file"] = arg
			logger.debug(f"Single input file set to: {arg}")
		elif opt in ("-o", "--single-output-file"):
			args["output_file"] = arg
			logger.debug(f"Single output file set to: {arg}")
		elif opt in ("--multiple-input-files"):
			args["multiple_files_input"] = True
			args["input_file"] = ''
			if arg:
				args["input_file"] = arg.removesuffix('.json')
			logger.debug(f"Multiple files input prefix set to: {args['input_file']}")
		elif opt in ("--multiple-output-files"):
			args["multiple_files_output"] = True
			args["output_file"] = ''
			if arg:
				args["output_file"] = arg.removesuffix('.json')
			logger.debug(f"Multiple files output prefix set to: {args['output_file']}")

	if (args["single_file_input"] and args["multiple_files_input"]) or (args["single_file_output"] and args["multiple_files_output"]):
		logger.error("Both single file and multiple files options set. Exiting.")
		print(config.BOLD + "Error: " + config.END + "You cannot use single file and multiple files options at the same time.")
		print(config.TXT_USAGE)
		sys.exit(2)

	logger.info("Arguments successfully parsed.")
	return args

