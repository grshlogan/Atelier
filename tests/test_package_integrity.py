from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.security.package_integrity import sha256_file, verify_sha256


class PackageIntegrityTests(unittest.TestCase):
    def test_sha256_file_returns_digest_for_file_bytes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "package.bin"
            target.write_bytes(b"atelier")

            digest = sha256_file(target)

            self.assertEqual(
                digest,
                "f4d65b2483b34a8d50bcf2c9e053077c4dc7c00b65008ce1988ce4eca45741c8",
            )

    def test_verify_sha256_rejects_mismatch(self) -> None:
        with TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "package.bin"
            target.write_bytes(b"atelier")

            self.assertFalse(verify_sha256(target, "0" * 64))


if __name__ == "__main__":
    unittest.main()
