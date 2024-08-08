import logging


def configure_logger():
	logging.basicConfig(filename='FS_Powerwatch.log', filemode='a', level = logging.DEBUG)
	
	rootLoggingStreamHandler = logging.StreamHandler()
	rootLoggingStreamHandler.setLevel(logging.WARNING)
	
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	rootLoggingStreamHandler.setFormatter(formatter)
	logging.addHandler(rootLoggingStreamHandler)
