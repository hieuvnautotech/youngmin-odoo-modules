/** @odoo-module **/
import { registry } from "@web/core/registry";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { useRef, onMounted } from "@odoo/owl";

import { ListRenderer } from "@web/views/list/list_renderer";


export class O2MListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.td_footer_num = [1]
    }
}

O2MListRenderer.template = "NoListRenderer"
O2MListRenderer.recordRowTemplate = "NoListRendererRecordRow";


export class One2ManySearchField extends X2ManyField {
    static template = "one2many_search.One2ManySearch";
    static components = {
        ...X2ManyField.components,
        ListRenderer: O2MListRenderer,
    }
    setup() {
        super.setup();
        this.rootRef = useRef("rootOne2manySearch");
        onMounted(() => {
            const input = this.rootRef.el.querySelector('input');
            if (input) {
                input.focus();
            }
            const o_notebook_headers = document.querySelector('.o_notebook_headers');
            if (o_notebook_headers) {
                o_notebook_headers.style.zIndex = '1';
            }
        });
    }

    onKeyUp(event) {
        const value = event.target.value.toLowerCase();

        // Sử dụng rootRef thay vì this.el
        const rootElement = this.rootRef.el;
        if (!rootElement) {
            console.warn("Root element not found");
            return;
        }

        const table = rootElement.querySelector('table');
        if (table) {
            table.classList.add('oe_one2many');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(value) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    }
}

export const one2ManySearchField = {
    ...x2ManyField,
    component: One2ManySearchField,
};

// Register the field
registry.category("fields").add("one2many_search", one2ManySearchField);