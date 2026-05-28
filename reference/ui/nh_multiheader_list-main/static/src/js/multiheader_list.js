/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { isMobileOS } from "@web/core/browser/feature_detection";
import { ListRenderer } from "@web/views/list/list_renderer";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { ColumnManager } from "@udoo_web_list_view/mod/manager";
import { deepCopy } from "@web/core/utils/objects";

patch(ListRenderer.prototype, {
    setup() {
        this.context = this.props.list.context;
        this.context.multiheaderOriginal = deepCopy(
            this.context?.multiheader || {}
        );
        super.setup();

        this.isColumnUpdated = false;
        // Định nghĩa hàm callback
        this.onColumnUpdate = (updatedColumns, columnId = -1, action = "", index = 0, drag_info) => {


            if (columnId != -1)
                index = this.state.columns.findIndex(el => el.id === columnId);
            this.state.columns = updatedColumns
            if (index != -1 && action) {
                if (this.context?.multiheader) {
                    if (action == "drag_drop") {
                        this.context.multiheader = this.updateMultiheaderPosition(this.context.multiheader, index, action, drag_info)
                    }
                    else {
                        this.context.multiheader = this.updateMultiheaderPosition(this.context.multiheader, index, action)
                    }
                    // Load config cho user hiện tại
                    this.updateMultiHeader();
                    this.isColumnUpdated = true;
                }
            }
        };
        // Khởi tạo arrays cho các level header
        this.multiHeader = [];
        this.headerLevels = {}; // Object chứa header theo từng level
        this.maxLevel = 0; // Level cao nhất
        this.userService = useService("user");
        this.actionService = useService("action");
        const list = this.props.list;

        const { actionId, actionType } = this.env.config || {};

        const isPotentiallyEditable =
            !isMobileOS() &&
            !this.env.inDialog &&
            this.userService.isSystem &&
            list === list.model.root &&
            actionId &&
            actionType === "ir.actions.act_window";
        this.udooEditable = useState({ value: isPotentiallyEditable });

        const columnConfigManager = this.columnConfigManager.loadConfig(
            this.props.list.resModel,
            this.props.archInfo?.id || this.env.config.viewId,
            this.env.config.actionId
        );
        const multiheader_config = columnConfigManager?.multiheader_config;
        const multiheader_original = columnConfigManager?.multiheader_original;
        this.has_multi_header = this.context.multiheader != undefined;
        if (
            multiheader_config &&
            multiheader_config.length > 0 &&
            this.has_multi_header
        ) {
            this.context.multiheader = multiheader_config;
        }
        if (this.hasSelectors && !this.context?.no_checkbox) {
            this.hasSelectorsWidget = true;
        }
        this.updateMultiHeader();

        // Chạy khi component được gắn vào DOM
        onMounted(() => {
            this.caculateManagerColumnPosition();
            this.applyTableStyles();
        });

        //It is called when actually a component did actually update its DOM. Useful to interact with DOM whenever a component is patched.
        onPatched(() => {
            if (this.isColumnUpdated) {
                this.isColumnUpdated = false;
                this.applyTableStyles();
            }
        });

        onWillUnmount(() => {
            if (this.has_multi_header) {
                const columnConfigManager = this.columnConfigManager.loadConfig(
                    this.props.list.resModel,
                    this.props.archInfo?.id || this.env.config.viewId,
                    this.env.config.actionId
                );
                this.columnConfigManager.update(
                    this.props.list.resModel,
                    {
                        ...columnConfigManager,
                        multiheader_config: this.context?.multiheader,
                        multiheader_original: columnConfigManager?.multiheader_original
                            ? columnConfigManager.multiheader_original
                            : this.context?.multiheaderOriginal,
                    },
                    this.props.archInfo?.id || this.env.config.viewId,
                    this.env.config.actionId
                );
            }
        });
    },

    applyTableStyles() {
        if (!this.tableRef?.el) return;
        let thead = this.tableRef.el.querySelector("thead");
        if (!thead) return;

        if (this.context.multiheader) {
            // Thêm class cho multi-level
            this.tableRef.el.classList.add(
                this.context.sub_list
                    ? "multi-header_multilevel"
                    : "multi-header_multilevel"
            );
            // Lấy tất cả rows, loại trừ search_header và hidden rows
            const validRows = Array.from(thead.querySelectorAll("tr"));
            // Lấy row cuối cùng (main headers)

            let mainRow;
            validRows.forEach((tr) => {
                if (tr.classList.contains("o_origin_thead")) {
                    mainRow = tr;
                }
            });
            const mainRowThs = mainRow ? mainRow.querySelectorAll("th") : [];
            // Xử lý border cho th đầu tiên của mainRowThs

            if (this.maxLevel == 1) {
                const levelHeaders = thead.querySelectorAll(
                    `th.o_group_header_level_1[merge]`
                );
                levelHeaders.forEach((th) => {
                    const indexAttr = th.getAttribute("index");
                    if (indexAttr) {
                        const index =
                            parseInt(indexAttr, 10) - (this.hasSelectorsWidget ? 0 : 1);
                        // Áp dụng cho main row (row cuối)
                        if (index >= 0 && index < mainRowThs.length) {
                            const targetTh = mainRowThs[index];
                            if (targetTh) {
                                targetTh.classList.add("no-border-top");
                                const span = targetTh.querySelector("div span");
                                if (span) {
                                    span.style.cssText = `
                                    text-wrap: auto;
                                    margin-top: ${this.topPosition}px;
                                    min-width: 100% !important;
                                `;
                                }
                            }
                        }
                    }
                });
            } else {
                let is_print = false
                // Xử lý style cho từng level
                for (let level = 1; level < this.maxLevel; level++) {
                    const levelHeaders = thead.querySelectorAll(
                        `th.o_group_header_level_${level}[merge]`
                    );
                    if (level == 1) {
                        levelHeaders.forEach((th) => {
                            const indexAttr = th.getAttribute("index");
                            if (indexAttr) {
                                const index = parseInt(indexAttr, 10) - (this.hasSelectorsWidget ? 0 : 1);

                                // Kiểm tra xem cột này có bị che phủ bởi level cao hơn không
                                const isCoveredByHigherLevel = this.isColumnCoveredByHigherLevel(index - 1, level);
                                console.log(index, isCoveredByHigherLevel, th)
                                // Nếu bị che phủ → giữ nguyên border-top (không làm gì)
                                if (isCoveredByHigherLevel) {
                                    th.classList.add("no-border-top");
                                }


                                // Xử lý cho level 0 (mainRowThs)
                                if (index >= 0 && index < mainRowThs.length) {
                                    const targetTh = mainRowThs[index];
                                    if (targetTh) {
                                        targetTh.classList.add("no-border-top");
                                        const span = targetTh.querySelector("div span");
                                        if (span) {
                                            span.style.cssText = `
                            text-wrap: auto;
                            margin-top: ${this.topPosition + (isCoveredByHigherLevel? 25 : 30)}px;
                            min-width: 100% !important;
                        `;
                                        }
                                    }
                                }
                            }
                        });
                    }
                }
            }
            // Xử lý border cho th đầu tiên của tất cả valid rows
            if (this.hasSelectorsWidget)
                validRows.forEach((row) => {
                    const firstTh = row.querySelector("th:first-child");
                    if (
                        firstTh &&
                        !firstTh.classList.contains(
                            `o_group_header_level_${this.maxLevel}_checkbox`
                        )
                    ) {
                        firstTh.classList.add("no-border-top");
                    }
                });
        }

        // Xử lý o_resize cho tất cả valid rows
        const validRows = Array.from(thead.querySelectorAll("tr"));

        const oResizeElements = this.tableRef.el.querySelectorAll(".o_resize");
        const theadHeight = thead.offsetHeight;

        oResizeElements.forEach((resizeEl) => {
            const parentTh = resizeEl.closest("th");
            if (parentTh) {
                // Kiểm tra th có thuộc valid row không
                const parentRow = parentTh.closest("tr");
                const isValidRow = validRows.includes(parentRow);

                if (isValidRow) {
                    resizeEl.style.top = parentTh.classList.contains("no-border-top")
                        ? `${-(theadHeight - parentTh.offsetHeight)}px`
                        : "0px";
                }
            }
        });
    },

    /**
   * Kiểm tra xem một cột ở level hiện tại có bị che phủ bởi header thực ở level cao hơn không
   * CHỈ kiểm tra các header có label thực (không phải '-')
   * @param {number} columnIndex - Index của cột cần kiểm tra (bắt đầu từ 0)
   * @param {number} currentLevel - Level hiện tại của cột
   * @returns {boolean} - true nếu bị che phủ bởi level cao hơn có label thực (cần GIỮ border-top)
   */
    isColumnCoveredByHigherLevel(columnIndex, currentLevel) {
        if (!this.context?.multiheader) return false;

        // Duyệt qua các level từ currentLevel + 1 trở lên
        for (let level = currentLevel + 1; level <= this.maxLevel; level++) {
            // Tìm các header ở level cao hơn có label thực (không phải '-')
            const higherLevelHeaders = this.context.multiheader.filter(
                config => (config.level || 1) === level && config.label && config.label.trim() !== '-'
            );

            for (const header of higherLevelHeaders) {
                const positions = header.position.split(',').map(Number);
                const startPos = positions[0];
                const endPos = positions.length > 1 ? positions[1] : positions[0];
                console.log(columnIndex, startPos, endPos);
                // Kiểm tra xem columnIndex có nằm trong khoảng của header thực này không
                if (columnIndex >= startPos && columnIndex <= endPos) {
                    return false; // Cột BỊ CHE PHỦ → cần GIỮ border-top
                }
            }
        }

        return true; // Không bị che phủ → có thể XÓA border-top
    },
    isUdooEditable() {
        return this.udooEditable.value;
    },

    get displayOptionalFields() {
        return this.isUdooEditable() || super.displayOptionalFields;
    },

    caculateManagerColumnPosition() {
        // Xử lý dropdown-white-background
        const dropdownTh = this.tableRef.el.querySelector(
            ".dropdown-white-background"
        );
        if (dropdownTh) {
            let foundOrigin = false;
            const thead = this.tableRef.el.querySelector("thead");
            const theadHeight = thead.offsetHeight;

            // Chọn tr có 1 trong 2 class (multiheader HOẶC o_origin_thead)
            const allTrs = thead.querySelectorAll(
                "tr.multiheader, tr.o_origin_thead"
            );
            if (allTrs.length === 1) {
                // Trường hợp chỉ có 1 tr - căn giữa theo chiều cao của tr
                const trHeight = allTrs[0].offsetHeight;
                const topPosition = trHeight / 2 - dropdownTh.offsetHeight / 2;
                dropdownTh.style.top = `${topPosition}px`;
                this.topPosition = topPosition;
            } else if (allTrs.length > 1) {
                // Trường hợp có nhiều tr - tính chiều cao trung bình
                const totalHeight = Array.from(allTrs).reduce(
                    (sum, tr) => sum + tr.offsetHeight,
                    0
                );
                const averageHeight = totalHeight / allTrs.length;

                const parentTr = dropdownTh.closest("tr");
                const trOffsetTop = parentTr.offsetTop;
                const trHeight = parentTr.offsetHeight;

                // Sử dụng chiều cao trung bình thay vì theadHeight
                const centerOfAverage = averageHeight / 2;
                const centerOfTr = trOffsetTop + trHeight / 2;
                const topPosition = centerOfAverage - centerOfTr;
                this.topPosition = topPosition + 15;
                dropdownTh.style.top = `${this.topPosition + 30}px`;
            } else {
                // Trường hợp không có tr nào có class đó - fallback
                const parentTr = dropdownTh.closest("tr");
                const trOffsetTop = parentTr.offsetTop;
                const trHeight = parentTr.offsetHeight;
                const centerOfThead = theadHeight / 2;
                const centerOfTr = trOffsetTop + trHeight / 2;
                const topPosition = centerOfThead - centerOfTr;
                this.topPosition = topPosition;
                dropdownTh.style.top = `${topPosition + 15}px`;
            }
        }
    },

    /**
     * This function opens promote studio dialog
     *
     * @private
     */
    openColumnManager() {
        const { archInfo, list } = this.props;
        const state = this.actionService.currentController.getLocalState();
        this.env.services.dialog.add(ColumnManager, {
            viewId: this.env.config.viewId,
            resModel: list.resModel,
            fields: state.modelState.config.fields,
            fieldNodes: archInfo.fieldNodes,
            columns: this.state.columns,
            allColumns: this.allColumns,
            actionId: parseInt(this.env.config.actionId),
            onColumnUpdate: this.onColumnUpdate,
        });
    },

    getRandomString(length) {
        const characters =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let result = "";
        for (let i = 0; i < length; i++) {
            result += characters.charAt(
                Math.floor(Math.random() * characters.length)
            );
        }
        return result;
    },
    updateMultiHeader() {
        // Khởi tạo multiHeader base
        this.multiHeader = this.state.columns.map((col) => {
            return {
                field: col.name,
                label: col.label,
                groupLabel: undefined,
            };
        });

        // Reset header levels
        this.headerLevels = {};
        this.maxLevel = 0;

        if (
            this.context &&
            this.context.multiheader &&
            Array.isArray(this.context.multiheader)
        ) {
            // Tìm level cao nhất
            this.context.multiheader.forEach((config) => {
                const level = config.level || 1;
                if (level > this.maxLevel) {
                    this.maxLevel = level;
                }
            });

            // Xử lý từng level từ cao xuống thấp
            for (
                let currentLevel = this.maxLevel;
                currentLevel >= 1;
                currentLevel--
            ) {
                this.processHeaderLevel(currentLevel);
            }
        }
    },

    processHeaderLevel(level) {
        if (!this.headerLevels[level]) {
            this.headerLevels[level] = [];
        }

        // Tạo base header cho level này
        const levelHeaders = this.state.columns.map((col) => {
            return {
                field: col.name,
                label: col.label,
                header_style: col.header_style,
                groupLabel: undefined,
                level: level,
            };
        });

        // Áp dụng config cho level này
        this.context.multiheader.forEach((multiheaderConfig) => {
            if ((multiheaderConfig.level || 1) === level) {
                const position = multiheaderConfig.position.split(",").map(Number);

                if (position.length === 2 && levelHeaders.length > position[1]) {
                    if (multiheaderConfig.label.trim() === "-") {
                        for (let i = position[0]; i <= position[1]; i++) {
                            levelHeaders[i].groupLabel = this.getRandomString(6);
                            levelHeaders[i].is_group = true;
                            levelHeaders[i].is_merge = true;
                        }
                    } else {
                        for (let i = position[0]; i <= position[1]; i++) {
                            levelHeaders[i].groupLabel = multiheaderConfig.label;
                            levelHeaders[i].is_group = true;
                        }
                    }
                } else if (position.length === 1 && levelHeaders.length > position[0]) {
                    levelHeaders[position[0]].is_group = true;

                    if (multiheaderConfig.label.trim() === "-") {
                        levelHeaders[position[0]].groupLabel = this.getRandomString(6);
                        levelHeaders[position[0]].is_merge = true;
                    } else {
                        levelHeaders[position[0]].groupLabel = multiheaderConfig.label;
                    }
                }
            }
        });

        // Tạo rendered headers cho level này
        const renderedHeaders = levelHeaders.reduce((acc, header, index) => {
            if (header.is_group && !acc.some((h) => h.label === header.groupLabel)) {
                const newHeader = {
                    label: header.is_merge ? " " : header.groupLabel,
                    class: `o_group_header_level_${level} o_group_second_header`,
                    header_style: header.header_style,
                    colspan: 0,
                    is_merge: header.is_merge,
                    level: level,
                };

                // Đếm colspan
                levelHeaders.forEach((col) => {
                    if (col.is_group && col.groupLabel === header.groupLabel) {
                        newHeader.colspan++;
                        newHeader.index = index + 1;
                    }
                });

                // Áp dụng style từ config
                if (this.context && this.context.multiheader) {
                    this.context.multiheader.forEach((config) => {
                        if (
                            (config.level || 1) === level &&
                            config.label === header.groupLabel &&
                            config.backgroundColor
                        ) {
                            newHeader.style = `background-color: ${config.backgroundColor};`;
                        }
                    });
                }
                acc.push(newHeader);
            }
            return acc;
        }, []);

        if (renderedHeaders.length > 0) {
            const expectedColspan = this.multiHeader.length + 1;
            let actualColspan = renderedHeaders.reduce(
                (sum, header) => sum + header.colspan,
                0
            );
            if (this.hasSelectorsWidget)
                // Thêm cột checkbox
                renderedHeaders.unshift({
                    label: "",
                    class: `o_group_header_level_${level}_checkbox level_checkbox`,
                    level: level,
                });

            // Điền các cột trống
            while (actualColspan < expectedColspan) {
                const headerClass =
                    actualColspan === expectedColspan - 1
                        ? `o_group_header_level_${level} o_group_second_header second_header_action`
                        : `o_group_header_level_${level} o_group_second_header`;

                renderedHeaders.push({
                    label: "",
                    class: headerClass,
                    header_style: "",
                    colspan: 0,
                    is_merge: true,
                    index: actualColspan + 1,
                    level: level,
                });
                actualColspan++;
            }
        }

        this.headerLevels[level] = renderedHeaders;
    },

    // Các method getter cho template
    getAllHeaderLevels() {
        const levels = [];
        for (let i = this.maxLevel; i >= 1; i--) {
            if (this.headerLevels[i] && this.headerLevels[i].length > 0) {
                levels.push({
                    level: i,
                    headers: this.headerLevels[i],
                });
            }
        }
        return levels;
    },

    getHeadersForLevel(level) {
        return this.headerLevels[level] || [];
    },
    get getSecondHeaders() {
        // Trả về level 1 để tương thích với code cũ
        return this.headerLevels[1] || [];
    },

    getHeaders() {
        return this.multiHeader;
    },

    onStartResize(ev) {
        this.resizing = true;
        const table = this.tableRef.el;
        const th = ev.target.closest("th");
        const handler = th.querySelector(".o_resize");
        table.style.width = `${Math.floor(table.getBoundingClientRect().width)}px`;
        const thPosition = [...th.parentNode.children].indexOf(th);
        const resizingColumnElements = [...table.getElementsByTagName("tr")]
            .filter((tr) => tr.children.length === th.parentNode.children.length)
            .map((tr) => tr.children[thPosition]);
        const initialX = ev.clientX;
        const initialWidth = th.getBoundingClientRect().width;
        const initialTableWidth = table.getBoundingClientRect().width;
        const resizeStoppingEvents = ["keydown", "pointerdown", "pointerup"];

        // fix the width so that if the resize overflows, it doesn't affect the layout of the parent
        if (!this.rootRef.el.style.width) {
            this.rootRef.el.style.width = `${Math.floor(
                this.rootRef.el.getBoundingClientRect().width
            )}px`;
        }

        // Tìm group header từ bất kỳ level nào
        let groupHeader = null;
        for (let level = 1; level <= this.maxLevel; level++) {
            const levelHeaders = this.headerLevels[level] || [];
            groupHeader = levelHeaders.find((header) =>
                this.multiHeader.some(
                    (col) =>
                        col.groupLabel === header.label && col.field === th.dataset.name
                )
            );
            if (groupHeader) break;
        }

        let groupHeaderElement;
        let originalWidth;
        const columnWidths = {};

        if (groupHeader) {
            groupHeaderElement = document.querySelector(
                `th[data-header-label="${groupHeader.label}"]`
            );
            if (groupHeaderElement) {
                originalWidth = groupHeaderElement.getBoundingClientRect().width;
                this.multiHeader.forEach((col) => {
                    const colElement = document.querySelector(
                        `th[data-name="${col.field}"]`
                    );
                    if (colElement) {
                        columnWidths[col.field] = colElement.getBoundingClientRect().width;
                    }
                });
            }
        }

        table.classList.add("o_resizing");
        for (const el of resizingColumnElements) {
            el.classList.add("o_column_resizing");
            handler.classList.add("bg-primary", "opacity-100");
            handler.classList.remove("bg-black-25", "opacity-50-hover");
        }

        const resizeHeader = (ev) => {
            if (!$(".o_list_view table").hasClass("o_list_view_multiheader")) {
                $(".o_list_view table").addClass("o_list_view_multiheader");
            }

            const delta = ev.clientX - initialX;
            let newWidth = Math.max(50, initialWidth + delta);
            th.style.width = `${newWidth}px`;
            th.style.minWidth = `${newWidth}px`;

            const tableWidth = table.getBoundingClientRect().width + delta;
            const parentWidth = table.parentNode.getBoundingClientRect().width;

            if (tableWidth >= parentWidth || delta < 0) {
                table.style.maxWidth = `${Math.max(parentWidth, tableWidth)}px`;
            }

            if (groupHeader && groupHeaderElement) {
                let totalWidth = 0;
                this.multiHeader.forEach((col) => {
                    const colElement = document.querySelector(
                        `th[data-name="${col.field}"]`
                    );
                    if (colElement) {
                        if (colElement === th) {
                            totalWidth += newWidth - columnWidths[col.field]; // Chỉ thay đổi cột đang kéo
                        } else {
                            colElement.style.maxWidth = columnWidths[col.field] + "px";
                            colElement.style.minWidth = columnWidths[col.field] + "px";
                        }
                    }
                });

                if (totalWidth > originalWidth) {
                    groupHeaderElement.style.width = `${totalWidth}px`;
                    // groupHeaderElement.style.maxWidth = `${originalWidth}px`;
                } else {
                    groupHeaderElement.style.width = `${Math.min(
                        originalWidth,
                        totalWidth
                    )}px`;
                    // groupHeaderElement.style.maxWidth = `${Math.max(originalWidth, totalWidth)}px`;
                }
            }
        };

        window.addEventListener("pointermove", resizeHeader);

        // Mouse or keyboard events : stop resize
        const stopResize = (ev) => {
            this.resizing = false;
            // freeze column size after resizing
            this.keepColumnWidths = true;
            // Ignores the 'left mouse button down' event as it used to start resizing
            if (ev.type === "pointerdown" && ev.button === 0) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();

            table.classList.remove("o_resizing");
            for (const el of resizingColumnElements) {
                el.classList.remove("o_column_resizing");
                handler.classList.remove("bg-primary", "opacity-100");
                handler.classList.add("bg-black-25", "opacity-50-hover");
            }

            window.removeEventListener("pointermove", resizeHeader);
            for (const eventType of resizeStoppingEvents) {
                window.removeEventListener(eventType, stopResize);
            }

            // we remove the focus to make sure that the there is no focus inside
            // the tr.  If that is the case, there is some css to darken the whole
            // thead, and it looks quite weird with the small css hover effect.
            document.activeElement.blur();
            // Tìm và hiển thị group header từ bất kỳ level nào
            for (let level = 1; level <= this.maxLevel; level++) {
                const levelHeaders = this.headerLevels[level] || [];
                const groupHeader = levelHeaders.find((header) => {
                    const groupColumns = this.multiHeader.filter(
                        (col) => col.groupLabel === header.label
                    );
                    return groupColumns.some(
                        (col) => this.multiHeader.indexOf(col) === thPosition
                    );
                });
                if (groupHeader) {
                    const groupHeaderElement = $(
                        `th[data-header-label="${groupHeader.label}"]`
                    );
                    if (groupHeaderElement.length) {
                        groupHeaderElement.closest("tr").show();
                    }
                    break;
                }
            }
        };
        // We have to listen to several events to properly stop the resizing function. Those are:
        // - pointerdown (e.g. pressing right click)
        // - pointerup : logical flow of the resizing feature (drag & drop)
        // - keydown : (e.g. pressing 'Alt' + 'Tab' or 'Windows' key)
        for (const eventType of resizeStoppingEvents) {
            window.addEventListener(eventType, stopResize);
        }
    },

    /**
     * Cập nhật position trong multiheader khi thêm/xóa column
     * @param {Array} multiheader - Array chứa các header với position
     * @param {number} columnPosition - Vị trí column bị thêm/xóa (bắt đầu từ 1)
     * @param {string} action - 'add' hoặc 'remove'
     * @returns {Array} Multiheader đã được cập nhật
     */
    updateMultiheaderPosition(multiheader, columnPosition, action, drap_info) {
        const targetPosition = columnPosition;
        if (action == "drag_drop") {
            const table = this.tableRef.el;
            const { fromIndex, toIndex } = drap_info;
            let headers;
            let indexForRemoveBorderTop = 0
            if (fromIndex < toIndex)
                indexForRemoveBorderTop = fromIndex;
            else if (fromIndex > toIndex)
                indexForRemoveBorderTop = toIndex;
            if (this.context?.multiheader) {
                headers = [...table.querySelectorAll('tr:last-child th:not(.o_list_actions_header):not(.o_list_record_selector)')];
            }
            else {
                headers = [...table.querySelectorAll("thead th:not(.o_list_actions_header):not(.o_list_record_selector)")];
            }
            headers[indexForRemoveBorderTop].classList.remove("no-border-top");
            const span = headers[indexForRemoveBorderTop].querySelector("div span");
            if (span) {
                span.style.cssText = "";
            }

            this.mainRowThs
            let is_inside = false;
            multiheader.map((header, index) => {
                const [startPos, endPos] = header.position.split(',').map(Number);
                if (startPos <= fromIndex && fromIndex <= endPos && startPos <= toIndex && toIndex <= endPos) {
                    is_inside = true;
                    console.log(startPos, endPos)
                }
            })
            if (is_inside == true)
                return multiheader;
            let update_multiheader = multiheader.map((header, index) => {
                const [startPos, endPos] = header.position.split(',').map(Number);
                let newStartPos = startPos;
                let newEndPos = endPos;
                // Case 1: Header chứa cột được di chuyển (fromIndex)
                if (startPos <= fromIndex && fromIndex <= endPos) {
                    // Giảm endPos vì mất 1 cột
                    newEndPos = endPos - 1;
                    // // Nếu header trở thành invalid
                    // if (newStartPos > newEndPos) {
                    //     console.warn(`Header "${header.label}" becomes invalid after moving column ${fromIndex}`);
                    //     return null; // Hoặc xử lý theo cách khác
                    // }
                }

                // Case 2: Header nằm hoàn toàn giữa fromIndex và toIndex
                else if (fromIndex < startPos) {
                    // Dịch chuyển toàn bộ sang trái 1 vị trí
                    newStartPos = startPos - 1;
                    newEndPos = endPos - 1;
                }
                // (không cần xử lý gì)

                return {
                    ...header,
                    position: `${newStartPos},${newEndPos}`
                };
            })
            console.log(update_multiheader)

            let is_move = false
            update_multiheader = update_multiheader.map((header, index) => {
                const [startPos, endPos] = header.position.split(',').map(Number);
                let newStartPos = startPos;
                let newEndPos = endPos;
                // if (fromIndex > toIndex) // Qua trái
                // {
                if (header.label == "-") {
                    if (toIndex - endPos == 1) {
                        newEndPos = endPos + 1;
                        is_move = true;
                    }

                    else if (startPos <= toIndex && endPos >= toIndex) {
                        newEndPos = endPos + 1;
                        if (is_move) {
                            newStartPos = startPos + 1;
                        }

                    }
                    else if (endPos > toIndex) {
                        newEndPos = endPos + 1;
                        newStartPos = startPos + 1;
                    }
                }
                else {
                    if (startPos <= toIndex && endPos >= toIndex) {
                        newEndPos = endPos + 1;
                        if (is_move) {
                            newStartPos = startPos + 1;
                        }
                    }
                    else if (endPos > toIndex) {
                        newEndPos = endPos + 1;
                        newStartPos = startPos + 1;
                    }
                    // (không cần xử lý gì)
                }
                return {
                    ...header,
                    position: `${newStartPos},${newEndPos}`
                };
            })
            console.log(update_multiheader)
            return update_multiheader;
        }
        else if (action === "add") {
            return multiheader.map((header, index) => {
                // Tách start và end position
                const [startPos, endPos] = header.position.split(",").map(Number);
                let newStartPos = startPos;
                let newEndPos = endPos;
                // Kiểm tra nếu columnPosition nằm trong khoảng [startPos, endPos]
                if (startPos <= targetPosition && targetPosition <= endPos) {
                    // Tăng endPos để mở rộng khoảng
                    // newEndPos = endPos + 1;
                }
                // Nếu toàn bộ khoảng nằm sau targetPosition
                else if (startPos > targetPosition) {
                    // Dịch chuyển toàn bộ khoảng sang phải
                    newStartPos = startPos + 1;
                    newEndPos = endPos + 1;
                }
                // Nếu khoảng nằm hoàn toàn trước targetPosition thì không thay đổi
                return {
                    ...header,
                    position: `${newStartPos},${newEndPos}`,
                };
            });
        } else if (action === "remove") {
            return multiheader.map((header, index) => {
                // Tách start và end position
                const [startPos, endPos] = header.position.split(",").map(Number);
                let newStartPos = startPos;
                let newEndPos = endPos;
                // Kiểm tra nếu columnPosition nằm trong khoảng [startPos, endPos]
                if (startPos <= targetPosition && targetPosition <= endPos) {
                    // Thu hẹp khoảng
                    newEndPos = endPos - 1;
                    // Nếu khoảng trở thành rỗng (startPos > endPos), cần xử lý đặc biệt
                    if (newStartPos > newEndPos) {
                        // Có thể return null hoặc đánh dấu để xóa header này
                        console.warn(
                            `Header "${header.label}" becomes invalid after removing column ${targetPosition}`
                        );
                    }
                }
                // Nếu toàn bộ khoảng nằm sau targetPosition
                else if (startPos > targetPosition) {
                    // Dịch chuyển toàn bộ khoảng sang trái
                    newStartPos = startPos - 1;
                    newEndPos = endPos - 1;
                }
                // Nếu khoảng nằm hoàn toàn trước targetPosition thì không thay đổi
                return {
                    ...header,
                    position: `${newStartPos},${newEndPos}`,
                };
            });
        }
    },
});
