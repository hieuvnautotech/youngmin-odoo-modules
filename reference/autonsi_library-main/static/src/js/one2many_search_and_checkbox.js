/** @odoo-module **/
import {registry} from "@web/core/registry";
import {X2ManyField, x2ManyField} from "@web/views/fields/x2many/x2many_field";
import {useRef, onMounted} from "@odoo/owl";

import {ListRenderer} from "@web/views/list/list_renderer";
window.searchProductionRows = function(input) {
    const value = input.value.toLowerCase().trim();
    
    const table = input.closest('.o_notebook_content').querySelector('table.o_list_table');
    if (!table) {
        return;
    }
    
    const rows = table.querySelectorAll('tbody tr.o_data_row');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td.o_data_cell');
        let rowText = '';
        cells.forEach(cell => {
            const cellContent = cell.textContent || cell.innerText || '';
            rowText += cellContent + ' ';
        });
        rowText = rowText.toLowerCase();
        
        // Hiển thị tất cả nếu search empty HOẶC tìm thấy match
        if (value === '' || rowText.indexOf(value) > -1) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
};


export class O2MSearchAndCheckbox extends ListRenderer {
    setup() {
        this.hasSelectorsWidget = true;
        super.setup();
        this.td_footer_num = [1, 2]
    }

    get nbCols() {
        let nbCols = super.nbCols
        return nbCols + 1;
    }

    get one2ManySelectAll() {
        const list = this.props.list;
        const nbDisplayedRecords = list.records.length;
        const selection = list.records.filter(record => record.selected);
        return nbDisplayedRecords > 0 && selection.length === nbDisplayedRecords;
    }

    async one2ManyToggleSelection(e) {
        const records = this.props.list.records;
        const one2ManySelectAll = this.one2ManySelectAll;
        records.map((record) => record.selected = !one2ManySelectAll)
        const selection = this.props.list.records.filter(record => record.selected);
        this.props.list.model.root._config.context.selected_ids = selection.map(record => record.resId);
    }

    get nbCols() {

        let nbCols = this.state.columns.length;
        if (this.hasSelectors) {
            nbCols++;
        }
        if (this.activeActions.onDelete || this.displayOptionalFields) {
            nbCols++;
        }
        if (this.props.onOpenFormView) {
            nbCols++;
        }
        return nbCols + 2;
    }

    async one2ManyToggleRecordSelection(record) {
        await record.toggleSelection();
        const selection = this.props.list.records.filter(record => record.selected);
        this.props.list.model.root._config.context.selected_ids = selection.map(record => record.resId);
    }
}

O2MSearchAndCheckbox.template = "One2ManySelectionListRenderer_no"
O2MSearchAndCheckbox.recordRowTemplate = "One2ManySelectionListRendererRecordRow_no";

export class One2ManySearchField extends X2ManyField {
    static template = "one2many_search.One2ManySearchAndCheckbox";
    static components = {
        ...X2ManyField.components,
        ListRenderer: O2MSearchAndCheckbox,
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


registry.category("fields").add("one2many_search_and_checkbox", one2ManySearchField);
