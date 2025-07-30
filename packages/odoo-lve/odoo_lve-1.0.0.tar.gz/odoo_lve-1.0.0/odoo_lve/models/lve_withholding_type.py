from odoo import fields, models


class LVEWithholdingType(models.Model):
    _name = "lve_withholding_type"
    _description = "Withholding Type"

    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)
