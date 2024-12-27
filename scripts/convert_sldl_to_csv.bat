:: This file is only used to provide a 'Open as CSV' option in the context menu of Windows Explorer

@echo off
python "E:\Music\sldl\scripts\convert_sldl_to_csv.py" "%~1"
