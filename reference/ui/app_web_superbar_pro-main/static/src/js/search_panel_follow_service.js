/** @odoo-module */

import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

export const searchPanelFollowService = {
    start() {
        // Khởi tạo trạng thái từ localStorage (nếu có)
        const savedState = browser.localStorage.getItem("search_panel_follows_state");
        const initialState = savedState
            ? JSON.parse(savedState)
            : {
                search_panel_follows: [],
                search_panel_follows_filter: [],
                id_customer_follow: 0,
                customer_name: "",
                id_customer_follow_filter: [],
                date_search: [],
                action_id: 0,
            };

        // Tạo trạng thái reactive
        const state = reactive(initialState);
        // Hàm lưu trạng thái vào localStorage
        const saveToLocalStorage = () => {
            browser.localStorage.setItem("search_panel_follows_state", JSON.stringify(state));
        };

        return {
            // Phương thức để thêm mục vào search_panel_follows
            addFollow(description, active_value) {
                const existingIndex = state.search_panel_follows.findIndex(
                    item => item.description === description
                );
                if (existingIndex !== -1) {
                    state.search_panel_follows[existingIndex].active_value = active_value;
                } else {
                    state.search_panel_follows.push({
                        description: description,
                        active_value: active_value,
                    });
                }
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },
            updateActionId(action_id) {
                state.action_id = action_id;
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },
            getActionId() {
                return state.action_id;
            },

            addDateSearch(field_name, dateObj) {
                let existingIndex = state.date_search.findIndex(
                    item => item.field_name === field_name
                );
                if (existingIndex !== -1) {
                    state.date_search[existingIndex].from_date = dateObj?.from;
                    state.date_search[existingIndex].to_date = dateObj?.to;
                } else {
                    state.date_search.push({
                        field_name: field_name,
                        from_date: dateObj.from,
                        to_date: dateObj.to,
                    });
                }
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            addFollowFilter(description, active_value) {
                const existingIndex = state.search_panel_follows_filter.findIndex(
                    item => item.description === description
                );
                if (existingIndex !== -1) {
                    const index = state.search_panel_follows_filter[existingIndex].active_values.findIndex(
                        item => item.id === active_value.id
                    );
                    if (index !== -1) {
                        state.search_panel_follows_filter[existingIndex].active_values[index].checked =
                            active_value.checked;
                    } else {
                        state.search_panel_follows_filter[existingIndex].active_values.push({
                            id: active_value.id,
                            checked: active_value.checked,
                        });
                    }
                } else {
                    state.search_panel_follows_filter.push({
                        description: description,
                        active_values: [
                            {
                                id: active_value.id,
                                checked: active_value.checked,
                            },
                        ],
                    });
                }
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            updateIdCustomerFollow(active_value, customer_name) {
                state.id_customer_follow = active_value;
                state.customer_name = customer_name;
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            updateIdCustomerFollowFilter(active_value) {
                const index = state.id_customer_follow_filter.findIndex(
                    item => item.id === active_value.id
                );
                if (index !== -1) {
                    if (!active_value.checked) {
                        state.id_customer_follow_filter.splice(index, 1);
                    }
                } else {
                    state.id_customer_follow_filter.push({
                        id: active_value.id,
                        checked: active_value.checked,
                        display_name: active_value.display_name,
                    });
                }
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            // Phương thức để lấy danh sách search_panel_follows
            getFollows() {
                return state.search_panel_follows;
            },

            getDateSearch(field_name) {
                return state.date_search.find(item => item.field_name === field_name) || null;
            },

            getAllDateSearch() {
                return state.date_search;
            },

            getFollowsFilter() {
                return state.search_panel_follows_filter;
            },

            getIdCustomerFollow() {
                return state.id_customer_follow;
            },
            getCustomerName() {
                return state.customer_name;
            },

            getIdCustomerFollowFilter(id) {
                const index = state.id_customer_follow_filter.findIndex(item => item.id === id);
                return index !== -1 ? state.id_customer_follow_filter[index].checked : false;
            },

            geAllIdCustomerFollowFilter() {
                return state.id_customer_follow_filter;
            },
            getAllCustomerName() {
                return state.id_customer_follow_filter.length > 0
                    ? state.id_customer_follow_filter.map(item => item.display_name) : []
            },

            // Phương thức để xóa danh sách search_panel_follows
            clearFollows() {
                state.search_panel_follows.length = 0;
                state.search_panel_follows_filter.length = 0;
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            clearDateSearch() {
                state.date_search.length = 0;
                saveToLocalStorage(); // Lưu vào localStorage sau khi thay đổi
            },

            // Phương thức tìm kiếm follow theo description và trả về active_value tương ứng
            findFollowByDescription(description) {
                const follow = state.search_panel_follows.find(
                    item => item.description === description
                );
                return follow ? follow.active_value : undefined;
            },

            findFollowFilterByDescriptionAndID(description, id) {
                const existingIndex = state.search_panel_follows_filter.find(
                    item => item.description === description
                );
                if (existingIndex) {
                    const index = existingIndex.active_values.findIndex(item => item.id === id);
                    return index !== -1 ? existingIndex.active_values[index].checked : false;
                }
                return false;
            },

            // Expose search_panel_follows để các override có thể sử dụng
            search_panel_follows: state.search_panel_follows,
        };
    },
};

registry.category("services").add("search_panel_follows", searchPanelFollowService);