/** @odoo-module */

import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';
import { useBus, useService } from '@web/core/utils/hooks';
import { localization } from '@web/core/l10n/localization';
import { usePopover } from '@web/core/popover/popover_hook';
import { condition, domainFromTree } from '@web/core/tree_editor/condition_tree';
import { getValueEditorInfo, getDefaultValue } from '@web/core/tree_editor/tree_editor_value_editors';
import { useLoadFieldInfo } from '@web/core/model_field_selector/utils';

import { Domain } from '@web/core/domain';
import { ListRenderer } from '@web/views/list/list_renderer';
import { Dropdown } from '@web/core/dropdown/dropdown';
import { DropdownItem } from '@web/core/dropdown/dropdown_item';
import { DomainSelectorDialog } from '@web/core/domain_selector_dialog/domain_selector_dialog';
import { Component, onWillStart, useState } from '@odoo/owl';

import { useUdooStore, useUdooLocalStore } from '@omux_state_manager/store';

import { DataFilterPopOver } from '../editor/data_filter';
import { getDomainDisplayedOperators } from '../editor/domain_selector_operator_editor';

export class QuickColumnFilterPopOver extends Component { }
QuickColumnFilterPopOver.components = { DropdownItem }
QuickColumnFilterPopOver.template = 'uweb.QuickColumnFilterPopOver';


ListRenderer.components = { ...ListRenderer.components, Uropdown: Dropdown }

