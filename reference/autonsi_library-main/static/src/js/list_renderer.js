/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';
import { useBus, useService } from '@web/core/utils/hooks';
import { useState, onMounted } from '@odoo/owl';
import { ListRenderer } from '@web/views/list/list_renderer';
import { registry } from "@web/core/registry";
const formatters = registry.category("formatters");


patch(ListRenderer.prototype, {
    setup() {

        super.setup();
        useBus(this.env.bus, "SEARCH_PANEL_TRIGGER", async (data) => {
            console.log(this.props.list.load())
        })
    },

    formatAggregateValue(group, column) {
        const { widget, attrs } = column;
        const field = this.props.list.fields[column.name];
        const aggregateValue = group.aggregates[column.name];
        if (field.type == "datetime" || field.type == "date") {
            return aggregateValue
        }
        if (!(column.name in group.aggregates)) {
            return "";
        }
        const formatter = formatters.get(widget, false) || formatters.get(field.type, false);
        const formatOptions = {
            digits: attrs.digits ? JSON.parse(attrs.digits) : field.digits,
            escape: true,
        };
        const value = formatter ? formatter(aggregateValue, formatOptions) : aggregateValue;
        return value != 0 ? value : aggregateValue;
    }
});