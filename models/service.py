from odoo import api, fields, models

class CallCenterService(models.Model):
    _name = "call.center.service"
    _description = "Customer Service (CRM)"
    _order = "id desc"

    # NEW: sequential number (6 digits, starts at 100000)
    service_number = fields.Char(
        string="Service #",
        copy=False,
        readonly=True,
        index=True,
        required=True,
        default="/",
    )

    name = fields.Char("Service name", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Related product")
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([
        ("active", "Active"),
        ("paused", "Paused"),
        ("ended", "Ended"),
    ], default="active", string="Status")
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        code = "call.center.service.number"
        for vals in vals_list:
            # let imports/tests pass if explicitly provided
            if not vals.get("service_number") or vals["service_number"] == "/":
                vals["service_number"] = seq.next_by_code(code) or "/"
        return super().create(vals_list)
