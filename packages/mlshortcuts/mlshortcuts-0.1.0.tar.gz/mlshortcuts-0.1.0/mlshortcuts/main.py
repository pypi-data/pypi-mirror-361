import zipfile
import shutil
import os

def info():

    """Run me!!!

    mlshortcuts.info()
    
    I will be the guide to use this library
    """

    print(
        """
    This function is the guide to use this library.

    Functions:
    * Zip.extract_zip(): Lets you extract .zip files into any specified path.
    * Zip.view_zip(): Lets you view the contents of the .zip files.
    * Zip.create_zip_from_dir: Lets you create zip files by directory.
    * Zip.create_zip_from_list: Lets you create zip files by list.
    
    """
    )

class Zip:
    def extract_zip(zipfile_path, extract_to=''):

        """
        Extract the zipfile at a specific path.

        * zipfile_path: Path of the zipfile.
        * extract_to: Path to extract the zipfile to.

        Returns the path of the extracted file, **(if provided)**.
        """


        try:
            with zipfile.ZipFile(zipfile_path, 'r') as zipref:
                zipref.extractall(extract_to)
                print("Successfully!! Extracted the zipfile")

        except Exception as e:
            print(f"Encounterd an exception!!! \n{e}")

        return extract_to

    def view_zip(zipfile_path):
        """
        View the members in the zipfile. 

        * zipfile_path: The path to the zipfile.
        
        Returns the list of members in the zipfile.
        """

        try:
            with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
                member_names = zip_ref.namelist()
                for name in member_names:
                    print(name)
    
        except Exception as e:
            print(f"An error occurred during extraction: {e}")

        return member_names
    

    def create_zip_from_dir(dir_path: str, zip_name: str):
        """
        Compress a directory into a .zip file using zipfile module.

        * dir_path: Path to the directory to zip.
        * zip_name: Output zip file path (with or without .zip extension).

        Returns the path of the created zip file.
        """

        # Ensure .zip extension
        if not zip_name.endswith('.zip'):
            zip_name += '.zip'

        try:
            zip_path = shutil.make_archive(zip_name, 'zip', dir_path)
            print(f"Successfully created zip file: {zip_name}")
            return zip_path

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
   

    def create_zip_from_list(file_list: list, zip_name: str):
        """
        Create zipfile using file list.

        * file_list: A list of path of all files.
        * zip_name: Name of the zip file.

        Returns the path of the  zipfile.
        """
        
        try:
            with zipfile.ZipFile(f"{zip_name}.zip", 'w') as zipf:
                for file in file_list:
                    zipf.write(file)
            print(f"Successfully created '{f"{zip_name}.zip"}' containing the specified files.")
        except Exception as e:
            print(f"An error occurred: {e}")
