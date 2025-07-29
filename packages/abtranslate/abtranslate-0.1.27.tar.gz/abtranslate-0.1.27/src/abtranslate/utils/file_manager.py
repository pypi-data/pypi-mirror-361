from zipfile import ZipFile
from pathlib import Path

from .logger import logger 

def extract_package(model_file: str, extract_dir: str) -> bool:
    """
    Safely extract model files with.
    
    Args:
        model_file: Path to the model archive file
        extract_dir: Directory to extract files to
        
    Returns:
        Path to package directory if extraction successful, False otherwise
    """
    try:
        with ZipFile(model_file, 'r') as zip_ref:
            # Validate zip file integrity
            zip_ref.testzip()
            
            # Get list of files to extract
            file_list = zip_ref.namelist()
            # Add this to extract_package for debugging
            logger.info(f"Files in ZIP: {file_list[:5]}")  # Show first 5 files
            
            # Check if files already exist
            extract_path = Path(extract_dir)
            all_exist = all(
                (extract_path / name).exists() 
                for name in file_list   
            )
            
            if not all_exist:
                logger.info(f"Extracting model files to {extract_dir}")
                zip_ref.extractall(extract_dir)
            else:
                logger.info("Model files already exist, skipping extraction")
            
            package_name = file_list[0]
            logger.info(f"Package name detected: {package_name}")
            return Path(extract_dir)/package_name
            
    except Exception as e:
        raise Exception(f"Model extraction failed: {e}")
        # return False