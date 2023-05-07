import os
import tempfile
import json
import subprocess


def edit_data(data, encoding=None, cls=None):
    # Create a temporary file and write the JSON data to it
    with tempfile.NamedTemporaryFile(mode='w+', encoding=encoding, delete=False, suffix='.json') as f:
        json.dump(data, f, indent=4, cls=cls, ensure_ascii=False)
        # Get the path of the temporary file
        filename = f.name

    print(f'Opening {filename}...')
    # Open the temporary file in the default editor for JSON files
    if os.name == 'nt':  # if on Windows
        os.startfile(filename)
    else:  # if on Unix-like system
        subprocess.run(['open', '-a', 'TextEdit', filename], check=True)

    # Wait for the user to save and close the file
    input('Press enter when done editing the file...')

    # Read the modified JSON data
    with open(filename, 'r', encoding=encoding) as f:
        new_data = json.load(f)
        return new_data
