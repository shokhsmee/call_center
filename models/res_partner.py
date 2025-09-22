from odoo import api, fields, models, _
import re


class ResPartner(models.Model):
    _inherit = "res.partner"

    # --- Core fields ---
    phone = fields.Char(required=True)

    contact_type = fields.Selection([
        ("mijoz", "Mijoz"),
        ("hamkor", "Hamkor"),
        ("dokonchi", "Do'konchi"),
        ("diller", "Diller"),
    ], string="Kontakt turi")

    is_blocked = fields.Boolean(string="Bloklash")

    # CRM: all leads linked to this partner
    lead_ids = fields.One2many("crm.lead", "partner_id", string="CRM leadlar")

    # --- Header counters (stat buttons) ---
    service_count = fields.Integer(
        compute="_compute_counts", string="Servislar soni", compute_sudo=True
    )
    lead_count = fields.Integer(
        compute="_compute_counts", string="Leadlar soni", compute_sudo=True
    )

    # uTel call counters (NOTE: no @api.depends('id')!)
    call_in_count = fields.Integer(
        compute="_compute_call_counts", string="Kiruvchi qo'ng'iroqlar", compute_sudo=True
    )
    call_out_count = fields.Integer(
        compute="_compute_call_counts", string="Chiquvchi qo'ng'iroqlar", compute_sudo=True
    )
    call_total_count = fields.Integer(
        compute="_compute_call_counts", string="Qo'ng'iroqlar", compute_sudo=True
    )

    # --- Purchased/service products (your logic) ---
    purchased_product_ids = fields.Many2many(
        "product.product", compute="_compute_purchases_products",
        store=False, string="Mijoz haridlari",
    )
    service_product_ids = fields.Many2many(
        "product.product", compute="_compute_purchases_products",
        store=False, string="Mijoz servislar",
    )

    # ===================== COMPUTES =====================

    @api.depends("lead_ids")
    def _compute_counts(self):
        """Counts for services (call.center.service) and leads."""
        Lead = self.env["crm.lead"].sudo()
        lead_map = {
            d["partner_id"][0]: d["partner_id_count"]
            for d in Lead.read_group(
                [("partner_id", "in", self.ids)] if self.ids else [],
                ["partner_id"],
                ["partner_id"],
            )
        } if self.ids else {}

        if "call.center.service" in self.env and self.ids:
            Service = self.env["call.center.service"].sudo()
            svc_map = {
                d["partner_id"][0]: d["partner_id_count"]
                for d in Service.read_group(
                    [("partner_id", "in", self.ids)],
                    ["partner_id"],
                    ["partner_id"],
                )
            }
        else:
            svc_map = {}

        for rec in self:
            rec.lead_count = lead_map.get(rec.id, 0)
            rec.service_count = svc_map.get(rec.id, 0)

    @api.depends("sale_order_ids.state", "sale_order_ids.order_line.product_id")
    def _compute_purchases_products(self):
        SaleOrder = self.env["sale.order"].sudo()
        for partner in self:
            products = self.env["product.product"]
            services = self.env["product.product"]
            orders = SaleOrder.search([
                ("partner_id", "=", partner.id),
                ("state", "in", ["sale", "done"]),
            ], limit=0)
            for so in orders:
                for line in so.order_line:
                    if line.product_id:
                        products |= line.product_id
                        if line.product_id.detailed_type == "service":
                            services |= line.product_id
            partner.purchased_product_ids = products
            partner.service_product_ids = services

    from urllib.parse import quote
    from odoo import models
    from urllib.parse import quote

    def action_sip_call(self):
        self.ensure_one()
        number = (self.phone or "").strip().replace(" ", "")
        if not number:
            return False
        # navigate directly to the SIP protocol; stays in the same tab
        return {
            "type": "ir.actions.act_url",
            "url": f"sip:{quote(number, safe='+')}",
            "target": "self",
        }
    
    # NO @api.depends HERE (can't depend on 'id')
    def _compute_call_counts(self):
        """Count uTel calls per partner (incoming/outgoing/total)."""
        # reset first
        for rec in self:
            rec.call_in_count = rec.call_out_count = rec.call_total_count = 0

        if "utel.call" not in self.env or not self.ids:
            return

        Call = self.env["utel.call"].sudo()
        data = Call.read_group(
            domain=[("partner_id", "in", self.ids), ("type", "in", ["in", "out"])],
            fields=["partner_id"],
            groupby=["partner_id", "type"],
        )
        by_partner = {}
        for row in data:
            pid = row["partner_id"][0]
            cnt = row.get("partner_id_count") or row.get("__count", 0)
            tp = row.get("type")
            by_partner.setdefault(pid, {"in": 0, "out": 0})
            if tp in ("in", "out"):
                by_partner[pid][tp] = cnt

        for rec in self:
            ins = by_partner.get(rec.id, {}).get("in", 0)
            outs = by_partner.get(rec.id, {}).get("out", 0)
            rec.call_in_count = ins
            rec.call_out_count = outs
            rec.call_total_count = ins + outs

    # ===================== SIP CALL =====================

    def _sip_number(self):
        self.ensure_one()
        num = (self.phone or "").strip()
        return re.sub(r"\s+", "", num)

    def action_sip_call(self):
        self.ensure_one()
        number = self._sip_number()
        if not number:
            return False
        return {"type": "ir.actions.act_url", "url": f"sip:{number}", "target": "self"}

    # ===================== ACTIONS =====================

    def action_open_partner_services(self):
        """Open Services filtered by this partner (module optional)."""
        self.ensure_one()
        if "call.center.service" not in self.env:
            return False
        action = self.env.ref("call_center.action_call_center_service", raise_if_not_found=False)
        if action:
            act = action.read()[0]
            act["domain"] = [("partner_id", "=", self.id)]
            act["context"] = {"default_partner_id": self.id, "search_default_partner_id": self.id}
            return act
        return {
            "type": "ir.actions.act_window",
            "name": _("Mijoz servislar"),
            "res_model": "call.center.service",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }

    def action_open_partner_leads(self):
        self.ensure_one()
        action = self.env.ref("crm.crm_lead_all_leads", raise_if_not_found=False)
        if action:
            act = action.read()[0]
            act["domain"] = [("partner_id", "=", self.id)]
            act["context"] = {"default_partner_id": self.id, "search_default_partner_id": self.id}
            return act
        return {
            "type": "ir.actions.act_window",
            "name": _("CRM leadlar"),
            "res_model": "crm.lead",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }

    def action_open_partner_calls(self):
        """Open uTel calls filtered by this partner."""
        self.ensure_one()
        if "utel.call" not in self.env:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Qo'ng'iroqlar"),
            "res_model": "utel.call",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
        
