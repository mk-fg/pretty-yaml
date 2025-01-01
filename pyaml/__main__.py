import os, sys, pyaml.cli

main = pyaml.cli.main # was defined here before moving to cli.py

if __name__ == '__main__':
	try: sys.exit(main())
	except BrokenPipeError: # stdout pipe closed
		os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
		sys.exit(1)
