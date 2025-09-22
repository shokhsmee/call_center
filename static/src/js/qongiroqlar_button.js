/** @odoo-module **/

import { registry } from "@web/core/registry";

console.log("%c[call_center] qongiroqlar_button.js loaded", "color: green; font-weight: bold");

const qongiroqlarService = {
    dependencies: ["action"],
    start(env, { action }) {
        async function openForCurrentRecord(component) {
            const owner = component?.props?.chatter?.owner;
            console.log("[call_center] openForCurrentRecord owner =", owner);
            if (!owner || !owner.resModel || !owner.resId) return;
            if (owner.resModel !== "res.partner") return;

            await action.doAction({
                type: "ir.actions.act_window",
                name: "Qo'ng'iroqlar",
                res_model: "utel.call",                  // change if your model differs
                view_mode: "list,form",
                domain: [["partner_id", "=", owner.resId]],
                context: { default_partner_id: owner.resId },
                target: "current",
            });
        }
        return { openForCurrentRecord };
    },
};

registry.category("services").add("call_centerQongiroqlar", qongiroqlarService);
