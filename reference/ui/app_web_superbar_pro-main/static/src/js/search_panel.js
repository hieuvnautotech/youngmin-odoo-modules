/** @odoo-module **/

import { SearchPanel } from "@web/search/search_panel/search_panel";
import { patch } from "@web/core/utils/patch";
import { useService } from '@web/core/utils/hooks';

const { DateTime } = luxon;

patch(SearchPanel.prototype, {
    setup() {
        super.setup();
        this.resModel = this.env.model?.root?.resModel;
    },


    onDateTimeChanged(section, value, date) {
        if (section.pro || value.widget == 'date') {
            let obj = {};
            //Handle pass null values
            if (!value.childrenIds.length && !date) {
                //  todo: Full clear, use mvvm to process front-end clear value
                this.env.searchModel.toggleCategoryValue(section.id, date, undefined, true);
            }
            if (!date) {
                if (!section.activeValueId)
                    ;
                else if (section.activeValueId[value.id]) {
                    obj[value.id] = date;
                    this.env.searchModel.toggleCategoryValue(section.id, obj);
                }
            } else {
                //   Passing values ​​is different, to be processed
                if (!section.activeValueId || section.activeValueId[value.id] !== date) {
                    obj[value.id] = date;
                    this.env.searchModel.toggleCategoryValue(section.id, obj);
                }
            }
        }
    },

    onFloatChange(section, value, ev) {
        if (section.pro || value.widget == 'float') {
            let obj = {};
            var val = $(ev.target).val();
            //Handle pass null values
            if (!value.childrenIds.length && !val) {
                //  todo:  全清，用mvvm 方式处理前端清空值
                this.env.searchModel.toggleCategoryValue(section.id, val);
            }
            if (!val) {
                if (!section.activeValueId)
                    ;
                else if (section.activeValueId[value.id]) {
                    obj[value.id] = val;
                    this.env.searchModel.toggleCategoryValue(section.id, obj);
                }
            } else {
                //    Passing values ​​is different, to be processed
                if (!section.activeValueId || section.activeValueId[value.id] !== val) {
                    obj[value.id] = val;
                    this.env.searchModel.toggleCategoryValue(section.id, obj);
                }
            }
        }
    },

    onBoolChange(section, value, bool_value) {
        if (section.pro || value.widget == 'boolean') {
            this.env.searchModel.toggleCategoryValue(section.id, bool_value);
        }
    },

    async toggleCategory(category, value) {
        if (value.value === undefined) {
            category.isShowAllDataBtn = false
        }
        if (!category.pro) {
            this.env.searchModel.searchPanelSelect = true;
            await super.toggleCategory(...arguments);
            return
        }
        //Start special processing
        if (category.searchType == "month") {
            if (value.value === undefined) {
                let obj = {}
                this.env.searchModel.toggleCategoryValue(category.id, obj[value.id]);
                this.env.bus.trigger('SP:MonthPanelReset', { id_cate: category.id });
            }
        }
        else if (category.searchType == "year") {
            if (value.value === undefined) {
                let obj = {}
                this.env.searchModel.toggleCategoryValue(category.id, obj[value.id]);
                this.env.bus.trigger('SP:YearPanelReset', { id_cate: category.id });
            }
        }
        else if (!value.childrenIds.length) {
            //todo: Clear
            this.onDateTimeChanged(category, value, undefined);
        } else if (!value.childrenIds.length && category.fieldType == 'boolean') {
            //todo: 清空 bool
            this.onBoolChange(category, { 'widget': 'boolean' }, undefined);
        }

    },
    async onComboxboxChanged(section, value, v) {
        var obj = {}
        if (!section.activeValueId || section.activeValueId[value.id] !== v) {
            obj[1] = v;
            this.env.searchModel.toggleCategoryValue(section.id, obj);
        }
    },
    getAncestorValueIds(category, categoryValueId) {
        let value = category.values.get(1);
        let parentId = value ? value.parentId : null; // Gán giá trị mặc định nếu undefined

        if (parentId === null || parentId === undefined) {
            value = category.values.get(categoryValueId);
            parentId = value ? value.parentId : null; // Gán giá trị mặc định nếu undefined
        }
        return parentId ? [...this.getAncestorValueIds(category, parentId), parentId] : [];
    },
    async onFieldPanelChanged(section, value, currentId, date_from, date_to) {
        const result = await this.env.searchModel._setDefaultDateRange(currentId, true);
        if (result) return
        const localDate = new Date();
        var data = {}
        if (date_from) {

            date_from = date_from.startOf('day').plus({ hours: -localDate.getTimezoneOffset() / 60 });
        }

        data[value.id] = {
            value_id: currentId,
            date_from,
            date_to
        }
        this.env.searchModel.toggleCategoryValue(section.id, data);
        return;
    },

    onDatePanelChanged(section, value, currentId, date_from, date_to) {
        const localDate = new Date();
        var data = {}
        if (date_from) {
            date_from = date_from.startOf('day').plus({ hours: -localDate.getTimezoneOffset() / 60 });
        }

        data[value.id] = {
            value_id: currentId,
            date_from,
            date_to
        }
        this.env.searchModel.toggleCategoryValue(section.id, data);
    },

    onMonthPanelChanged(section, value, currentId, select_month) {
        const localDate = new Date();
        var data = {}

        let date_from, date_to;

        if (select_month) {
            // select_month đã là LuxonDateTime
            // Tạo ngày đầu tháng (00:00:00)
            date_from = select_month.startOf('month');

            // Tạo ngày cuối tháng (23:59:59.999)
            date_to = select_month.endOf('month');

            // // Áp dụng timezone offset
            // date_from = date_from.plus({ hours: -localDate.getTimezoneOffset() / 60 });
            // date_to = date_to.plus({ hours: -localDate.getTimezoneOffset() / 60 });
        }

        data[value.id] = {
            value_id: currentId,
            date_from,
            date_to
        }

        this.env.searchModel.toggleCategoryValue(section.id, data, select_month);
    },

    onYearPanelChanged(section, value, currentId, select_year) {
        const localDate = new Date();
        var data = {}

        let date_from, date_to;

        if (select_year) {
            // select_month đã là LuxonDateTime
            date_from = select_year.startOf('year');

            date_to = select_year.endOf('year');

            // // Áp dụng timezone offset
            // date_from = date_from.plus({ hours: -localDate.getTimezoneOffset() / 60 });
            // date_to = date_to.plus({ hours: -localDate.getTimezoneOffset() / 60 });
        }

        data[value.id] = {
            value_id: currentId,
            date_from,
            date_to
        }

        this.env.searchModel.toggleCategoryValue(section.id, data);
    },

});
