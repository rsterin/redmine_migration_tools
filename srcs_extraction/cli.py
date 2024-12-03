import getopt
import sys
from srcs_extraction import config, logger

def parse_args(argv):
	"""
	Parse command-line arguments and return them as a dictionary.

	Args:
		argv (list): List of argument.

	Returns:
		dict: Parsed arguments as a dictionary.
	"""
	args = {
		"api_key": None,
		"url": config.BASE_URL,
		"single_file": False,
		"multiple_files": False,
		"output": "outputs/redmine_data.json",
		"endpoints": []
	}

	try:
		opts, _ = getopt.getopt(
			argv, "hu:s:ma:e:", ["help", "url=", "single-file=", "multiple-files=", "api-key=", "endpoint="]
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
		elif opt in ("-a", "--api-key"):
			args["api_key"] = arg
			logger.debug(f"API key set to: {arg}")
		elif opt in ("-u", "--url"):
			args["url"] = arg
			logger.debug(f"Base URL set to: {arg}")
		elif opt in ("-s", "--single-file"):
			args["single_file"] = True
			args["output"] = arg
			logger.debug(f"Single output file set to: {arg}")
		elif opt in ("-m", "--multiple-files"):
			args["multiple_files"] = True
			args["output"] = ''
			if arg:
				args["output"] = arg.removesuffix('.json')
			logger.debug(f"Multiple files output prefix set to: {args['output']}")
		elif opt in ("-e", "--endpoint"):
			args["endpoints"].append(arg)
			logger.debug(f"Custom endpoint added: {arg}")

	if not args["api_key"]:
		logger.error("Missing API key. Exiting.")
		print(config.BOLD + "Error: " + config.END + "Missing API key")
		print(config.TXT_USAGE)
		sys.exit(2)

	if args["single_file"] and args["multiple_files"]:
		logger.error("Both single file and multiple files options set. Exiting.")
		print(config.BOLD + "Error: " + config.END + "You cannot use single file and multiple files options at the same time.")
		print(config.TXT_USAGE)
		sys.exit(2)

	logger.info("Arguments successfully parsed.")
	return args
