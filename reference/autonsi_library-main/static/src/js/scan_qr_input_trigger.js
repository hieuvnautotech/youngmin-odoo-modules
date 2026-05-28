/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useBus, useService } from "@web/core/utils/hooks";
import { useState, onMounted } from "@odoo/owl";
import { ListRenderer } from "@web/views/list/list_renderer";
import { registry } from "@web/core/registry";
const formatters = registry.category("formatters");

import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, {
  setup() {
    super.setup();

    this.rpc = useService("rpc");
    this.orm = useService("orm");
    this.notification = useService("notification");

    useBus(this.env.bus, "SCAN_QR_INPUT_TRIGGER", async (data) => {
      const { actionId, qrValue } = data.detail;
      console.log("trigger-data", data);

      let actionName = "Unknown";

      try {
        // thử tìm trong ir.actions.act_window
        const result = await this.orm.read(
          "ir.actions.act_window",
          [actionId],
          ["name", "res_model"]
        );

        if (result?.length) {
          console.log("Action found:", result[0]);
          actionName = result[0].name;
          console.log("✅ Action found:", actionName, result[0].res_model);
        } else {
          console.warn("⚠️ Không tìm thấy action:", actionId);
        }
      } catch (err) {
        console.error("❌ Error fetching action:", err);
      }

      // Hiển thị thông báo
      //      this.notification.add(_t(`Đã quét QR trong action: ${actionName}`), {
      //        type: "success",
      //      });

      // Điền QR vào ô tìm kiếm
      const input = document.querySelector(".o_searchview_input.o_input");
      if (input) {
        input.value = qrValue;

        // Gửi sự kiện "input" để Odoo nhận thấy có thay đổi
        input.dispatchEvent(new Event("input", { bubbles: true }));

        // Gửi phím Enter để kích hoạt tìm kiếm
        const keyEvent = new KeyboardEvent("keydown", {
          bubbles: true,
          cancelable: true,
          key: "Enter",
          code: "Enter",
          keyCode: 13,
        });
        input.dispatchEvent(keyEvent);
      }
    });
  },
});
