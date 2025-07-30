# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class LiquidityTransfer(models.Model):
    _name = "liquidity_transfer"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.many2one_configurator",
        "mixin.company_currency",
        "mixin.transaction_account_move_with_field",
        "mixin.account_move_double_line_with_field",
    ]
    _description = "Liquidity Transfer"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False
    _automatically_insert_open_policy_fields = False
    _automatically_insert_open_button = False

    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_open",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    # account.move.line
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"  # TODO
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _number_field_name = "name"

    # Debit ML Attribute
    _debit_account_id_field_name = "account_id"
    _debit_partner_id_field_name = "custodian_id"
    _debit_analytic_account_id_field_name = False
    _debit_label_field_name = "name"
    _debit_product_id_field_name = False
    _debit_uom_id_field_name = False
    _debit_quantity_field_name = False
    _debit_price_unit_field_name = False
    _debit_currency_id_field_name = "currency_id"
    _debit_company_currency_id_field_name = "company_currency_id"
    _debit_amount_currency_field_name = "transfer_amount"
    _debit_company_id_field_name = "company_id"
    _debit_date_field_name = "date"
    _debit_need_date_due = False
    _debit_date_due_field_name = False

    # Credit ML Attribute
    _credit_account_id_field_name = "account_id"
    _credit_partner_id_field_name = "custodian_id"
    _credit_analytic_account_id_field_name = False
    _credit_label_field_name = "name"
    _credit_product_id_field_name = False
    _credit_uom_id_field_name = False
    _credit_quantity_field_name = False
    _credit_price_unit_field_name = False
    _credit_currency_id_field_name = "currency_id"
    _credit_company_currency_id_field_name = "company_currency_id"
    _credit_amount_currency_field_name = "transfer_amount"
    _credit_company_id_field_name = "company_id"
    _credit_date_field_name = "date"
    _credit_need_date_due = False
    _credit_date_due_field_name = False

    date = fields.Date(
        string="Date",
        default=lambda r: r._default_date(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="liquidity_transfer_type",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    custodian_id = fields.Many2one(
        string="Custodian",
        comodel_name="res.partner",
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    transfer_amount_method = fields.Selection(
        related="type_id.transfer_amount_method",
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_account_ids",
        store=False,
    )
    allowed_journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        compute="_compute_allowed_journal_ids",
        store=False,
    )
    allowed_partner_ids = fields.Many2many(
        string="Allowed Partners",
        comodel_name="res.partner",
        compute="_compute_allowed_partner_ids",
        store=False,
    )
    reference_move_line_ids = fields.One2many(
        string="Reference Move Lines",
        comodel_name="account.move.line",
        inverse_name="liquidity_transfer_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    aml_amount = fields.Monetary(
        string="Reference Amount",
        compute="_compute_aml_amount",
        store=True,
    )
    journal_account_id = fields.Many2one(
        related="journal_id.default_account_id",
    )
    transfer_amount = fields.Monetary(
        string="Amount",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    @api.model
    def _default_date(self):
        return fields.Date.today()

    @api.depends(
        "reference_move_line_ids",
        "reference_move_line_ids.amount_currency",
    )
    def _compute_aml_amount(self):
        for record in self:
            result = 0.0
            for aml in record.reference_move_line_ids:
                result += aml.amount_currency
            record.aml_amount = result

    @api.depends("type_id")
    def _compute_allowed_account_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.account",
                    method_selection=record.type_id.account_selection_method,
                    manual_recordset=record.type_id.account_ids,
                    domain=record.type_id.account_domain,
                    python_code=record.type_id.account_python_code,
                )
            record.allowed_account_ids = result

    @api.depends("type_id")
    def _compute_allowed_partner_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.partner",
                    method_selection=record.type_id.partner_selection_method,
                    manual_recordset=record.type_id.partner_ids,
                    domain=record.type_id.partner_domain,
                    python_code=record.type_id.partner_python_code,
                )
            record.allowed_partner_ids = result

    @api.depends("type_id")
    def _compute_allowed_journal_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.journal",
                    method_selection=record.type_id.journal_selection_method,
                    manual_recordset=record.type_id.journal_ids,
                    domain=record.type_id.journal_domain,
                    python_code=record.type_id.journal_python_code,
                )
            record.allowed_journal_ids = result

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    @api.onchange(
        "journal_id",
    )
    def onchange_currency_id(self):
        self.currency_id = False
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_currency_id

    @api.onchange(
        "aml_amount",
        "transfer_amount_method",
    )
    def onchange_transfer_amount(self):
        self.transfer_amount = 0.0
        if self.transfer_amount_method == "aml":
            self.transfer_amount = self.aml_amount

    @api.onchange(
        "type_id",
    )
    def onchange_account_id(self):
        self.account_id = False
        if self.type_id:
            self.account_id = self.type_id.account_id

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_custodian_id(self):
        self.custodian_id = False

    @api.model
    def _get_policy_field(self):
        res = super(LiquidityTransfer, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.post_cancel_action()
    def _01_clear_reference_aml(self):
        self.ensure_one()
        self.reference_move_line_ids.write(
            {
                "liquidity_transfer_id": False,
            }
        )

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @ssi_decorator.post_open_action()
    def _01_create_accounting_entry(self):
        if self.move_id:
            return True

        self._create_standard_move()  # Mixin
        debit_ml, credit_ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "debit_result_move_line_id": debit_ml.id,
                "credit_result_move_line_id": credit_ml.id,
            }
        )
        self._post_standard_move()  # Mixin

    @ssi_decorator.post_cancel_action()
    def _02_delete_accounting_entry(self):
        self.ensure_one()
        self._delete_standard_move()  # Mixin
