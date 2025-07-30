#!/usr/bin/env python3

import os
import sys

try:
	from setuptools import setup
except Exception as e:
	print(e)
	sys.exit(1)

file_setup = os.path.abspath(os.path.realpath(__file__))
dir_of_project = os.path.dirname(file_setup)
sys.path.insert(0, dir_of_project)


DESCRIPTION = ''
LONG_DESCRIPTION = ''

setup(
	name='ocrlib',
	version='1.2',
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	license='MIT',
	requires=[
			'PyPDF2',
			'PyMuPDF',
			'reportlab',
			'openpyxl',
			'openpyxl',
			'pandas',
			'Pillow',
			'opencv_python',
			'requests',
			'pytesseract',
			'soup_files',
			'convert_stream',
	],
	packages=['ocrlib', 'ocrlib.models', 'ocrlib.utils'],
	zip_safe=False,
)


