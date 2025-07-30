from odoo import fields, models
from . import lve_utils


class LVEWithholdingRate(models.Model):
    _name = "lve_withholding_rate"
    _description = "Withholding Rate"

    code = fields.Char("Code", required=True)
    active = fields.Boolean("Active", default=True)
    withholding_rate = fields.Float(string="Withholding Rate", required=True, default=0)
    lve_person_type = fields.Selection(
        string="Person Type", selection=lve_utils.person_type_selection, required=False
    )
    valid_from = fields.Date("Valid From", required=True, default=fields.Datetime.now())
    tributary_units_restriction = fields.Boolean(
        "Tributary Units Restriction", default=False
    )
    min_tributary_units = fields.Integer(
        string="Minimum Tributary Units", required=True, default=0
    )
    max_tributary_units = fields.Integer(
        string="Maximum Tributary Units", required=True, default=0
    )
    lve_withholding_concept_id = fields.Many2one(
        string="Withholding Concept", comodel_name="lve_withholding_concept"
    )
    account_tax_ids = fields.Many2many(
        string="Taxes",
        comodel_name="account.tax",
        relation="lve_withholding_rate_tax",
        column2="account_tax_id",
        check_company=True,
    )
