
"""
Utility functions for file operations in the Stylus Analyzer
"""
import os
import glob
import platform
import subprocess
from typing import List, Optional, Dict, Any, Tuple
import tree_sitter
from tree_sitter import Language, Parser
import pkg_resources
import shutil

# Global parser instance to avoid recreating it multiple times
_RUST_PARSER = None

def _get_shared_library_extension() -> str:
    """
    Get the appropriate shared library file extension for the current platform
    
    Returns:
        File extension for shared libraries (.so, .dll, .dylib)
    """
    system = platform.system().lower()
    if system == 'windows':
        return '.dll'
    elif system == 'darwin':  # macOS
        return '.dylib'
    else:  # Linux and other Unix-like systems
        return '.so'

def _is_compatible_shared_library(library_file: str) -> bool:
    """
    Check if the shared library is compatible with the current platform
    
    Args:
        library_file: Path to the shared library file
        
    Returns:
        True if compatible, False otherwise
    """
    if not os.path.exists(library_file):
        return False
        
    try:
        # Try to determine file type using 'file' command on Unix-like systems
        if platform.system() in ['Linux', 'Darwin']:  # Linux or macOS
            try:
                result = subprocess.run(
                    ['file', library_file], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    file_output = result.stdout.lower()
                    
                    # Check for Linux compatibility
                    if platform.system() == 'Linux':
                        if 'elf' in file_output and 'shared object' in file_output:
                            return True
                        if 'pe32' in file_output or 'ms windows' in file_output:
                            print(f"Warning: Found Windows DLL on Linux system: {library_file}")
                            return False
                            
                    # Check for macOS compatibility  
                    elif platform.system() == 'Darwin':
                        if 'mach-o' in file_output and ('bundle' in file_output or 'shared' in file_output):
                            return True
                        if 'pe32' in file_output or 'ms windows' in file_output:
                            print(f"Warning: Found Windows DLL on macOS system: {library_file}")
                            return False
            except FileNotFoundError:
                # 'file' command not available, fall back to loading test
                pass
                        
        # Fallback: try to load the library to test compatibility
        try:
            test_lang = Language(library_file, 'rust')
            return True
        except Exception as e:
            print(f"Shared library compatibility test failed for {library_file}: {e}")
            return False
            
    except Exception as e:
        print(f"Error checking shared library compatibility: {e}")
        return False

def get_rust_parser():
    """
    Get or initialize the Rust parser (singleton pattern)
    
    Returns:
        Parser instance configured for Rust
    """
    global _RUST_PARSER
    if _RUST_PARSER is None:
        try:
            # Get the package directory
            package_dir = pkg_resources.resource_filename('stylus_analyzer', '')
            
            # Define paths
            build_dir = os.path.join(package_dir, 'build')
            rust_dir = os.path.join(package_dir, 'tree-sitter-rust')
            
            # Use platform-appropriate file extension
            library_extension = _get_shared_library_extension()
            library_file = os.path.join(build_dir, f'my-languages{library_extension}')
            
            # Create build directory if it doesn't exist
            os.makedirs(build_dir, exist_ok=True)
            
            # Check if we need to build/rebuild the library
            needs_rebuild = False
            
            if not os.path.exists(library_file):
                print(f"Shared library not found at {library_file}, building for {platform.system()}...")
                needs_rebuild = True
            elif not _is_compatible_shared_library(library_file):
                print(f"Shared library is incompatible with {platform.system()}, rebuilding...")
                needs_rebuild = True
                
            if needs_rebuild:
                print(f"Building tree-sitter language library for {platform.system()}...")
                try:
                    tree_sitter.Language.build_library(
                        library_file,
                        [rust_dir]
                    )
                    print(f"Successfully built language library at {library_file}")
                except Exception as build_error:
                    print(f"Failed to build tree-sitter library: {build_error}")
                    
                    # Try to find an existing compatible library
                    for ext in ['.so', '.dll', '.dylib']:
                        alt_file = os.path.join(build_dir, f'my-languages{ext}')
                        if os.path.exists(alt_file) and _is_compatible_shared_library(alt_file):
                            print(f"Using existing compatible library: {alt_file}")
                            library_file = alt_file
                            break
                    else:
                        raise build_error
            
            # Load the Rust language
            rust_language = Language(library_file, 'rust')
            
            # Initialize the parser
            _RUST_PARSER = Parser()
            _RUST_PARSER.set_language(rust_language)
            # print(f"Rust parser initialized successfully with {library_file}")
            
        except Exception as e:
            print(f"Error initializing Rust parser: {str(e)}")
            print(f"Platform: {platform.system()} {platform.machine()}")
            # Return a None parser which will be handled by the callers
    
    return _RUST_PARSER

def generate_rust_ast(code: str):
    """
    Generate AST for Rust code using tree-sitter
    
    Args:
        code: Rust source code as string
        
    Returns:
        Tree object representing the parsed AST
    """
    parser = get_rust_parser()
    if not parser:
        return None
        
    return parser.parse(bytes(code, "utf8"))

def find_rust_contracts(directory: str) -> List[str]:
    """
    Find all Rust contract files in the given directory
    
    Args:
        directory: The directory to search in
        
    Returns:
        List of file paths to Rust contracts
    """
    contract_files = []
    
    # Normalize directory path for cross-platform compatibility
    directory = os.path.normpath(directory)
    
    # Common patterns for Rust contract files in Stylus projects
    rust_patterns = [
        os.path.join(directory, "**", "*.rs"),
        os.path.join(directory, "src", "**", "*.rs"),
        os.path.join(directory, "contracts", "**", "*.rs"),
        os.path.join(directory, "lib", "**", "*.rs"),
    ]
    
    for pattern in rust_patterns:
        try:
            contract_files.extend(glob.glob(pattern, recursive=True))
        except Exception as e:
            print(f"Error searching pattern {pattern}: {e}")
    
    # Remove duplicates and normalize paths
    contract_files = list(set(os.path.normpath(f) for f in contract_files))
    
    return contract_files

def read_file_content(file_path: str) -> Optional[str]:
    """
    Read the content of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string, or None if file can't be read
    """
    try:
        # Normalize path for cross-platform compatibility
        file_path = os.path.normpath(file_path)
        
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def find_readme(directory: str) -> Optional[str]:
    """
    Find and read the README file in the given directory
    
    Args:
        directory: The directory to search in
        
    Returns:
        Content of the README file, or None if not found
    """
    # Normalize directory path
    directory = os.path.normpath(directory)
    
    readme_patterns = [
        "README.md",
        "Readme.md", 
        "readme.md",
        "README.txt",
        "readme.txt",
        "README.rst",
        "readme.rst",
    ]
    
    for pattern in readme_patterns:
        readme_path = os.path.join(directory, pattern)
        if os.path.exists(readme_path):
            return read_file_content(readme_path)
    
    return None

def collect_project_files(directory: str) -> Dict[str, Any]:
    """
    Collect all relevant files from the Stylus project
    
    Args:
        directory: The root directory of the project
        
    Returns:
        Dictionary containing contract files and README content
    """
    # Normalize directory path
    directory = os.path.normpath(directory)
    
    contract_files = find_rust_contracts(directory)
    readme_content = find_readme(directory)
    
    contract_contents = {}
    for file_path in contract_files:
        content = read_file_content(file_path)
        if content:
            contract_contents[file_path] = content
    
    return {
        "contracts": contract_contents,
        "readme": readme_content,
        "project_dir": directory
    } 
