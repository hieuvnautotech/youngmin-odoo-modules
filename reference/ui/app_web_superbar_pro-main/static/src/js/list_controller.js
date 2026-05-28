/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { onPatched } from "@odoo/owl";
import { useState, useRef, onMounted, onWillUpdateProps } from "@odoo/owl";

patch(ListController.prototype, {
  setup() {
    super.setup(...arguments);
    onPatched(() => {
      if (this.props.context.save_current_action)
        localStorage.setItem("currentControllerId", this.env.services.action.currentController.jsId)
    })
  }
});
