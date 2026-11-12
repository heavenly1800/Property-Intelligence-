import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class DockerRuntimeImportsTest(unittest.TestCase):
    def test_app_main_imports_from_docker_filesystem_layout(self):
        repository_root = Path(__file__).resolve().parents[3]

        with tempfile.TemporaryDirectory() as temporary_directory:
            runtime_root = Path(temporary_directory)
            shutil.copytree(
                repository_root / "services" / "api" / "app",
                runtime_root / "app",
            )
            shutil.copytree(
                repository_root / "services" / "decision-engine",
                runtime_root / "decision-engine",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            environment = os.environ.copy()
            environment.update(
                {
                    "APP_ENV": "test",
                    "PYTHONPATH": str(runtime_root),
                    "SUPABASE_URL": "https://ci-test.supabase.co",
                    "SUPABASE_ANON_KEY": "ci-test-anon-key",
                    "SUPABASE_SERVICE_ROLE_KEY": "ci-test-service-role-key",
                    "OPENAI_API_KEY": "ci-test-openai-key",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-c",
                    (
                        "import app.main; "
                        "from strategies.assignment_strategy import "
                        "AssignmentStrategy; "
                        "assert AssignmentStrategy"
                    ),
                ],
                cwd=runtime_root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
