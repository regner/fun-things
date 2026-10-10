"""Focused tests for tracked Godot saved-identity enforcement."""

from pathlib import Path
import struct
import tempfile
import unittest

from saved_identity_check import ALLOWLIST, collect_findings


class SavedIdentityCheckTest(unittest.TestCase):
    def test_valid_scene_accepts_matching_dependencies_and_placeholder_exception(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "scripts/owner.gd", "extends Node\n")
            self._write(root, "scripts/owner.gd.uid", "uid://script1\n")
            self._write(
                root,
                "resources/definition.tres",
                '[gd_resource type="Resource" format=3 uid="uid://resource1"]\n',
            )
            self._write(
                root,
                "scene.tscn",
                "\n".join(
                    [
                        '[gd_scene format=3 uid="uid://scene1"]',
                        "",
                        '[ext_resource type="Script" uid="uid://script1" '
                        'path="res://scripts/owner.gd" id="1"]',
                        '[ext_resource type="Resource" uid="uid://resource1" '
                        'path="res://resources/definition.tres" id="2"]',
                        "",
                        '[node name="Root" type="Node" unique_id=1]',
                        '[node name="Deferred" type="Node" parent="." '
                        'instance_placeholder="res://deferred.tscn"]',
                        "",
                    ]
                ),
            )
            tracked = [
                "resources/definition.tres",
                "scene.tscn",
                "scripts/owner.gd",
                "scripts/owner.gd.uid",
            ]

            findings = collect_findings(root, tracked)

        self.assertEqual(findings, [])

    def test_reports_exact_lines_for_every_identity_category(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "scripts/missing.gd", "extends Node\n")
            self._write(root, "scripts/wrong.gd", "extends Node\n")
            self._write(root, "scripts/wrong.gd.uid", "not-a-uid\n")
            self._write(root, "resources/target.tres", '[gd_resource format=3 uid="uid://right1"]\n')
            self._write(
                root,
                "broken.tscn",
                "\n".join(
                    [
                        "[gd_scene format=3]",
                        '[ext_resource type="Resource" path="res://resources/target.tres" id="1"]',
                        '[ext_resource type="Resource" uid="uid://wrong1" '
                        'path="res://resources/target.tres" id="2"]',
                        '[node name="Root" type="Node"]',
                        "",
                    ]
                ),
            )
            tracked = [
                "broken.tscn",
                "resources/target.tres",
                "scripts/missing.gd",
                "scripts/wrong.gd",
                "scripts/wrong.gd.uid",
            ]

            rendered = [finding.format() for finding in collect_findings(root, tracked)]

        self.assertIn("broken.tscn:1: missing or invalid saved resource header UID", rendered)
        self.assertIn("broken.tscn:2: external resource has no UID", rendered)
        self.assertTrue(
            any(
                row.startswith("broken.tscn:3: dependency UID uid://wrong1 does not match")
                for row in rendered
            )
        )
        self.assertIn("broken.tscn:4: node has no unique_id", rendered)
        self.assertIn(
            "scripts/missing.gd:1: tracked GDScript has no tracked .gd.uid",
            rendered,
        )
        self.assertIn("scripts/wrong.gd.uid:1: missing or invalid GDScript UID", rendered)

    def test_empty_referenced_resource_reports_both_exact_locations(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "resources/empty.tres", "")
            self._write(
                root,
                "scene.tscn",
                "\n".join(
                    [
                        '[gd_scene format=3 uid="uid://scene1"]',
                        '[ext_resource type="Resource" uid="uid://missing1" '
                        'path="res://resources/empty.tres" id="1"]',
                        '[node name="Root" type="Node" unique_id=1]',
                        "",
                    ]
                ),
            )

            rendered = [
                finding.format()
                for finding in collect_findings(
                    root,
                    ["resources/empty.tres", "scene.tscn"],
                )
            ]

        self.assertIn(
            "resources/empty.tres:1: missing or invalid saved resource header UID",
            rendered,
        )
        self.assertIn(
            "scene.tscn:2: dependency has no tracked UID metadata: "
            "res://resources/empty.tres",
            rendered,
        )

    def test_matches_binary_resource_header_uid(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            uid = 8980820833686374502
            resource = bytearray(b"RSRC" + b"\0" * 20)
            resource.extend(struct.pack("<I", 10))
            resource.extend(b"ArrayMesh\0")
            resource.extend(b"\0" * 8)
            resource.extend(struct.pack("<I", 3))
            resource.extend(struct.pack("<Q", uid))
            (root / "mesh.res").write_bytes(resource)
            self._write(
                root,
                "scene.tscn",
                "\n".join(
                    [
                        '[gd_scene format=3 uid="uid://scene1"]',
                        '[ext_resource type="ArrayMesh" uid="uid://d07m2o58fqeok" '
                        'path="res://mesh.res" id="1"]',
                        '[node name="Root" type="Node" unique_id=1]',
                        "",
                    ]
                ),
            )

            findings = collect_findings(root, ["mesh.res", "scene.tscn"])

        self.assertEqual(findings, [])

    def test_excludes_vendor_history_and_temporary_allowlist(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [
                "addons/vendor/broken.tscn",
                "docs/history/broken.tscn",
                "prototypes/old/broken.tscn",
                next(iter(ALLOWLIST)),
            ]

            findings = collect_findings(root, paths)

        self.assertEqual(findings, [])

    @staticmethod
    def _write(root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
