import unittest
import os

def load_tests_excluding_utils(start_dir="tests/unit", pattern="test_*.py", exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {"utils"}

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=start_dir)
                module_name = rel_path.replace(os.sep, ".")[:-3] 
                try:
                    module = __import__(f"tests.unit.{module_name}", fromlist=[""])
                    suite.addTests(loader.loadTestsFromModule(module))
                except Exception as e:
                    print(f"⚠️ No se pudo cargar {module_name}: {e}")
    return suite
