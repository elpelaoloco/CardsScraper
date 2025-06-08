# tests/run_all_tests.py
import unittest
import sys
from utils.tee import Tee

def run_tests():
    report_path = "test_report.txt"
    tee = Tee(report_path)
    sys.stdout = tee

    print("REPORTE DE TESTS")
    print("=" * 40)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 40)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Tests exitosos : {len(result.successes) if hasattr(result, 'successes') else result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallos         : {len(result.failures)}")
    print(f"Errores        : {len(result.errors)}")

    tee.close()
    sys.stdout = sys.__stdout__
    print(f"📝 Reporte guardado en {report_path}")

if __name__ == "__main__":
    run_tests()
