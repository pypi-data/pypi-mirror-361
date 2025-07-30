# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line"]

    liquidity_transfer_id = fields.Many2one(
        string="# Liquidity Transfer",
        comodel_name="liquidity_transfer",
    )
