/* @odoo-module */

import { browser } from "@web/core/browser/browser";
import { useBus, useService } from "@web/core/utils/hooks";
import { ViewButton } from "@web/views/view_button/view_button";
import { LoadingIndicator } from "@web/webclient/loading_indicator/loading_indicator";
import { patch } from "@web/core/utils/patch";
patch(LoadingIndicator.prototype, {
    setup() {
        super.setup(...arguments);
    },

    requestCall({ detail }) {
        if (localStorage.getItem("N:CanLoad")) return
        if (detail.settings.silent) {
            return
        }
        if (this.state.count === 0) {
            browser.clearTimeout(this.startShowTimer);
            this.startShowTimer = browser.setTimeout(() => {
                if (this.state.count) {
                    this.state.show = true;
                }
            }, 250);
        }
        this.rpcIds.add(detail.data.id);
        this.state.count++;
    }
});

patch(ViewButton.prototype, {
    async onClick(event) {
        // calll super onClick
        await super.onClick(event);
    },
});

