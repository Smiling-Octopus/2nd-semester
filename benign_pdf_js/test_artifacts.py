"""Static structural checks; these do not execute JavaScript in a PDF viewer."""
import unittest
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import IndirectObject, DictionaryObject, ArrayObject

ROOT = Path(__file__).resolve().parent / 'artifacts'
FIELDS = {'test_status', 'viewer_type', 'viewer_version', 'viewer_variation'}


def inspect_objects(reader):
    seen = set()
    found = []
    def walk(value):
        if isinstance(value, IndirectObject):
            key = (value.idnum, value.generation)
            if key in seen:
                return
            seen.add(key)
            walk(value.get_object())
        elif isinstance(value, DictionaryObject):
            found.append(value)
            for v in value.values():
                walk(v)
        elif isinstance(value, (ArrayObject, list)):
            for v in value:
                walk(v)
    walk(reader.trailer)
    # Include unreferenced ordinary and object-stream entries as well.
    for gen, entries in reader.xref.items():
        if gen != 65535:
            for oid in entries:
                if oid:
                    walk(IndirectObject(oid, gen, reader))
    for oid in reader.xref_objStm:
        walk(IndirectObject(oid, 0, reader))
    return found


class ArtifactTests(unittest.TestCase):
    def test_pages_and_text(self):
        for name in ('control_no_js.pdf', 'benign_js_test.pdf'):
            r = PdfReader(ROOT / name)
            self.assertEqual(len(r.pages), 1)
            self.assertFalse(r.is_encrypted)
            text = r.pages[0].extract_text()
            self.assertIn('NOT_RUN' if name == 'control_no_js.pdf' else 'JS_EXECUTED', text)
            self.assertIn('About', text)

    def test_initial_fields_readonly(self):
        for name in ('control_no_js.pdf', 'benign_js_test.pdf'):
            fields = PdfReader(ROOT / name).get_fields()
            self.assertEqual(set(fields), FIELDS)
            for name, f in fields.items():
                self.assertEqual(f['/V'], 'NOT_RUN' if name == 'test_status' else 'UNKNOWN')
                self.assertEqual(f['/Ff'] & 1, 1)

    def test_control_no_actions(self):
        objects = inspect_objects(PdfReader(ROOT / 'control_no_js.pdf'))
        self.assertFalse(any('/JS' in obj or obj.get('/S') == '/JavaScript' for obj in objects))

    def test_active_exact_script(self):
        objects = inspect_objects(PdfReader(ROOT / 'benign_js_test.pdf'))
        scripts = [str(obj['/JS']) for obj in objects if '/JS' in obj]
        self.assertEqual(scripts, [(ROOT / 'test.js').read_text()])

    def test_no_external_actions_or_attachments(self):
        forbidden = {'/Launch', '/URI', '/GoToR', '/GoToE', '/SubmitForm', '/ImportData', '/Rendition', '/Movie', '/Sound'}
        forbidden_keys = {'/EmbeddedFiles', '/EF', '/RichMediaContent', '/XFA', '/AA'}
        for name in ('control_no_js.pdf', 'benign_js_test.pdf'):
            for obj in inspect_objects(PdfReader(ROOT / name)):
                self.assertNotIn(obj.get('/S'), forbidden)
                self.assertFalse(set(obj) & forbidden_keys)
                if '/S' in obj and '/JS' in obj:
                    self.assertEqual(obj['/S'], '/JavaScript')


if __name__ == '__main__':
    unittest.main()
