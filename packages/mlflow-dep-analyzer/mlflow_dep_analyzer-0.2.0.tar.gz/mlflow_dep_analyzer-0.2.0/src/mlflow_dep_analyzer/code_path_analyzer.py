"""
Code Path Analysis for MLflow Models

This module provides utilities to analyze Python code and determine
the minimal set of files needed for MLflow model deployment with code_paths.

The goal is to identify which files are actually used by a model so that
only necessary code is bundled with the model artifact.
"""

import ast
import os
from pathlib import Path


class CodePathAnalyzer:
    """
    Analyzer for determining minimal code paths for MLflow models.

    This analyzer:
    1. Uses AST to find local imports without code execution
    2. Recursively discovers all dependencies
    3. Filters out unnecessary files
    4. Provides detailed analysis for debugging
    """

    def __init__(self, repo_root: str):
        """
        Initialize the code path analyzer.

        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = Path(repo_root).resolve()

    def analyze_file(self, file_path: str) -> set[str]:
        """
        Find all local imports in a Python file.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Set of local import module names
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return set()

        local_imports = set()
        repo_name = self.repo_root.name

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    # Check if it's a local import
                    if self._is_local_import(module_name, repo_name):
                        local_imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Relative imports (. or ..)
                    if node.level > 0:
                        local_imports.add(node.module or "")
                    # Absolute imports that start with repo name or known local patterns
                    elif self._is_local_import(node.module, repo_name):
                        local_imports.add(node.module)

        return local_imports

    def _is_local_import(self, module_name: str, repo_name: str) -> bool:
        """Check if a module name represents a local import using dynamic detection."""
        if not module_name:
            return False

        # Check if starts with repo name
        if repo_name and module_name.startswith(repo_name):
            return True

        # Get the top-level module name
        top_level_module = module_name.split(".")[0]

        # Check if this module exists as a directory or file in the repo
        return self._module_exists_in_repo(top_level_module)

    def _module_exists_in_repo(self, module_name: str) -> bool:
        """Check if a module exists as a local file or directory in the repository."""
        # Check common locations where Python modules might exist
        search_paths = [
            self.repo_root,  # Root level
            self.repo_root / "src",  # src/ directory
            self.repo_root / "lib",  # lib/ directory
            self.repo_root / "packages",  # packages/ directory
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Check for package directory (with __init__.py)
            package_dir = search_path / module_name
            if package_dir.is_dir():
                # It's a local package if it has __init__.py or contains .py files
                if (package_dir / "__init__.py").exists() or any(package_dir.glob("*.py")):
                    return True

            # Check for module file
            module_file = search_path / f"{module_name}.py"
            if module_file.is_file():
                return True

        return False

    def collect_dependencies(self, entry_file: str) -> dict[str, set[str]]:
        """
        Recursively collect all local dependencies from an entry file.

        Args:
            entry_file: Path to the main file to start analysis from

        Returns:
            Dictionary mapping file paths to their local imports
        """
        dependencies = {}
        # Convert entry_file to absolute path for consistency
        entry_file_abs = str(Path(entry_file).resolve())
        to_process = {entry_file_abs}
        processed = set()

        while to_process:
            current = to_process.pop()
            if current in processed:
                continue
            processed.add(current)

            # Get imports for current file
            imports = self.analyze_file(current)
            dependencies[current] = imports

            # Find corresponding files for imports
            for imp in imports:
                # Convert module path to file paths
                potential_files = self._module_to_file_paths(imp)
                for file_path in potential_files:
                    if file_path and file_path not in processed:
                        to_process.add(file_path)

        return dependencies

    def _module_to_file_paths(self, module_name: str) -> list[str]:
        """
        Convert a module name to potential file paths.

        Args:
            module_name: Python module name (e.g., "projects.my_model.sentiment")

        Returns:
            List of potential file paths that could contain this module
        """
        if not module_name:
            return []

        paths = []

        # Convert dots to path separators
        module_path = module_name.replace(".", "/")

        # Try as a package (directory with __init__.py)
        package_init = self.repo_root / module_path / "__init__.py"
        if package_init.exists():
            paths.append(str(package_init))

        # Try as a direct .py file
        module_file = self.repo_root / (module_path + ".py")
        if module_file.exists():
            paths.append(str(module_file))

        # Try relative to different base directories
        for base_dir in ["", "src", "examples"]:
            if base_dir:
                base_path = self.repo_root / base_dir / module_path
            else:
                base_path = self.repo_root / module_path

            # Check for package
            package_init = base_path / "__init__.py"
            if package_init.exists() and str(package_init) not in paths:
                paths.append(str(package_init))

            # Check for module file
            module_file = Path(str(base_path) + ".py")
            if module_file.exists() and str(module_file) not in paths:
                paths.append(str(module_file))

        return paths

    def analyze_code_paths(
        self,
        entry_files: list[str],
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> dict:
        """
        Analyze code paths for a set of entry files.

        Args:
            entry_files: List of main files to analyze
            include_patterns: Glob patterns for files to include
            exclude_patterns: Glob patterns for files to exclude

        Returns:
            Dictionary with analysis results
        """
        if include_patterns is None:
            include_patterns = ["**/*.py"]
        if exclude_patterns is None:
            exclude_patterns = ["**/__pycache__/**", "**/.git/**"]

        all_dependencies = {}
        all_required_files = set()

        # Analyze each entry file
        for entry_file in entry_files:
            if not os.path.exists(entry_file):
                print(f"Warning: Entry file does not exist: {entry_file}")
                continue

            file_deps = self.collect_dependencies(entry_file)
            all_dependencies[entry_file] = file_deps

            # Add all discovered files - both from the dependency keys and the resolved file paths
            all_required_files.update(file_deps.keys())  # All files that were analyzed
            # Also add any additional files discovered through module resolution
            for deps in file_deps.values():
                for dep_files in [self._module_to_file_paths(dep) for dep in deps]:
                    all_required_files.update(dep_files)

        # Filter files based on patterns
        filtered_files = self._filter_files(all_required_files, include_patterns, exclude_patterns)

        # Generate relative paths for MLflow
        relative_paths = []
        for file_path in filtered_files:
            try:
                rel_path = os.path.relpath(file_path, self.repo_root)
                if not rel_path.startswith(".."):  # Only include files within repo
                    relative_paths.append(rel_path)
            except ValueError:
                # Path is on different drive (Windows)
                pass

        return {
            "entry_files": entry_files,
            "required_files": sorted(filtered_files),
            "relative_paths": sorted(relative_paths),
            "dependencies": all_dependencies,
            "analysis": {
                "total_files": len(filtered_files),
                "total_dependencies": sum(len(deps) for deps in all_dependencies.values()),
                "include_patterns": include_patterns,
                "exclude_patterns": exclude_patterns,
            },
        }

    def _filter_files(self, files: set[str], include_patterns: list[str], exclude_patterns: list[str]) -> set[str]:
        """Filter files based on include/exclude patterns."""
        from fnmatch import fnmatch

        filtered = set()

        for file_path in files:
            file_path_obj = Path(file_path)

            # Check if file matches include patterns
            included = False
            for pattern in include_patterns:
                if fnmatch(str(file_path_obj), pattern) or fnmatch(file_path_obj.name, pattern):
                    included = True
                    break

            if not included:
                continue

            # Check if file matches exclude patterns
            excluded = False
            for pattern in exclude_patterns:
                if fnmatch(str(file_path_obj), pattern) or fnmatch(file_path_obj.name, pattern):
                    excluded = True
                    break

            if not excluded:
                filtered.add(file_path)

        return filtered


def analyze_code_paths(
    entry_files: list[str],
    repo_root: str,
    include_patterns: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[str]:
    """
    Analyze code paths and return relative paths for MLflow code_paths.

    This is a convenience function that returns just the relative paths
    needed for MLflow's code_paths parameter.

    Args:
        entry_files: List of main Python files to analyze
        repo_root: Root directory of the repository
        include_patterns: Glob patterns for files to include
        exclude_patterns: Glob patterns for files to exclude

    Returns:
        List of relative file paths for MLflow code_paths
    """
    analyzer = CodePathAnalyzer(repo_root)
    result = analyzer.analyze_code_paths(
        entry_files=entry_files, include_patterns=include_patterns, exclude_patterns=exclude_patterns
    )
    return result["relative_paths"]


def find_model_code_paths(model_file: str, repo_root: str | None = None) -> list[str]:
    """
    Find all code paths needed for a specific model file.

    This is a high-level convenience function for the common use case
    of finding code paths for a single model file.

    Args:
        model_file: Path to the main model Python file
        repo_root: Root directory of the repository (auto-detected if None)

    Returns:
        List of relative file paths for MLflow code_paths
    """
    if repo_root is None:
        # Auto-detect repo root by looking for common markers
        current_dir = Path(model_file).parent
        while current_dir != current_dir.parent:
            if any(
                (current_dir / marker).exists() for marker in [".git", "pyproject.toml", "setup.py", "requirements.txt"]
            ):
                repo_root = str(current_dir)
                break
            current_dir = current_dir.parent

        if repo_root is None:
            repo_root = str(Path(model_file).parent)

    return analyze_code_paths(
        entry_files=[model_file],
        repo_root=repo_root,
        exclude_patterns=["**/__pycache__/**", "**/.git/**", "**/tests/**", "test_*.py"],
    )
