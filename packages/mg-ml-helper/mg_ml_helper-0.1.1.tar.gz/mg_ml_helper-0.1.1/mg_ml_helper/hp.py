from zipfile import ZipFile, ZIP_DEFLATED

def extract_files(zipfile_path, folder_path='', extract_to=''):
    """
    Extracts a zip file to a specified folder.

    Parameters: 
    zipfile_path: Enter the path of the zipfile.
    folder_path: specific file in the .zip file.
    extract_to: destination folder, to extract the zip file.
    
    """
    try:
        with ZipFile(zipfile_path, 'r') as zip_ref:
            zip_ref.extract(f"{zipfile_path}/{folder_path}", extract_to)
            print("Successfully extracted the zipfile")
    except Exception as e:
        print(f"Something went wrong! \nAn error occurred: {e}")


def compress_files(files_to_compress, output_zip_filename):

    """
    files_compress: List containing the paths of files to compress.
    output_zip_filename: Name of the output zip file.

    """

    try:
        with ZipFile(output_zip_filename, "w", ZIP_DEFLATED) as zipf:
            for file_path in files_to_compress:
                zipf.write(file_path)
                
            print(f"Files compressed into {output_zip_filename}")
    except Exception as e:
        print(f"Something went wrong! \nAn error occurred: {e}")