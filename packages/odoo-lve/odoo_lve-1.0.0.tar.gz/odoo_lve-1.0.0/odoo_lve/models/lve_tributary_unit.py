from odoo import fields, models


class LVETributaryUnit(models.Model):
    _name = "lve_tributaryunit"
    _description = "Tributary Unit"

    name = fields.Char("Name", required=True)
    valid_from = fields.Date("Valid From", required=True, default=fields.Datetime.now())
    active = fields.Boolean("Active", default=True)
    description = fields.Char("Description", required=True)
    amount = fields.Float("Amount", required=True)
