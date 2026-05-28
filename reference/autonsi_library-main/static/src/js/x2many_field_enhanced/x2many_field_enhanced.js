/** @odoo-module **/
import { registry } from "@web/core/registry";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillUpdateProps, onWillStart } from "@odoo/owl";

/**
 * Enhanced ListRenderer với hỗ trợ server-side grouping
 */
class X2ManyGroupedListRenderer extends ListRenderer {
  static template = "autonsi_library.X2ManyGroupedListRenderer";

  setup() {
    super.setup();
    this.orm = useService("orm");
    
    // DEBUG: Check props
    console.log('X2ManyGroupedListRenderer props:', {
      onAdd: this.props.onAdd,
      editable: this.props.editable,
      activeActions: this.activeActions,
      list: this.props.list
    });
    
    this.groupState = useState({
      expandedGroups: new Set(),
      serverGroups: null,
      loading: false,
      allGroupsExpanded: true,
    });

    this.state = useState({
      ...this.state,
      allGroupsExpanded: true,
    });

    onWillStart(async () => {
      await this._loadServerGroups();
    });

    onWillUpdateProps(async (nextProps) => {
      if (this._shouldReloadGroups(nextProps)) {
        await this._loadServerGroups(nextProps);
      }
      this._updateExpandedGroupsOnPropsChange(nextProps);
    });
  }

  _shouldReloadGroups(nextProps) {
    const currentRecordIds = this.props.list.records.map(r => r.id).sort().join(',');
    const nextRecordIds = nextProps.list.records.map(r => r.id).sort().join(',');
    return currentRecordIds !== nextRecordIds;
  }

  /**
   * GỌI web_read_group TỪ SERVER
   */
  async _loadServerGroups(props = this.props) {
    const groupByField = this.getGroupByField(props);
    if (!groupByField) {
      this.groupState.serverGroups = null;
      return;
    }

    const list = props.list;
    
    // ✅ Lấy IDs của records hiện có
    const recordIds = list.records.map(r => r.resId || r.id).filter(Boolean);
    
    if (recordIds.length === 0) {
      this.groupState.serverGroups = null;
      return;
    }

    this.groupState.loading = true;

    try {
      // ✅ Domain chỉ lấy records có ID trong list hiện tại
      const domain = [['id', 'in', recordIds]];
      
      console.log('🔍 Domain for web_read_group:', domain);
      
      const fields = Object.keys(list.fields);

      const result = await this.orm.webReadGroup(
        list.resModel,
        domain,
        fields,
        [groupByField],
        {
          lazy: true,
          limit: false,
        }
      );

      this.groupState.serverGroups = this._processServerGroups(result, groupByField, props);

      // Mở tất cả groups mặc định
      this.groupState.serverGroups.forEach(group => {
        this.groupState.expandedGroups.add(group.key);
      });

    } catch (error) {
      console.error("Error loading server groups:", error);
      this.groupState.serverGroups = null;
    } finally {
      this.groupState.loading = false;
    }
  }

