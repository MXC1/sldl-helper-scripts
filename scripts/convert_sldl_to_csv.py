import csv
import os
import tempfile
import subprocess
import sys

def convert_sldl_to_csv(file_path):
    # Generate a unique temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=temp_dir)
    temp_csv_path = temp_file.name
    temp_file.close()  # Close the file handle to allow Excel to access it later

    # Write CSV header and process input file
    with open(temp_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Location", "Artist", "Album", "Title", "Length", "???", "State", "???"])

        with open(file_path, mode='r', encoding='utf-8') as f:
            lines = f.read().strip().split(";")
            for line in lines:
                if line.startswith("#SLDL:"):
                    line = line.replace("#SLDL:", "")
                # Handle quoting and commas
                row = next(csv.reader([line], skipinitialspace=True))
                csv_writer.writerow(row)

    # Open the CSV file in Excel
    subprocess.Popen(["excel.exe", temp_csv_path], shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
    else:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            convert_sldl_to_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            
    # input()
