/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";

patch(RelationalModel.prototype, {
  setup() {
    super.setup(...arguments);
    localStorage.removeItem("N:CanLoad");
    this.isLoadFirst = false;
    if (this.useSampleModel)
      this.useSampleModelTemp = true;

  },
  async load(params = {}) {
    if (this.env.searchModel?.default_no_data_btn) {
      this.canReloadSplitView = false;
      if (this.env.searchModel.searchPanelSelect) {
        this.env.searchModel.searchPanelSelect = false
        this.useSampleModel = false;
        return;
      }
    }
    if (localStorage.getItem("N:CanLoad")) return;

    const res = await super.load(params);
    // if (this.config.context?.list_reload) {
    //   this.env.bus.trigger("List:ReLoad", {});
    // } else if (this.config.context?.many2one_field_reload) {
    //   this.env.bus.trigger("List:LoadMany2one_field", {});
    // } else if (this.config.context?.splited_tree_reload) {
    //   this.env.bus.trigger("List:LoadSplited_tree", {});
    // }
    this.canReloadSplitView = true;
    if (this.env.searchModel) {
      this.env.searchModel.buttonClick = false;
    }
    // Đợi tick tiếp theo để đảm bảo UI đã render
    return res;
  },

  hasData() {
    if (this.env.searchModel?.default_no_data_btn) {
      this.useSampleModel = !this.isLoadFirst;
      return this.isLoadFirst;
    }
    return super.hasData()
  }

});
