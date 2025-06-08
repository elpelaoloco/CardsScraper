# tests/run_all_tests.py
import unittest
import sys
import traceback
from collections import defaultdict
from tests.utils.tee import Tee
from tests.utils.load_tests import load_tests_excluding_utils

class VerboseTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
        self.test_logs = defaultdict(list)

    def startTest(self, test):
        super().startTest(test)
        module = test.__class__.__module__
        self.test_logs[module].append(f"→ Ejecutando: {test}")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)
        module = test.__class__.__module__
        self.test_logs[module].append(f"✔ Éxito: {test}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        module = test.__class__.__module__
        self.test_logs[module].append(f"❌ Fallo: {test}\n{self._exc_info_to_string(err, test)}")

    def addError(self, test, err):
        super().addError(test, err)
        module = test.__class__.__module__
        self.test_logs[module].append(f"⚠️ Error: {test}\n{self._exc_info_to_string(err, test)}")

def run_tests():
    report_path = "test_report.txt"
    tee = Tee(report_path)
    sys.stdout = tee

    print("🧪 REPORTE DE TESTS")
    print("=" * 60)

    suite = load_tests_excluding_utils()
    runner = unittest.TextTestRunner(verbosity=2, resultclass=VerboseTestResult)
    result = runner.run(suite)

    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Tests exitosos : {len(result.successes)}")
    print(f"Fallos         : {len(result.failures)}")
    print(f"Errores        : {len(result.errors)}")

    if result.failures:
        print("\n❌ FALLAS DETECTADAS:")
        for test, tb in result.failures:
            print(f"- {test}:\n{tb}")


    print("\n📄 DETALLES POR TEST:")
    for module, logs in result.test_logs.items():
        print(f"\n--- {module} ---")
        for line in logs:
            print(line)
    if result.errors:
        print("\n⚠️ ERRORES DETECTADOS:")
        for test, tb in result.errors:
            print(f"- {test}:\n{tb}")

    tee.close()
    sys.stdout = sys.__stdout__
    print(f"📝 Reporte guardado en {report_path}")

if __name__ == "__main__":
    run_tests()
