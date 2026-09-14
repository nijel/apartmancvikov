# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase


class ImageManifestTest(SimpleTestCase):
    def setUp(self):
        """Build an isolated manifest without requiring GraphicsMagick."""
        self.generator = importlib.import_module("scripts.generate-images")
        directory = self.enterContext(TemporaryDirectory())
        root = Path(directory)
        self.manifest_path = root / "manifest.json"
        source = root / "source.jpg"
        source.write_bytes(b"source")
        output = root / "output.webp"
        output.write_bytes(b"output")
        self.enterContext(patch.object(self.generator, "STATIC_DIR", root))
        self.enterContext(
            patch.object(self.generator, "MANIFEST_PATH", self.manifest_path)
        )
        self.enterContext(
            patch.object(self.generator, "sources", return_value=[source])
        )
        self.enterContext(patch.object(self.generator, "GM_BINARY", None))
        self.manifest = self.generator.build_manifest([output])

    def write_manifest(self):
        """Save the fixture for verification through the real check function."""
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_current_settings(self):
        """Matching settings and hashes pass without an image converter."""
        self.write_manifest()
        self.generator.check()

    def test_changed_settings(self):
        """Reject stale quality, method and width settings."""
        for key, value in (
            ("jpeg_quality", 85),
            ("webp_quality", 82),
            ("webp_method", 4),
            ("widths", [480, 800]),
        ):
            with self.subTest(setting=key):
                self.manifest["settings"] = self.generator.encoding_settings()
                self.manifest["settings"][key] = value
                self.write_manifest()
                with self.assertRaisesRegex(SystemExit, "settings changed; regenerate"):
                    self.generator.check()

    def test_missing_method(self):
        """Manifests from before explicit WebP methods require regeneration."""
        del self.manifest["settings"]["webp_method"]
        self.write_manifest()
        with self.assertRaisesRegex(SystemExit, "settings changed; regenerate"):
            self.generator.check()

    def test_missing_settings(self):
        """A manifest without settings cannot silently pass verification."""
        del self.manifest["settings"]
        self.write_manifest()
        with self.assertRaisesRegex(SystemExit, "settings changed; regenerate"):
            self.generator.check()
