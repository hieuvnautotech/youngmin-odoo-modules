/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { many2OneField, Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class Many2OneQRScanField extends Many2OneField {
    static template = "web.Many2OneQRScanField";

    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    async onScanQRClick() {
        const videoContainer = document.getElementById("scan-video-container");
        const video = document.getElementById("scan-video");

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.notification.add(_t("Trình duyệt không hỗ trợ camera!"), {
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
            this.notification.add(_t("Không thể mở camera!"), {
                title: "Error",
                type: "danger",
            });

        }
    }

    async tickQRScan(video) {
        if (!this.scanning) return;

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        // Kiểm tra jsQR có tồn tại không
        if (typeof jsQR === 'undefined') {
            console.error("jsQR library not found");
            this.stopQRScanner();
            this.notification.add(_t("Thư viện QR code chưa được tải!"), {
                type: "danger",
            });
            return;
        }

        const code = jsQR(imageData.data, canvas.width, canvas.height, {
            inversionAttempts: "dontInvert",
        });

        if (code) {
            const qrValue = code.data.trim();
            console.log("QR Result:", qrValue);
            this.scanning = false;
            this.stopQRScanner();

            // Tìm kiếm record dựa trên QR code
            await this.searchAndFillFromQR(qrValue);
            return;
        }

        requestAnimationFrame(() => this.tickQRScan(video));
    }

    async searchAndFillFromQR(qrValue) {
        try {
            if (qrValue) {

                // Tìm kiếm record bằng name_search
                const results = await this.orm.call(this.relation, "name_search", [], {
                    name: qrValue,
                    args: this.getDomain(),
                    operator: "ilike",
                    limit: 5,
                    context: this.context,
                });

                if (results.length === 0) {
                    this.notification.add(
                        _t("Không tìm thấy bản ghi nào với mã: %s", qrValue),
                        { type: "warning" }
                    );
                    return;
                }

                if (results.length === 1) {
                    // Nếu chỉ có 1 kết quả, tự động fill
                    const [id, displayName] = results[0];
                    await this.update([{ id, name: displayName }]);
                    this.notification.add(
                        _t("Đã chọn: %s", displayName),
                        { type: "success" }
                    );
                }
                else {
                    // Nếu có nhiều kết quả, hiển thị trong autocomplete
                    const searchInput = this.autocompleteContainerRef.el.querySelector("input");
                    if (searchInput) {
                        searchInput.value = qrValue;
                        searchInput.dispatchEvent(new Event("input", { bubbles: true }));
                        searchInput.focus();
                    }
                    this.notification.add(
                        _t("Tìm thấy %s kết quả, vui lòng chọn", results.length),
                        { type: "info" }
                    );
                }

            }
            else {
                this.notification.add(
                    _t("Không tìm thấy bản ghi nào với mã: %s", qrValue),
                    { type: "warning" }
                );
                return;
            }

        } catch (error) {
            console.error("Search error:", error);
            this.notification.add(
                _t("Lỗi khi tìm kiếm: %s", error.message || error),
                { type: "danger" }
            );
        }
    }

    stopQRScanner() {
        this.scanning = false;
        if (this.videoStream) {
            this.videoStream.getTracks().forEach((track) => track.stop());
            this.videoStream = null;
        }
        const videoContainer = document.getElementById("scan-video-container");
        if (videoContainer) {
            videoContainer.style.display = "none";
        }
    }
}

export const many2OneQRScanField = {
    ...many2OneField,
    component: Many2OneQRScanField,
    extractProps(fieldInfo) {
        const props = many2OneField.extractProps(...arguments);
        props.canOpen = fieldInfo.viewType === "form";
        props.canScanBarcode = true; // Enable scan nếu cần
        return props;
    },
};

registry.category("fields").add("many2one_qr_scan", many2OneQRScanField);