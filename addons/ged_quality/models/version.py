from odoo import fields, models, api
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class Version(models.Model):
    _name = 'ged_quality.document.version'
    _description = 'GED Quality Document Version'
    _inherit = ['mail.thread']

    document_id = fields.Many2one('ged_quality.document', string='Document', required=True, ondelete='cascade')
    version_number = fields.Integer(
        'Version number',
        compute='_compute_version_number',
        store=True,
        readonly=True,
        copy=False
    )
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True)
    writer_id = fields.Many2one('res.users', string='Writer', required=True)
    verifier_id = fields.Many2one('res.users', string='Verifier')
    approver_id = fields.Many2one('res.users', string='Approver')
    state = fields.Selection([
            ('drafting', 'Drafting'),
            ('pending_verification', 'Pending verification'),
            ('pending_approval', 'Pending approval'),
            ('applicable', 'Applicable'),
            ('archived', 'Archived'),
        ],
        default='drafting',
        string='State',
        required=True
    )

    _sql_constraints = [
        ('unique_document_version', 'UNIQUE(document_id, version_number)', 'This version number already exists for this document.')
    ]

    @api.depends('document_id')
    def _compute_version_number(self):
        for record in self:
            if record.version_number:
                continue

            if record.document_id:
                existing_versions = record.document_id.version_ids.filtered(lambda v: v.id != record.id)

                if existing_versions:
                    max_v = max(existing_versions.mapped('version_number') or [0])
                    _logger.error(f"Max version for document {record.document_id.id} is {max_v}")
                    record.version_number = max_v + 1
                else:
                    record.version_number = 1
            else:
                record.version_number = 1

    def name_get(self):
        result = []

        for record in self:
            result.append(
                (record.id, f"Version {record.version_number:02d}")
            )

        return result

    def action_submit_verification(self):
        for record in self:
            if record.state != 'drafting':
                raise UserError(
                    'Only drafting versions can be submitted.'
                )

            record.state = 'pending_verification'

    def action_verify(self):
        for record in self:
            if record.verifier_id != self.env.user:
                raise UserError(
                    'Only the assigned verifier can verify.'
                )

            if record.state != 'pending_verification':
                raise UserError(
                    'Version must be pending verification.'
                )

            record.state = 'pending_approval'

    def action_approve_release(self):
        for record in self:
            if record.approver_id != self.env.user:
                raise UserError(
                    'Only the assigned approver can approve.'
                )

            if record.state != 'pending_approval':
                raise UserError(
                    'Version must be pending approval.'
                )

            previous_versions = self.search([
                ('document_id', '=', record.document_id.id),
                ('id', '!=', record.id),
                ('state', '=', 'applicable'),
                ('version_number', '=', record.version_number - 1),
            ])

            previous_versions.write({
                'state': 'archived'
            })

            record.state = 'applicable'

        self.env.cr.flush()
