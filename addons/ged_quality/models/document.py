from odoo import fields, models, api
from odoo.exceptions import UserError

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
        string="Document Type",
        required=True
    )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('in_progress', 'In progress'),
            ('applicable', 'Applicable'),
            ('archived', 'Archived'),
        ],
        default='draft',
        string="State",
        required=True
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
                raise UserError("Reference already exists.")