patch(ListRenderer.prototype, {
    setup() {
        super.setup();

        this.ue = useUdooLocalStore();
        this.uo = useUdooStore();
        this.uState = useState({});

        this.loadFieldInfo = useLoadFieldInfo();
        this.notification = useService('notification');
        this.user = useService('user');
        this.rpc = useService('rpc');

        const direction = localization.direction === 'rtl' ? 'bottom' : 'right';
        this.dropover = usePopover(QuickColumnFilterPopOver, {
            position: direction,
            closeOnClickAway: true,
            fixedPosition: true,
            popoverClass: 'fs-6',
            animation: false,
        });
        this.filtover = usePopover(DataFilterPopOver, {
            arrow: true,
            position: 'bottom',
            popoverClass: 'fs-6',
        });

        useBus(this.env.bus, 'CTL:USEFBR', async () => {
            this.uo.useFilterBar = true;
            if (!this.uState.fieldDefsLocked) {
                this.loadColumnFieldDefs(this.state.columns);
            }
        });

        onWillStart(async () => {
            const { resModel } = this.env.model.config;
            if (!this.uo.filterValues) {
                this.uo.filterValues = { '_FK_': resModel };
            } else if (this.uo.filterValues['_FK_'] !== resModel) {
                this.uo.filterValues = { '_FK_': resModel };
            }
            if (this.uo.useFilterBar && !this.uState.fieldDefsLocked) {
                await this.loadColumnFieldDefs(this.state.columns);
            }
        });
    },

    async loadColumnFieldDefs(columns) {
        const { resModel } = this.env.model.config;
        const paths = columns.map(column => column.name);

        const promises = [];
        const fieldDefs = {};
        for (const path of paths) {
            if (typeof path === 'string') {
                promises.push(
                    this.loadFieldInfo(resModel, path).then(({ fieldDef }) => {
                        fieldDefs[path] = fieldDef;
                    })
                );
            }
        }
        await Promise.all(promises);

        this.uFieldDefs = fieldDefs;
        this.uState.fieldDefsLocked = true;
    },

    getColumnEditorInfo(column) {
        const fieldDef = this.uFieldDefs[column.name];
        const operator = getDomainDisplayedOperators(fieldDef)[0];
        const inf = getValueEditorInfo(fieldDef, operator, { addBlankOption: true });

        if (inf.component.name == 'DateTimeInput') {
            inf.mutGetter = () => false;
        }
        else if (inf.defaultValue() == 1) {
            inf.mutGetter = () => '';
        } else {
            inf.mutGetter = () => inf.defaultValue();
        }

        inf.valueSetter = async (value) => {
            const domain = await this._validateFilterDomain(column.name, operator, value);
            if (domain) {
                this._applyColumnFilter(column.name, domain);
            }
        }
        if (inf.component.name == 'DomainSelectorAutocomplete' && column.domain) {
            const domain = new Domain(column.domain).toList();
            const originalExtractProps = inf.extractProps;
            inf.extractProps = ({ value, update }) => {
                return {
                    ...originalExtractProps({ value, update }),
                    domain: domain,
                };
            }
        }
        return inf;
    },

    uIsStorable(column) {
        // if (this.fields[column.name]) {
        //     return this.fields[column.name].store;
        // }
        return true;
    },

    uQuickFilterPop(column) {
        const targetEl = this.rootRef.el.querySelector(`.elvf_${column.name}`);
        this.dropover.open(targetEl, {
            widget: this,
            items: this.uSearchFilter(column),
            itemClass: 'lh-ud',
            emptyMsg: _t('No column filters found.'),
            popAction: (item) => this.uQuisToggleSearchItem(item),
        });
    },

    uQuisToggleSearchItem(searchItem) {
        this.closeCurrentPop('elv_dropfunc');
        this.env.searchModel.toggleSearchItem(searchItem.id);
    },

    uSortAscending(column) {
        this.props.list.uSortBy(column.name, true);
    },

    uSortDescending(column) {
        this.props.list.uSortBy(column.name, false);
    },

    uResetSort(column) {
        this.props.list.uSortReset(column.name);
    },

    uToggleGroupPop(column) {
        const targetEl = this.rootRef.el.querySelector(`.elvg_${column.name}`);
        this.dropover.open(targetEl, {
            widget: this,
            items: [
                { description: _t('Year'), id: 'year' },
                { description: _t('Quarter'), id: 'quarter' },
                { description: _t('Month'), id: 'month' },
                { description: _t('Week'), id: 'week' },
                { description: _t('Day'), id: 'day' },
            ],
            popAction: (item) => {
                this.closeCurrentPop('elv_dropfunc');
                this.uToggleGroup(column, false, item.id);
            },
        });
    },

    uToggleGroup(column, revert = false, interval = 'day') {
        function groupMacher(item) {
            return item.fieldName == column.name && ['groupBy', 'dateGroupBy'].includes(item.type);
        }

        let searchItem = this.env.searchModel.getSearchItems(
            (searchItem) => groupMacher(searchItem)
        );

        if (revert) {
            if (searchItem.length) {
                this.env.searchModel.uToggleSearchItem(searchItem[0].id, true);
            }
            return;
        }

        if (!searchItem.length) {
            let config = { interval, label: column.label };
            this.env.searchModel.uCreateNewGroupBy(column.name, config);
            return;
        } else {
            let { options, id: itemId } = searchItem[0];
            if (options) {
                // TODO: Support multi interval on toggle menu
                this.env.searchModel.toggleDateGroupBy(itemId, interval);
            } else {
                this.env.searchModel.toggleSearchItem(itemId);
            }
        }
    },

    uSearchFilter(column) {
        function filterMacher(item) {
            return item.type == 'filter' && item.domain.includes(column.name);
        }
        return this.env.searchModel.getSearchItems(
            (searchItem) => filterMacher(searchItem)
        );
    },

    uResetFilter(column) {
        function filterMacher(item) {
            return item.type == 'filter' && item.domain.includes(column.name);
        }
        const filterItems = this.env.searchModel.uGetSearchItems(
            (searchItem) => filterMacher(searchItem)
        );
        this.env.searchModel.uFilterReset(filterItems);
    },

    uAddCustomFilter(column) {
        const { domainEvalContext: context, resModel } = this.env.searchModel;

        const supportedTypes = column.field.supportedTypes;
        let ope = 'in', opv = '[]';
        if (supportedTypes?.length) {
            if (supportedTypes.includes('char') && !supportedTypes.includes('selection')) {
                ope = 'ilike'; opv = `''`;
            } else if (supportedTypes.includes('date')) {
                const nowStr = luxon.DateTime.utc().toFormat('yyyy-MM-dd HH:mm:ss');
                ope = 'between'; opv = `['${nowStr}', '${nowStr}']`;
            } else if (supportedTypes.includes('float') || supportedTypes.includes('integer')) {
                ope = '=';
            }
        }

        const domain = `[('${column.name}', '${ope}', ${opv})]`;
        this.env.services.dialog.add(DomainSelectorDialog, {
            resModel,
            defaultConnector: '|',
            domain,
            context,
            onConfirm: (domain) => this._applyColumnFilter(column.name, domain),
            disableConfirmButton: (domain) => domain === `[]`,
            title: _t('Filter by ' + column.label),
            confirmButtonText: _t('Apply'),
            discardButtonText: _t('Cancel'),
            isDebugMode: this.env.searchModel.isDebugMode,
        });
    },

    triggerColPop(column) {
        const targetEl = this.rootRef.el.querySelector(`.elvc_${column.name}`);
        if (targetEl) {
            targetEl.click();
        }
    },

    openInlaceFilter(ev, column) {
        if (this.filtover.isOpen) {
            this.filtover.close();
            return;
        }
        const { resModel, isDebugMode } = this.env.searchModel;
        let defCondition = false;
        if (!this.uo.filterValues[column.name] || this.uo.filterValues[column.name] === '[]') {
            const fieldDef = this.uFieldDefs[column.name];

            const ope = getDomainDisplayedOperators(fieldDef)[0];
            const val = getDefaultValue(fieldDef, ope);
            defCondition = condition(fieldDef.name, ope, val);

            this.uo.filterValues[column.name] = domainFromTree(defCondition);
        }
        this.filtover.open(ev.target.closest('.form-control'), {
            widget: this,
            className: 'u_field_filter px-4 py-3',
            readonly: false,
            resModel,
            isDebugMode,
            defaultConnector: '|',
            forceFieldPath: column.name,
            defCondition: defCondition,
            domain: this.uo.filterValues[column.name],
            update: (domain, path) => {
                this.uo.filterValues[path] = domain;
            },
            applyDomain: (path) => {
                this._applyColumnFilter(column.name, this.uo.filterValues[path]);
            }
        });
    },

    closeCurrentPop(popClass) {
        this.dropover.close();
        const currentPop = this.rootRef.el.querySelector(`.${popClass}.show`);
        if (currentPop) {
            // NOTE: Manual closing of dropdown, make it auto
            currentPop.querySelector('button').click();
        }
    },

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    _clearColumnFilter(path) {
        const groupKey = '_GID_' + path;
        this._resetColumnFilter(groupKey);
        delete this.uo.filterValues[path];
        delete this.uo.filterValues[groupKey];
    },

    _resetColumnFilter(groupKey) {
        const currentGroup = this.uo.filterValues[groupKey];
        if (currentGroup) {
            this.env.searchModel.deactivateGroup(currentGroup);
        }
    },

    async _applyColumnFilter(path, domain) {
        const currentGroup = this.uo.filterValues['_GID_' + path];
        const callback = (groupId) => { this.uo.filterValues['_GID_' + path] = groupId; }
        await this.env.searchModel.uSplitAndAddDomain(domain, currentGroup, callback);

        this.uo.filterValues[path] = domain;
    },

    async _validateFilterDomain(path, operator, value) {
        const { resModel } = this.env.searchModel;

        let domain, domainStr, isValid;
        try {
            const evalContext = { ...this.user.context, ...this.env.searchModel.domainEvalContext };
            domainStr = domainFromTree(condition(path, operator, value));
            domain = new Domain(domainStr).toList(evalContext);
        } catch {
            isValid = false;
        }
        if (isValid === undefined) {
            isValid = await this.rpc('/web/domain/validate', {
                model: resModel,
                domain,
            });
        }
        if (!isValid) {
            this.notification.add(_t('Domain is invalid. Please correct it'), {
                type: 'danger',
            });
            return isValid;
        }
        return domainStr;
    },

    // -------------------------------------------------------------------------
    // Overridle
    // -------------------------------------------------------------------------

    onClickSortColumn(column) {
        if (this.rootRef.el.querySelector('.d-cfunc.show')) {
            return;
        }
        super.onClickSortColumn(column);
    },

    isSortable(column) {
        const { hasLabel, name, options } = column;
        const { sortable } = this.fields[name];
        return (sortable || options.allow_order) && hasLabel;
    }
});
