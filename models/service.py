from odoo import api, fields, models

class CallCenterService(models.Model):
    _name = "call.center.service"
    _description = "Customer Service (CRM)"

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

class ResPartner(models.Model):
    _inherit = "res.partner"
    service_ids = fields.One2many("call.center.service", "partner_id", string="Mijoz servislar")
