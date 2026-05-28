/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { useBus } from "@web/core/utils/hooks";

patch(ListController.prototype, {
  setup() {
    super.setup(...arguments);
    useBus(this.env.bus, "Reload:StockMoveLine", ({ detail }) => {
      this.model.load();
    });
  },
});
