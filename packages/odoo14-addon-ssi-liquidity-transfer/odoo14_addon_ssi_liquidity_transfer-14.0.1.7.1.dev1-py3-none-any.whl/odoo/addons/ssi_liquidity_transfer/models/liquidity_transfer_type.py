# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LiquiityTransferType(models.Model):
    _name = "liquidity_transfer_type"
    _inherit = [
        "mixin.master_data",
        "mixin.account_account_m2o_configurator",
        "mixin.account_journal_m2o_configurator",
        "mixin.res_partner_m2o_configurator",
    ]
    _description = "Liquidity Transfer Type"
    _account_account_m2o_configurator_insert_form_element_ok = True
    _account_account_m2o_configurator_form_xpath = "//page[@name='account']"
    _account_journal_m2o_configurator_insert_form_element_ok = True
    _account_journal_m2o_configurator_form_xpath = "//page[@name='account']"
    _res_partner_m2o_configurator_insert_form_element_ok = True
    _res_partner_m2o_configurator_form_xpath = "//page[@name='custodian']"

    account_ids = fields.Many2many(
        relation="rel_liquidity_transfer_type_2_account",
    )
    journal_ids = fields.Many2many(
        relation="rel_liquidity_transfer_type_2_journal",
    )
    partner_ids = fields.Many2many(
        relation="rel_liquidity_transfer_type_2_partner",
    )
    account_id = fields.Many2one(
        string="Default Transfer Account",
        comodel_name="account.account",
        required=True,
    )
    transfer_amount_method = fields.Selection(
        string="Transfer Amount Method",
        selection=[
            ("free", "Free Amount"),
            ("aml", "Based On Transaction"),
        ],
        default="free",
        required=True,
    )
