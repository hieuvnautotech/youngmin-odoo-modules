/** @odoo-module */
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import {patch} from '@web/core/utils/patch';

patch(RelationalModel.prototype, {
    
    async load() {
        const res = await super.load(...arguments);
        if (this?.root?._config?.context?.selected_ids) {
            this.root._config.context.selected_ids = [];
        }
        return res;
    }
})

export class O2MListRenderer extends ListRenderer {
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

O2MListRenderer.template = "One2ManySelectionListRenderer_no"
O2MListRenderer.recordRowTemplate = "One2ManySelectionListRendererRecordRow_no";

export class CustomX2ManyField extends X2ManyField {
    setup() {
        super.setup();
    }

    static components = {
        ...X2ManyField.components,
        ListRenderer: O2MListRenderer,
    }
}

export const one2manySelection = {
    ...x2ManyField,
    component: CustomX2ManyField,
};
registry.category("fields").add("one2many_selection_no", one2manySelection);
