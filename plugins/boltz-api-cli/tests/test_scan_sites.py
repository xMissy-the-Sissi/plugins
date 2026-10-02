from __future__ import annotations

import importlib.util
import itertools
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


class MockArray:
    def __init__(self, data):
        self.data = list(data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self

    def min(self, axis=None):
        if not self.data:
            return 0.0
        if axis == 0:
            xs = [p[0] for p in self.data]
            ys = [p[1] for p in self.data]
            zs = [p[2] for p in self.data]
            return MockArray([min(xs), min(ys), min(zs)])
        if isinstance(self.data[0], (int, float)):
            return min(self.data)
        if isinstance(self.data[0], MockArray):
            return min(a.min() for a in self.data)
        return min(self.data)

    def max(self, axis=None):
        if not self.data:
            return 0.0
        if axis == 0:
            xs = [p[0] for p in self.data]
            ys = [p[1] for p in self.data]
            zs = [p[2] for p in self.data]
            return MockArray([max(xs), max(ys), max(zs)])
        return max(self.data)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return MockArray([x - other for x in self.data])
        if isinstance(other, MockArray):
            if len(other.data) > 0 and isinstance(other.data[0], (int, float)):
                return MockArray([[a - b for a, b in zip(pt, other.data)] for pt in self.data])
            res = []
            for p1 in self.data:
                row = []
                for p2 in other.data:
                    row.append([a - b for a, b in zip(p1, p2)])
                res.append(MockArray(row))
            return MockDiffArray(res)
        return self

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return MockArray([x + other for x in self.data])
        return self

    def __lt__(self, other):
        if isinstance(other, MockArray):
            return [a < b for a, b in zip(self.data, other.data)]
        if isinstance(other, (int, float)):
            return [a < other for a in self.data]
        return False

    def __gt__(self, other):
        if isinstance(other, MockArray):
            return [a > b for a, b in zip(self.data, other.data)]
        if isinstance(other, (int, float)):
            return [a > other for a in self.data]
        return False


class MockDiffArray:
    def __init__(self, rows):
        self.rows = rows

    def __pow__(self, power):
        res = []
        for row in self.rows:
            r = []
            for p in row.data:
                r.append([x ** power for x in p])
            res.append(r)
        return MockDiffArrayPow(res)


class MockDiffArrayPow:
    def __init__(self, rows):
        self.rows = rows

    def sum(self, axis=-1):
        res = []
        for row in self.rows:
            r = [sum(p) for p in row]
            res.append(MockArray(r))
        return MockArray(res)


class MockNumpy:
    @staticmethod
    def vstack(arrays):
        if not arrays:
            raise ValueError("need at least one array to concatenate")
        flat = []
        for a in arrays:
            flat.extend(a.data if isinstance(a, MockArray) else a)
        return MockArray(flat)

    @staticmethod
    def any(vals):
        return any(vals)

    @staticmethod
    def array(data, dtype=float):
        return MockArray(data)


gemmi_mock = types.ModuleType("gemmi")

def load_script_module(script_name: str, common: types.ModuleType, np_module: types.ModuleType) -> types.ModuleType:
    scripts_dir = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "boltz-protein-design"
        / "scripts"
    )
    script_path = scripts_dir / script_name
    dependencies = {
        "_common": common,
        "gemmi": gemmi_mock,
        "numpy": np_module,
    }
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, dependencies):
        spec.loader.exec_module(module)
    return module


common_mock = types.ModuleType("_common")
common_mock.atom_coords = lambda res: getattr(res, "coords", MockArray([[0.0, 0.0, 0.0]]))
common_mock.indexed_residues = lambda poly: ([(i, r) for i, r in enumerate(poly)], True)
common_mock.load_chain = None

np_mock = MockNumpy()

scan_sites = load_script_module("scan_sites.py", common_mock, np_mock)
crop_radius = load_script_module("crop_radius.py", common_mock, np_mock)


class Chain:
    def __init__(self, name: str) -> None:
        self.name = name


class ResidueMock:
    def __init__(self, coords):
        self.coords = MockArray(coords)


