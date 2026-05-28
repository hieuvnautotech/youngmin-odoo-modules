/** @odoo-module */
import { DateTimeInput } from '@web/core/datetime/datetime_input';
import { StaticList } from "@web/model/relational_model/static_list";
import { ListRenderer } from "@web/views/list/list_renderer";
import { browser } from "@web/core/browser/browser";

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";


patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.useSampleModel = false;
    },

    // get showNoContentHelper() {
    //     const { model } = this.props.list;
    //     if (model.useSampleModel && this.useSampleModel == undefined)
    //         this.useSampleModel = true;
    //     if (model.env?.searchModel?.default_no_data_btn) {
    //         if (this.canReloadSplitView == undefined) {
    //             if (model.canReloadSplitView) {
    //                 this.canReloadSplitView = true;
    //                 this.useSampleModel = false;
    //             }
    //         }
    //         return this.props.noContentHelp && (model.useSampleModel || this.useSampleModel || !model.hasData());
    //     } else
    //         return this.props.noContentHelp && (model.useSampleModel || !model.hasData());
    // }
})