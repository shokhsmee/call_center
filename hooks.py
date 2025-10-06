def post_init_fill_service_numbers(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID, {})
    Service = env["call.center.service"].sudo()
    missing = Service.search([("service_number", "=", False)]) | Service.search([("service_number", "=", "/")])
    if not missing:
        return
    seq = env["ir.sequence"]
    code = "call.center.service.number"
    for rec in missing:
        rec.service_number = seq.next_by_code(code)