class ScanSitesTest(unittest.TestCase):
    def test_site_clustering_merges_transitive_bridges_in_any_order(self) -> None:
        footprints = [{1, 2}, {3, 4}, {2, 3}]
        for permutation in itertools.permutations(footprints):
            with self.subTest(permutation=permutation):
                self.assertEqual(
                    scan_sites.cluster_sites(permutation, 0.25), [[0, 1, 2]]
                )

    def test_explicit_binder_chain_excludes_other_target_chains(self) -> None:
        model = [Chain("A"), Chain("B"), Chain("C")]
        self.assertEqual(scan_sites._binder_chain_names(model, "A", ["B"]), {"B"})

    def test_single_non_target_chain_is_inferred(self) -> None:
        model = [Chain("A"), Chain("B")]
        self.assertEqual(scan_sites._binder_chain_names(model, "A"), {"B"})

    def test_ambiguous_binder_chains_fail_closed(self) -> None:
        model = [Chain("A"), Chain("B"), Chain("C")]
        with self.assertRaisesRegex(ValueError, "binder chains are ambiguous"):
            scan_sites._binder_chain_names(model, "A")

    def test_target_chain_cannot_be_selected_as_binder(self) -> None:
        model = [Chain("A"), Chain("B")]
        with self.assertRaisesRegex(ValueError, "cannot also be a binder"):
            scan_sites._binder_chain_names(model, "A", ["A"])

    def test_missing_binder_chain_is_rejected(self) -> None:
        model = [Chain("A"), Chain("B")]
        with self.assertRaisesRegex(ValueError, r"binder chain\(s\) C not found"):
            scan_sites._binder_chain_names(model, "A", ["C"])

    def test_crop_within_prunes_distant_residues_and_keeps_site(self) -> None:
        pairs = [
            (0, ResidueMock([[0.0, 0.0, 0.0]])),
            (1, ResidueMock([[0.0, 0.0, 5.0]])),
            (2, ResidueMock([[0.0, 0.0, 20.0]])),
            (3, ResidueMock([[100.0, 100.0, 100.0]])),
        ]
        site = {0}
        radius = 10.0
        kept = crop_radius.crop_within(pairs, site, radius)
        self.assertEqual(kept, [0, 1])

    def test_crop_within_empty_site(self) -> None:
        pairs = [(0, ResidueMock([[0.0, 0.0, 0.0]]))]
        kept = crop_radius.crop_within(pairs, set(), 10.0)
        self.assertEqual(kept, [])

    def test_footprint_filters_contacted_residues(self) -> None:
        class PosMock:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z

        class AtomMock:
            def __init__(self, pos):
                self.pos = pos

        class ResMock:
            def __init__(self, atoms, label_seq=None):
                self._atoms = atoms
                self.label_seq = label_seq
                self.coords = MockArray([[a.pos.x, a.pos.y, a.pos.z] for a in atoms])
            def __iter__(self):
                return iter(self._atoms)

        class PolymerMock:
            def __init__(self, residues):
                self._residues = residues
            def __iter__(self):
                return iter(self._residues)

        class ChainMock:
            def __init__(self, name, residues):
                self.name = name
                self._residues = residues
            def get_polymer(self):
                return PolymerMock(self._residues)
            def __iter__(self):
                return iter(self._residues)

        target_chain = ChainMock("A", [
            ResMock([AtomMock(PosMock(0.0, 0.0, 0.0))], label_seq=1),
            ResMock([AtomMock(PosMock(0.0, 0.0, 5.0))], label_seq=2),
            ResMock([AtomMock(PosMock(0.0, 0.0, 50.0))], label_seq=3),
        ])
        binder_chain = ChainMock("B", [
            ResMock([AtomMock(PosMock(0.0, 0.0, 2.0))]),
        ])

        model = [target_chain, binder_chain]
        st_mock = mock.MagicMock()
        st_mock.__getitem__.return_value = model

        with mock.patch.object(gemmi_mock, "read_structure", create=True, return_value=st_mock):
            site = scan_sites.footprint("dummy.cif", "A", cutoff=6.0, binder_chains=["B"])
            self.assertEqual(site, {0, 1})


if __name__ == "__main__":
    unittest.main()
