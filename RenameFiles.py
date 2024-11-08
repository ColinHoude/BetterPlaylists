import os


def rename_files_in_folders(base_path, folders, characters_to_remove):
    """
    Renames files in specified folders by removing certain characters from filenames.

    Parameters:
    base_path (str): The base directory where the folders are located.
    folders (list): List of folder names within the base directory to process.
    characters_to_remove (str): A string of characters to remove from filenames.

    """
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                if os.path.isfile(file_path):
                    new_filename = ''.join(c for c in filename if c not in characters_to_remove)
                    new_file_path = os.path.join(folder_path, new_filename)

                    # Rename the file if the new name is different
                    if new_file_path != file_path:
                        os.rename(file_path, new_file_path)
                        print(f"Renamed: '{filename}' -> '{new_filename}'")
        else:
            print(f"Folder '{folder}' does not exist at path '{folder_path}'.")


# Usage example
base_path = "mp3Folder"
folders = ["AfroHouse", "DeepHouse", "House", "MelodicHouse"]
characters_to_remove = "&[]'"
rename_files_in_folders(base_path, folders, characters_to_remove)