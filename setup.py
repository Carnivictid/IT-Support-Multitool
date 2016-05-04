from distutils.core import setup
import py2exe

setup(
	windows = [
		{
			"script": 'auto_caller.py',
            "icon_resources": [(1, "apslogo.ico")]
		}
			],
	data_files = [('', ["status_text", "chromedriver.exe", "apslogo.ico"])]
)