/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import { condition, treeFromDomain } from '@web/core/tree_editor/condition_tree';
import { getDefaultValue } from '@web/core/tree_editor/tree_editor_value_editors';
import { deepEqual } from '@web/core/utils/objects';
import { Domain } from '@web/core/domain';
import { Component, useState } from '@odoo/owl';
import { DomainSelector } from '@web/core/domain_selector/domain_selector';
import { TreeEditor } from '@web/core/tree_editor/tree_editor';

import { getDomainDisplayedOperators } from './domain_selector_operator_editor';


export class DataFilterTreeEditor extends TreeEditor {
    static template = 'uweb.DataFilterTreeEditor'

}

const ARCHIVED_CONDITION = condition('active', 'in', [true, false]);

export class DataFilter extends DomainSelector {
    static components = { ...DomainSelector.components, 'TreeEditor': DataFilterTreeEditor };
    static template = 'uweb.DataFilter';
    static props = {
        ...DomainSelector.props, forceFieldPath: { type: String, optional: true },
    }

    async onPropsUpdated(p) {
        const paths = new Set([this.props.forceFieldPath, 'active']);
        await this.loadFieldDefs(p.resModel, paths);

        let defCondition = this.props.defCondition;
        if (!defCondition) {
            const fieldDef = this.fieldDefs[this.props.forceFieldPath];
            const operator = getDomainDisplayedOperators(fieldDef)[0];
            const value = getDefaultValue(fieldDef, operator);
            defCondition = condition(fieldDef.name, operator, value);
        }
        const domain = new Domain(p.domain);

        this.tree = treeFromDomain(domain, {
            getFieldDef: this.getFieldDef.bind(this),
            distributeNot: !p.isDebugMode,
        });
        this.defaultCondition = defCondition;

        this.showArchivedCheckbox = Boolean(this.fieldDefs.active);
        this.includeArchived = false;
        if (this.showArchivedCheckbox) {
            if (this.tree.value === '&') {
                this.tree.children = this.tree.children.filter((child) => {
                    if (deepEqual(child, ARCHIVED_CONDITION)) {
                        this.includeArchived = true;
                        return false;
                    }
                    return true;
                });
                if (this.tree.children.length === 1) {
                    this.tree = this.tree.children[0];
                }
            } else if (deepEqual(this.tree, ARCHIVED_CONDITION)) {
                this.includeArchived = true;
                this.tree = treeFromDomain(`[]`);
            }
        }
    }
}

export class DataFilterPopOver extends Component {
    static components = { DataFilter }
    static template = 'uweb.DataFilterPopOver'

    setup() {
        super.setup();
        this.orgDomain = this.props.domain;
        this.state = useState({ domain: this.props.domain });
    }

    apply() {
        this.props.applyDomain(this.props.forceFieldPath);
        this.props.close();
    }

    reset() {
        this.state.domain = this.orgDomain;
        this.props.update(this.orgDomain, this.props.forceFieldPath);
    }

    clear() {
        this.props.widget._clearColumnFilter(this.props.forceFieldPath);
        this.props.close();
    }

    get domainSelectorProps() {
        return {
            className: this.props.className,
            resModel: this.props.resModel,
            readonly: this.props.readonly,
            isDebugMode: this.props.isDebugMode,
            defaultConnector: this.props.defaultConnector,
            forceFieldPath: this.props.forceFieldPath,
            domain: this.state.domain,
            update: (domain) => {
                this.state.domain = domain;
                this.props.update(domain, this.props.forceFieldPath);
            },
        };
    }
}