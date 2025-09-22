# addons/<your_module>/models/res_partner_calls.py
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    # single source of truth for the UI smart-button
    call_total_count = fields.Integer(
        string="Qo'ng'iroqlar",
        compute="_compute_call_total_count",
        store=False,
    )

    @api.depends()
    def _compute_call_total_count(self):
        # default to 0
        for rec in self:
            rec.call_total_count = 0

        if not self.ids or "utel.call" not in self.env:
            return

        Call = self.env["utel.call"].sudo()
        # count calls per partner (all types), respecting multi-company via record rules
        groups = Call.read_group(
            domain=[("partner_id", "in", self.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )
        counts = {g["partner_id"][0]: g["partner_id_count"] for g in groups}
        for rec in self:
            rec.call_total_count = counts.get(rec.id, 0)

    def action_open_partner_calls(self):
        self.ensure_one()
        if "utel.call" not in self.env:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": "Qo'ng'iroqlar",
            "res_model": "utel.call",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
            "target": "current",
        }
