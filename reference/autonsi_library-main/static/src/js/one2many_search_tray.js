/** @odoo-module **/

import { registry } from "@web/core/registry";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
export class One2ManySearchTrayField extends X2ManyField {
	onKeyUp(event) {
		const value = event.target.value.toLowerCase();
		const table = this.el.querySelector('table');

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
		return nbCols + 1;
	}
}

One2ManySearchTrayField.template = "one2many_search_tray.One2ManySearchTray";


export const one2ManySearchTrayField = {
	...x2ManyField,
	component: One2ManySearchTrayField,
};


// Register the field
registry.category("fields").add("one2many_search_tray", one2ManySearchTrayField);