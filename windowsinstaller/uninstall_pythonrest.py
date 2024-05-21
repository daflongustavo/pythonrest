import os
import re
import shutil
import sys
import subprocess
import time
import hashlib
import json


def generate_hash_for_file(script_to_be_checked):
    """ Generate a SHA-256 hash for the given file. """
    hash_func = hashlib.sha256()
    with open(os.path.abspath(script_to_be_checked), 'rb') as file:  # Open in binary mode for hashing
        while chunk := file.read(4096):  # Read the file in chunks to avoid memory issues
            hash_func.update(chunk)
    return hash_func.hexdigest()


def validate_script_integrity(current_script_directory_path, script_to_be_checked, script_path):
    try:
        with open(os.path.join(current_script_directory_path, "script_hashs.json"), 'r') as file:
            data = json.load(file)
            expected_hash = data.get(script_to_be_checked)
            if expected_hash is None:
                raise ValueError("Expected hash not found in JSON.")
        current_hash = generate_hash_for_file(script_path)
        if current_hash == expected_hash:
            print("Script integrity check passed.")
            return True
        else:
            print("Error: Script integrity check failed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def validate_localappdata(local_app_data_path):
    # Regex pattern to match a standard Windows LOCALAPPDATA path
    # This assumes the path starts with a drive letter, followed by ':', and standard Windows folder structure
    pattern = r'[A-Za-z]:\\Users\\[^\\]+\\AppData\\Local$'

    if re.match(pattern, local_app_data_path):
        return True
    else:
        print("LOCALAPPDATA path is invalid:", local_app_data_path)
        return False


def remove_pythonrest_from_user_program_files():
    local_app_data_path = os.environ['LOCALAPPDATA']
    if validate_localappdata(local_app_data_path):
        install_directory = os.path.join(local_app_data_path, 'PythonREST')
        try:
            shutil.rmtree(install_directory)
            print(f'Successfully removed the PythonREST installation from {install_directory}.')
        except Exception as e:
            print(f'Error: Unable to remove PythonREST installation folder. {e}')
            sys.exit(1)
    else:
        print(f'Error: Failed to validate local app data path: {local_app_data_path}')
        sys.exit(1)


def run_script_that_removes_pythonrest_from_path(current_script_directory, powershell_script_name):
    try:
        powershell_script_path = os.path.join(current_script_directory, powershell_script_name)
        validate_script_integrity(current_script_directory, powershell_script_name, powershell_script_path)
        powershell_command = [
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-File', powershell_script_path
        ]
        subprocess.run(powershell_command, check=True)
        print('Successfully cleaned PythonREST from the user PATH settings.')
    except Exception as e:
        print(f'Error: Unable to remove PythonREST from user PATH. {e}')
        sys.exit(1)


if __name__ == "__main__":
    try:
        current_script_directory = os.path.dirname(os.path.abspath(__file__))

        remove_pythonrest_from_user_program_files()

        time.sleep(1)

        powershell_script_name = 'removepythonrestfromuserpath.ps1'

        run_script_that_removes_pythonrest_from_path(current_script_directory, powershell_script_name)

    except SystemExit:
        input('Press Enter to exit...')
        sys.exit(1)

    print('PythonREST uninstallation completed successfully.')
    input('Press Enter to exit...')
