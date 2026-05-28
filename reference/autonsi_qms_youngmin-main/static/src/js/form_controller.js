/* @odoo-module */

import { useBus } from "@web/core/utils/hooks";
import { patch } from '@web/core/utils/patch';
import { FormController } from '@web/views/form/form_controller';

patch(FormController.prototype, {
  setup() {
    super.setup();
    useBus(this.env.bus, "Reload:StockMoveLine", ({ detail }) => {
      this.model.load();
    });
  }
})