# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move"]

    payment_order_id = fields.Many2one(
        string="Payment Order",
        comodel_name="payment_order",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
