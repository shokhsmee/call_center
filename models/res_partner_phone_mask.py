# -*- coding: utf-8 -*-
from odoo import api, models

# --- Local helpers (no cross-module import) ---
def _digits_only(num):
    return "".join(ch for ch in str(num or "") if ch.isdigit())

def _uz_digits(d):
    """
    Uzbekistan raqami digits-only ko'rinish:
    9 xonali (90xxxxxxx) bo'lsa 998 prefiksini qo'shamiz.
    12 xonali 998... bo'lsa o'sha holicha.
    """
    if not d:
        return ""
    s = _digits_only(d)
    if len(s) == 9:
        return "998" + s
    return s

def _format_uz_pretty(digits):
    """
    '99890xxxxxxx' -> '+998 90 xxx xx xx'
    Aks holda: '+<digits>'
    """
    s = _digits_only(digits)
    if len(s) == 12 and s.startswith("998"):
        n = s[3:]  # 90xxxxxxx (9 xonali)
        return f"+998 {n[0:2]} {n[2:5]} {n[5:7]} {n[7:9]}"
    return f"+{s}" if s else ""

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _mask_if_uz(self, vals, field):
        """vals[field] bor bo'lsa, UZ bo'lsa masklab beradi."""
        raw = vals.get(field)
        if not raw:
            return vals
        d = _uz_digits(_digits_only(raw))
        if len(d) == 12 and d.startswith("998"):
            vals[field] = _format_uz_pretty(d)
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._mask_if_uz(vals, "phone")
            self._mask_if_uz(vals, "mobile")
        return super().create(vals_list)

    def write(self, vals):
        # copy emas; Odoo write ichida dict ni o'zgartirish normal
        self._mask_if_uz(vals, "phone")
        self._mask_if_uz(vals, "mobile")
        return super().write(vals)
