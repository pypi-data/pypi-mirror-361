import ast
from pathlib import Path
import subprocess
from importlib.metadata import version, PackageNotFoundError
import json

class HRequire:
    def __init__(self):
        self.base_dir: Path = Path(".").resolve()
        self.excluded_dirs = {"__pycache__", ".venv", "venv", ".env", "env", ".git"}
        self.MANUAL_MAP = {
            "bs4": "beautifulsoup4",
            "PIL": "Pillow",
            "yaml": "PyYAML",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "google": "google-auth",
        }
    def list_py_files(self) -> list[Path]:
        py_files = []
        for file in self.base_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            if any(part in self.excluded_dirs for part in file.parts):
                continue
            py_files.append(file.resolve())
        return py_files

    def list_imports(self, file_path: Path) -> tuple[bool, list[str] | str]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source_code = f.read()
                tree = ast.parse(source_code, filename=str(file_path))
        except SyntaxError as e:
            return False, f"Error: SyntaxError: {e}"
        except Exception as e:
            return False, f"E rror: {type(e).__name__}: {e}"

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".")[0]
                    mapped_name = self.MANUAL_MAP.get(top_level, top_level)
                    imports.add(mapped_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_level = node.module.split(".")[0]
                    mapped_name = self.MANUAL_MAP.get(top_level, top_level)
                    imports.add(mapped_name)

        return True, sorted(set(imports))
    
    def get_package_version(self, package: str) -> str:
        try:
            return version(package)
        except PackageNotFoundError:
            return "unknown"
        
    def list_imports_json(self) -> dict[str, list[str] | str]:
        """
        For more details each file.
        """
        result = {}
        for file in self.list_py_files():
            rel_path = file.relative_to(self.base_dir)
            ok, data = self.list_imports(file)
            if ok:
                with_versions = [
                    f"{pkg}=={self.get_package_version(pkg)}" for pkg in data
                ]
                result[str(rel_path)] = sorted(with_versions)
            else:
                result[str(rel_path)] = data 
        return result

    def get_top_level_packages(self):
        result = subprocess.run(
            ["pip", "list", "--not-required", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        return [pkg['name'] for pkg in packages]

    def mapping_top_level_imports(self) -> list[str]:
        """
        Return list of unique 3rd-party packages imported (not standard lib or dependencies).
        """
        top_level_installed = set(pkg.lower() for pkg in self.get_top_level_packages())
        used_packages = set()

        for file in self.list_py_files():
            ok, data = self.list_imports(file)
            if ok:
                for pkg in data:
                    if pkg.lower() in top_level_installed:
                        used_packages.add(pkg)

        return sorted(
            f"{pkg}=={self.get_package_version(pkg)}" for pkg in used_packages
        )

    def write_requirements_txt(self, output_path: Path = Path("requirements.txt")) -> None:
        """
        Write the result of mapping_top_level_imports() to a requirements.txt file.
        """
        print(f">> Creating requirements.txt ...")
        packages = self.mapping_top_level_imports()
        output_path.write_text("\n".join(packages), encoding="utf-8")
        print(f">> Succeed")

def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Auto-generate requirements.txt from your project imports.")
    parser.add_argument("--details", action="store_true", help="Show detailed import mapping per file (as JSON)")

    args = parser.parse_args()

    h = HRequire()

    if args.details:
        details = h.list_imports_json()
        print(json.dumps(details, indent=2, ensure_ascii=False))
    else:
        h.write_requirements_txt()
if __name__ == "__main__":
    cli()
