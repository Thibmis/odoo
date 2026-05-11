from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError


class TestGedDocument(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ged_document = self.env['ged_quality.document']

    def test_create(self):
        """
        Ensure document reference is unique.
        """
        record = self.ged_document.create({'name': 'DocumentName', 'reference': 'docref', 'document_type': 'mmq', 'state': 'draft'})
        self.assertEqual(
            record.name,
            'DocumentName')
        self.assertEqual(
            record.reference,
            'docref')
        self.assertEqual(
            record.document_type,
            'mmq')
        self.assertEqual(
            record.state,
            'draft')

    def test_reference_uniqueness(self):
        """
        Ensure document reference is unique.
        """

        self.ged_document.create({
            'name': 'Document 1',
            'reference': 'PG-01',
            'document_type': 'mmq',
            'state': 'draft',
        })

        with self.assertRaises(IntegrityError):
            self.ged_document.create({
                'name': 'Document 2',
                'reference': 'PG-01',
                'document_type': 'procedure',
                'state': 'draft',
            })
