import json
import unittest
from pathlib import Path

# Run tests from project root
# python -m scripts.tests.test_valueset_licensing

CPT_SYSTEM = 'http://www.ama-assn.org/go/cpt'
CPT_MAX_CODES = 1000

EXTERNAL_VALUESETS = Path('input/vocabulary/valueset/external')


def _expansion_codes(valueset):
    """Return the expansion.contains list, or [] when there is no expansion."""
    return (valueset.get('expansion') or {}).get('contains') or []


def _contains_cpt(codes):
    return any(code.get('system') == CPT_SYSTEM for code in codes)


class TestValueSetLicensing(unittest.TestCase):
    """Guards the AMA licensing restriction on CPT-bearing valuesets.

    A valueset containing CPT codes may not be committed with more than 1000
    expanded entries. This is a licensing restriction imposed by the AMA, not a
    technical limit, so it cannot be relaxed by changing tooling. It is why the
    I-03 expansion repair was deliberately scoped to non-CPT valuesets.
    """

    @classmethod
    def setUpClass(cls):
        cls.valuesets = []
        for path in sorted(EXTERNAL_VALUESETS.glob('*.json')):
            with open(path) as handle:
                cls.valuesets.append((path, json.load(handle)))

    def test_external_valueset_directory_is_present(self):
        """Guard against the test silently passing on an empty glob."""
        self.assertTrue(EXTERNAL_VALUESETS.is_dir(), f'missing {EXTERNAL_VALUESETS}')
        self.assertGreater(len(self.valuesets), 0, 'no external valuesets found')

    def test_cpt_valuesets_do_not_exceed_1000_codes(self):
        """No CPT-bearing valueset may exceed the AMA 1000-entry cap."""
        violations = []
        for path, valueset in self.valuesets:
            codes = _expansion_codes(valueset)
            if _contains_cpt(codes) and len(codes) > CPT_MAX_CODES:
                violations.append(f'{path.name}: {len(codes)} codes')
        self.assertEqual(
            [], violations,
            'CPT valuesets over the AMA 1000-code cap:\n  ' + '\n  '.join(violations),
        )

    def test_hypoglycemics_treatment_medications_is_present(self):
        """I-44: CMS871 needs 2.16.840.1.113762.1.4.1196.394 committed.

        It was marked Fixed for weeks while the file had never been committed,
        and the engine threw `Unable to locate ValueSet ...1196.394` on every
        run. This pins it so the regression cannot recur silently.
        """
        oid = '2.16.840.1.113762.1.4.1196.394'
        matches = [vs for _, vs in self.valuesets if vs.get('id', '').startswith(oid)]
        self.assertEqual(1, len(matches), f'expected exactly one valueset for {oid}')

        expansion = matches[0].get('expansion') or {}
        codes = _expansion_codes(matches[0])
        self.assertEqual(expansion.get('total'), len(codes),
                         'expansion is truncated: contains < total')
        self.assertFalse(_contains_cpt(codes), 'unexpected CPT codes in an RxNorm valueset')


if __name__ == '__main__':
    unittest.main()
