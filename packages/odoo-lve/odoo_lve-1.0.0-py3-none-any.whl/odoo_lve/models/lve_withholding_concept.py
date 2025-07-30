from odoo import fields, models


class LVEWithholdingConcept(models.Model):
    _name = "lve_withholding_concept"
    _description = "Withholding Concept"

    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)
    lve_withholding_type_id = fields.Many2one(
        "lve_withholding_type", string="Withholding Type"
    )
