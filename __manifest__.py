{
    "name": "Call Center",
    "version": "18.0.1.0.0",
    "summary": "Contact form tailored for call center workflow",
    "author": "Shohjahon Obruyev",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "crm", "sale", "utel_integration", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_default.xml",
        "data/uz_states.xml",
        "data/sequence.xml",
        "views/service_views.xml",
        "views/res_partner_views.xml",
        # "views/res_partner_buttons.xml",  # optional – comment out to remove stat button
        # "views/res_partner_chatter.xml",    # <-- add this line
    ],

    "application": False,
}
