#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = SKILL_ROOT / "scripts" / "nimbus-autoreview"


class NimbusAutoreviewTests(unittest.TestCase):
    def test_wrapper_delegates_with_profile_and_context(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            base = root / "autoreview"
            base.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "print(json.dumps(sys.argv[1:]))\n",
                encoding="utf-8",
            )
            base.chmod(base.stat().st_mode | stat.S_IXUSR)
            env = os.environ.copy()
            env["NIMBUS_AUTOREVIEW_BASE"] = str(base)

            result = subprocess.run(
                [sys.executable, str(WRAPPER), "--mode", "local", "--dry-run"],
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

        arguments = json.loads(result.stdout)
        self.assertEqual(arguments[0], "--config")
        self.assertEqual(Path(arguments[1]), SKILL_ROOT / "autoreview.toml")
        self.assertEqual(arguments[2], "--prompt")
        self.assertIn("Crate dependency invariants", arguments[3])
        self.assertEqual(arguments[-3:], ["--mode", "local", "--dry-run"])

    def test_wrapper_refuses_to_drop_nimbus_config(self) -> None:
        result = subprocess.run(
            [sys.executable, str(WRAPPER), "--no-config"],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires its Nimbus profile config", result.stderr)


if __name__ == "__main__":
    unittest.main()