  /**
   * XỬ LÝ DỮ LIỆU TỪ web_read_group
   */
  _processServerGroups(result, groupByField, props) {
    const groups = [];
    const field = props.list.fields[groupByField];
    const recordsMap = new Map();

    props.list.records.forEach(record => {
      const fieldValue = record.data[groupByField];
      let groupKey;

      if (field.type === 'many2one') {
        groupKey = Array.isArray(fieldValue) ? fieldValue[0] : fieldValue;
      } else {
        groupKey = fieldValue !== false && fieldValue !== null ? fieldValue : 'undefined';
      }

      if (!recordsMap.has(groupKey)) {
        recordsMap.set(groupKey, []);
      }
      recordsMap.get(groupKey).push(record);
    });

    result.groups.forEach(serverGroup => {
      const groupValue = serverGroup[groupByField];
      let groupKey, groupDisplay;

      if (field.type === 'many2one') {
        if (Array.isArray(groupValue) && groupValue.length >= 2) {
          groupKey = groupValue[0];
          groupDisplay = groupValue[1];
        } else {
          groupKey = groupValue || 'undefined';
          groupDisplay = groupValue ? String(groupValue) : 'Undefined';
        }
      } else {
        groupKey = groupValue !== false && groupValue !== null ? groupValue : 'undefined';
        groupDisplay = groupValue !== false && groupValue !== null ? String(groupValue) : 'Undefined';
      }

      const records = recordsMap.get(groupKey) || [];
      const aggregates = this._extractServerAggregates(serverGroup, props);

      groups.push({
        key: groupKey,
        display: groupDisplay,
        records: records,
        count: serverGroup[`${groupByField}_count`] || records.length,
        fieldName: groupByField,
        field: field,
        aggregates: aggregates,
        serverGroup: serverGroup,
        // Thêm groupValue để dùng khi tạo record mới
        groupValue: groupValue,
      });
    });

    return groups.sort((a, b) => {
      if (a.key === 'undefined') return 1;
      if (b.key === 'undefined') return -1;
      return String(a.display).localeCompare(String(b.display));
    });
  }

  /**
   * TRÍCH XUẤT AGGREGATES TỪ SERVER
   */
  _extractServerAggregates(serverGroup, props) {
    const aggregates = {};

    this.state.columns.forEach(column => {
      if (column.type !== 'field') return;

      const fieldName = column.name;
      const value = serverGroup[fieldName];

      if (value && typeof value === 'object' && value.widget === 'pro') {
        aggregates[fieldName] = value.value;
        return;
      }

      const field = props.list.fields[fieldName];
      if (field && ['integer', 'float', 'monetary'].includes(field.type)) {
        if (typeof value === 'number') {
          aggregates[fieldName] = value;
        }
      }
    });

    return aggregates;
  }

  get groupedRecords() {
    debugger
    if (this.groupState.serverGroups) {
      return this.groupState.serverGroups;
    }
    return this._clientSideGrouping();
  }

  /**
   * FALLBACK: Group ở client-side
   */
  _clientSideGrouping() {
    const groupByField = this.getGroupByField();
    if (!groupByField) {
      return null;
    }

    const records = this.props.list.records;
    if (!records || records.length === 0) {
      return null;
    }

    // Implement client-side grouping logic here if needed
    return null;
  }

  getGroupByField(props = this.props) {
    const context = props.list.context || {};
    const groupBys = context.list_groupbys ||
      context.group_by ||
      context.groupby ||
      [];

    if (Array.isArray(groupBys) && groupBys.length > 0) {
      const groupBy = groupBys[0];
      return groupBy.split(':')[0];
    }

    return null;
  }

  toggleGroup(groupKey) {
    if (this.groupState.expandedGroups.has(groupKey)) {
      this.groupState.expandedGroups.delete(groupKey);
    } else {
      this.groupState.expandedGroups.add(groupKey);
    }
    
    this._updateAllGroupsExpandedState();
  }

  isGroupExpanded(groupKey) {
    return this.groupState.expandedGroups.has(groupKey);
  }

  toggleAllGroups() {
    const groups = this.groupedRecords;
    if (!groups) return;

    if (this.state.allGroupsExpanded) {
      this.collapseAllGroups();
    } else {
      this.expandAllGroups();
    }
  }

  expandAllGroups() {
    const groups = this.groupedRecords;
    if (groups) {
      groups.forEach(group => {
        this.groupState.expandedGroups.add(group.key);
      });
      this.state.allGroupsExpanded = true;
    }
  }

  collapseAllGroups() {
    this.groupState.expandedGroups.clear();
    this.state.allGroupsExpanded = false;
  }

  getGroupAggregates(group) {
    return group.aggregates || {};
  }

  _updateAllGroupsExpandedState() {
    const groups = this.groupedRecords;
    if (!groups) return;

    const allExpanded = groups.every(group => 
      this.groupState.expandedGroups.has(group.key)
    );
    
    this.state.allGroupsExpanded = allExpanded;
  }

