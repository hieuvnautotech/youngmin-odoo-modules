/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';
import { useBus, useService } from '@web/core/utils/hooks';
import { usePopover } from '@web/core/popover/popover_hook';
import { onWillStart, toRaw } from '@odoo/owl';

import { useUdooStore, useUdooLocalStore } from '@omux_state_manager/store';

import { ControlPanel } from '@web/search/control_panel/control_panel';
import { QuickColumnFilterPopOver } from '../patch/list_renderer';


patch(ControlPanel.prototype, {
    setup() {
        super.setup();

        this.ui = useService('ui');
        this.ue = useUdooLocalStore();
        this.uo = useUdooStore();

        this.filterTabPop = usePopover(QuickColumnFilterPopOver, {
            arrow: false,
        });

        onWillStart(async () => {
            const { config, searchModel } = this.env;
            const actionId = config.actionId;

            if (searchModel) {
                this.uFilterBarItems = searchModel.getSearchItems(o => ['filter', 'favorite'].includes(o.type));
            }

            if (actionId) {
                // Initialize actionAdvs if needed
                if (typeof this.ue.actionAdvs != 'object') {
                    this.ue.actionAdvs = {};
                }
                const actionAdvs = toRaw(this.ue).actionAdvs;

                // Handle list filter bar
                const useListFilterBarCtx = searchModel?.context?.use_list_filter_bar;
                if ((useListFilterBarCtx !== undefined && useListFilterBarCtx)) {
                    this.ue.actionAdvs[actionId] = true;
                }
                this.uo.useFilterBar = actionAdvs[actionId];

                // Handle filter nav bar
                const useFilterNavBarCtx = searchModel?.context?.use_filter_nav_bar;
                if (!actionAdvs['FTB_' + actionId] && (useFilterNavBarCtx !== undefined && useFilterNavBarCtx)) {
                    this.uToggleFilterTabBar();
                } else {
                    this.uo.useFilterTabBar = actionAdvs['FTB_' + actionId];
                }
            }

            // Set popup states
            this.uo.useFilterTabBarPop = this.uo.useFilterTabBar;
            this.uo.useFilterBarPop = this.uo.useFilterBar;
        });

        useBus(this.env.bus, 'ACTION_MANAGER:UI-UPDATED', () => {
            const { env, uo, ue } = this;
            const actionId = env.config.actionId;
            const actionAdvs = toRaw(ue).actionAdvs;

            if (env.config.viewType == 'list' && actionAdvs[actionId]) {
                env.bus.trigger('CTL:USEFBR');
            }
            uo.useFilterTabBar = actionAdvs['FTB_' + actionId];
        });
    },

    get uFilterPinnedTabs() {
        const { config, searchModel } = this.env;

        if (searchModel) {
            if (config.actionId) {
                const rawAdvs = toRaw(this.ue).actionAdvs['FTS_' + config.actionId];

                if (!rawAdvs) return [];

                return searchModel.getSearchItems((o) => {
                    return ['filter', 'favorite'].includes(o.type) && rawAdvs[o.id]
                });
            } else {
                return this.uFilterBarItems;
            }
        }
        return []
    },

    uFilterTabBarSetter(ev) {
        const { env, ue } = this;
        const actionId = env.config.actionId;

        this.filterTabPop.open(ev.target, {
            widget: this,
            items: this.uFilterBarItems,
            itemClass: 'ps-4',
            emptyMsg: _t('No filters found.'),
            popAction: (item, pop) => {
                if (!ue.actionAdvs['FTS_' + actionId]) {
                    ue.actionAdvs['FTS_' + actionId] = {};
                }
                ue.actionAdvs['FTS_' + actionId][item.id] = !ue.actionAdvs['FTS_' + actionId][item.id];
                pop.render();
            },
            isel: (item) => {
                const itemState = ue.actionAdvs['FTS_' + actionId];
                if (itemState) return itemState[item.id]
                return false;
            }
        });
    },

    uToggleFilterTabBar() {
        const { env, uo, ue, uFilterBarItems } = this;
        const actionId = env.config.actionId;

        if (actionId) {
            this.uo.useFilterTabBarPop = false; // Reset

            uo.useFilterTabBar = !uo.useFilterTabBar;
            if (uo.useFilterTabBar) {
                ue.actionAdvs['FTB_' + actionId] = true;

                const rawAdvs = toRaw(ue).actionAdvs['FTS_' + actionId];

                if (!rawAdvs) {
                    const defFtsSet = {};
                    uFilterBarItems.forEach(o => {
                        if (!o.isDefault) defFtsSet[o.id] = true;
                    });
                    ue.actionAdvs['FTS_' + actionId] = defFtsSet;
                }
            } else {
                delete ue.actionAdvs['FTB_' + actionId];
            }
        } else if (env.searchModel) {
            uo.useFilterTabBarPop = !uo.useFilterTabBarPop;
        }
    },

    uToggleFilterTab(item) {
        const { isDefault, id: itemId } = item;
        const { searchModel } = this.env;

        if (isDefault && searchModel.query.find((o) => o.searchItemId == item.id)) {
            return;
        }
        if (this.state.filterTab && searchModel.query.find((o) => o.searchItemId == this.state.filterTab)) {
            searchModel.toggleSearchItem(this.state.filterTab);
        }
        if (!isDefault) {
            this.state.filterTab = itemId;
        }
        searchModel.toggleSearchItem(itemId);
    },
});
