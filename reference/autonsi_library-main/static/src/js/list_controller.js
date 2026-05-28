/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { ListRenderer } from '@web/views/list/list_renderer';


patch(ListController, {
  props: {
    ...ListController.props,
    
    rendererProps: { type: Object, optional: true },
  }
  ,
  components: {
    ...ListController.components,
    ListRenderer,
  },
})


patch(ListController.prototype, {
  setup() {
    super.setup();
  },
  get display() {
    const { controlPanel } = this.props.display;
    if (!controlPanel) {
      return this.props.display;
    }

    const display = {
      ...this.props.display,
      controlPanel: {
        ...controlPanel,
        layoutActions: !this.nbSelected,
      },
    };
    return display;
  },
});
