/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useBus, useService } from "@web/core/utils/hooks";
import { useState, onMounted } from "@odoo/owl";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { registry } from "@web/core/registry";
const formatters = registry.category("formatters");

patch(SearchBar.prototype, {
  setup() {
    super.setup();
    this.notification = useService("notification");
    this.show_scan_button =
      this.env?.model?.config.context.show_scan_button || false;

    this.actionId = this.env?.config?.actionId || false;
    //    this.show_scan_button = this.show_scan_button || false;
    // console.log("Show scan button:", this);
  },

  onScanQRClick: async function () {
    const videoContainer = document.getElementById("scan-video-container");
    const video = document.getElementById("scan-video");

    //        if (videoContainer && video) {
    //            console.log("Video container and video element found");
    //        }
    //        try {
    //            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    //            this.notification.add("✅ Camera opened (demo only)", { type: "info" });
    //            setTimeout(() => stream.getTracks().forEach((t) => t.stop()), 2000);
    //        } catch (err) {
    //            this.notification.add("❌ Cannot access camera: " + err.message, { type: "danger" });
    //        }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.notification.add(_t("Trình duyệt không hỗ trợ camera !"), {
        title: "Error",
        type: "danger",
      });
      return;
    }

    videoContainer.style.display = "block";

    try {
      this.videoStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      video.srcObject = this.videoStream;
      video.setAttribute("playsinline", true);
      await video.play();

      this.scanning = true;
      await this.tickQRScan(video);
    } catch (err) {
      console.error("Camera error:", err);
      this.notification.add(_t("Không thể mở camera !"), {
        title: "Error",
        type: "danger",
      });
    }
  },

  async tickQRScan(video) {
    if (!this.scanning) return;

    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, canvas.width, canvas.height, {
      inversionAttempts: "dontInvert",
    });

    if (code) {
      const qrValue = code.data.trim();
      console.log("QR Result:", qrValue);
      this.scanning = false;

      const value = {
        actionId: this.actionId,
        qrValue: qrValue,
      };

      this.env.bus.trigger("SCAN_QR_INPUT_TRIGGER", value);
      this.stopQRScanner();
    }

    requestAnimationFrame(() => this.tickQRScan(video));
  },

  stopQRScanner() {
    this.scanning = false;
    //    this.env.bus.trigger("SCAN_QR_INPUT_TRIGGER", "abc");
    if (this.videoStream) {
      this.videoStream.getTracks().forEach((track) => track.stop());
      this.videoStream = null;
    }
    document.getElementById("scan-video-container").style.display = "none";
  },
});
