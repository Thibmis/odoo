from odoo import fields, models, api
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class Document(models.Model):
    _name = 'ged_quality.document'
    _description = 'GED Quality Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    reference = fields.Char('Reference', required=True)
    document_type = fields.Selection([
            ('mmq', 'MMQ'),
            ('procedure', 'Procedure'),
            ('instruction', 'Instruction'),
            ('method', 'Method'),
            ('form_record', 'Form/Record'),
        ],
        default='mmq',
        string='Document Type',
        required=True
    )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('in_progress', 'In progress'),
            ('applicable', 'Applicable'),
            ('archived', 'Archived'),
        ],
        default='draft',
        string='State',
        required=True
    )

    version_ids = fields.One2many('ged_quality.document.version', 'document_id', string='Versions')

    current_version_id = fields.Many2one(
        'ged_quality.document.version',
        compute='_compute_current_version_id',
        store=True,
        string='Current Version',
    )

    _sql_constraints = [
        ('unique_reference', 'UNIQUE(reference)', 'Reference already exists.')
    ]

    @api.constrains('reference')
    def _check_unique_reference(self):
        for record in self:
            existing = self.search([
                ('reference', '=', record.reference),
                ('id', '!=', record.id)
            ], limit=1)

            if existing:
                raise UserError('Reference already exists.')

    @api.depends('version_ids.state', 'version_ids.version_number')
    def _compute_current_version_id(self):
        for document in self:
            applicable_versions = document.version_ids.filtered(
                lambda v: v.state == 'applicable'
            )

            document.current_version_id = (
                max(applicable_versions, key=lambda v: v.version_number)
                if applicable_versions
                else False
            )

    def name_get(self):
        result = []
        for record in self:
            version = (
                record.current_version_id.version_number
                if record.current_version_id
                else 0
            )

            name = f"{record.name} V{version:02d}"
            result.append((record.id, name))

        return result