  _updateExpandedGroupsOnPropsChange(nextProps) {
    const currentGroupKeys = this.groupedRecords?.map(g => g.key) || [];
    const currentSet = new Set(currentGroupKeys);

    const keysToRemove = [];
    this.groupState.expandedGroups.forEach(key => {
      if (!currentSet.has(key)) {
        keysToRemove.push(key);
      }
    });
    keysToRemove.forEach(key => {
      this.groupState.expandedGroups.delete(key);
    });
    
    this._updateAllGroupsExpandedState();
  }

  /**
   * Add record vào group cụ thể
   */
  async addInGroupByKey(groupKey) {
    const group = this.groupedRecords.find(g => g.key === groupKey);
    if (!group) {
      console.error('Group not found:', groupKey);
      return;
    }

    // Tạo context với giá trị mặc định cho field groupBy
    const context = {};
    
    if (group.fieldName && group.groupValue !== undefined) {
      if (group.field.type === 'many2one') {
        context[`default_${group.fieldName}`] = Array.isArray(group.groupValue) 
          ? group.groupValue[0] 
          : group.groupValue;
      } else {
        context[`default_${group.fieldName}`] = group.groupValue;
      }
    }

    console.log('addInGroupByKey - Group:', group);
    console.log('addInGroupByKey - Context:', context);
    console.log('addInGroupByKey - Props.onAdd exists:', !!this.props.onAdd);

    // SỬ DỤNG props.onAdd
    if (this.props.onAdd) {
      try {
        await this.props.onAdd({ 
          context, 
          editable: this.props.editable || "bottom"
        });
        
        console.log('addInGroupByKey - onAdd completed');
        console.log('addInGroupByKey - List records after add:', this.props.list.records);
        
        // Sau khi add, reload server groups để cập nhật
        await this._loadServerGroups();
        
        console.log('addInGroupByKey - Groups after reload:', this.groupedRecords);
      } catch (error) {
        console.error('addInGroupByKey - Error:', error);
      }
    } else {
      console.error('props.onAdd not found!');
    }
  }

  async onCellClicked(record, column, ev) {
    if (this.groupedRecords) {
      return super.onCellClicked(record, column, ev);
    }
    return super.onCellClicked(record, column, ev);
  }

  get canCreate() {
    return "link" in this.activeActions ? this.activeActions.link : this.activeActions.create;
  }

  get isX2Many() {
    return this.activeActions.type !== "view";
  }

  get displayRowCreates() {
    const result = this.isX2Many && this.canCreate;
    console.log('displayRowCreates:', {
      isX2Many: this.isX2Many,
      canCreate: this.canCreate,
      editable: this.props.editable,
      activeActions: this.activeActions,
      result: result
    });
    return result;
  }
}

/**
 * Enhanced X2Many Field
 */
export class X2ManyEnhanced extends X2ManyField {
  static template = "autonsi_library.X2ManyEnhanced";
  static components = {
    ...X2ManyField.components,
    X2ManyGroupedListRenderer,
  };

  setup() {
    super.setup();

    this.groupedState = useState({
      useGroupedRenderer: this._shouldUseGroupedRenderer(),
    });
  }

  _shouldUseGroupedRenderer() {
    if (this.props.viewMode !== 'list') {
      return false;
    }

    const context = this.list?.context || {};
    const groupBys = context.list_groupbys ||
      context.group_by ||
      context.groupby ||
      [];

    return Array.isArray(groupBys) && groupBys.length > 0;
  }

  get shouldUseGroupedRenderer() {
    return this.groupedState.useGroupedRenderer;
  }

  get groupedRendererProps() {
    return this.rendererProps;
  }
}

export const x2ManyEnhanced = {
  ...x2ManyField,
  component: X2ManyEnhanced,
};

registry.category("fields").add("x2many_field_enhanced", x2ManyEnhanced);