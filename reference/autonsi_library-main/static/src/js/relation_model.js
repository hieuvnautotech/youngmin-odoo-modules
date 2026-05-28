// /** @odoo-module **/


// import { RelationalModel } from "@web/model/relational_model/relational_model";
// import { patch } from "@web/core/utils/patch";


// import { Domain } from "@web/core/domain";
// import {
//     extractInfoFromGroupData,
//     isRelational,
//     makeActiveField,
// } from "@web/model/relational_model/utils";

// // Lưu reference đến hàm gốc
// const originalExtractInfoFromGroupData = extractInfoFromGroupData;
// const AGGREGATABLE_FIELD_TYPES = ["float", "integer", "monetary"]; // types that can be aggregated in grouped views

// export function extractInfoFromGroupDataCustom(groupData, groupBy, fields) {
//     // Gọi hàm gốc để lấy kết quả ban đầu
//     const info = originalExtractInfoFromGroupData(groupData, groupBy, fields);
//     info.aggregates = getAggregatesFromGroupData(groupData, fields);
//     return info;
// }

// function getAggregatesFromGroupData(groupData, fields) {
//     const aggregates = {};
//     for (const [key, value] of Object.entries(groupData)) {
//         if (key in fields && (AGGREGATABLE_FIELD_TYPES.includes(fields[key].type) || value.widget == "pro")) {
//             if (value.widget == "pro")
//                 aggregates[key] = value.value;
//             else
//                 aggregates[key] = value;
//         }
//     }
//     return aggregates;
// }

// patch(RelationalModel.prototype, {
//     setup() {
//         super.setup(...arguments)
//     },
//     async _loadGroupedList(config) {
//         config.offset = config.offset || 0;
//         config.limit = config.limit || this.initialGroupsLimit;
//         if (!config.limit) {
//             config.limit = config.openGroupsByDefault
//                 ? this.constructor.DEFAULT_OPEN_GROUP_LIMIT
//                 : this.constructor.DEFAULT_GROUP_LIMIT;
//         }
//         config.groups = config.groups || {};
//         const firstGroupByName = config.groupBy[0].split(":")[0];
//         if (firstGroupByName.includes(".")) {
//             if (!config.fields[firstGroupByName]) {
//                 await this._getPropertyDefinition(config, firstGroupByName);
//             }
//             const propertiesFieldName = firstGroupByName.split(".")[0];
//             if (!config.activeFields[propertiesFieldName]) {
//                 // add the properties field so we load its data when reading the records
//                 // so when we drag and drop we don't need to fetch the value of the record
//                 config.activeFields[propertiesFieldName] = makeActiveField();
//             }
//         }
//         const orderBy = config.orderBy.filter(
//             (o) =>
//                 o.name === firstGroupByName ||
//                 (o.name in config.activeFields &&
//                     config.fields[o.name].group_operator !== undefined)
//         );
//         const response = await this._webReadGroup(config, firstGroupByName, orderBy);
//         const { groups: groupsData, length } = response;
//         const groupBy = config.groupBy.slice(1);
//         const groupByField = config.fields[config.groupBy[0].split(":")[0]];
//         const commonConfig = {
//             resModel: config.resModel,
//             fields: config.fields,
//             activeFields: config.activeFields,
//         };
//         let groupRecordConfig;
//         const groupRecordResIds = [];
//         if (this.groupByInfo[firstGroupByName]) {
//             groupRecordConfig = {
//                 ...this.groupByInfo[firstGroupByName],
//                 resModel: config.fields[firstGroupByName].relation,
//                 context: {},
//             };
//         }
//         const proms = [];
//         let nbOpenGroups = 0;

//         const groups = [];
//         for (const groupData of groupsData) {
//             const group = extractInfoFromGroupDataCustom(groupData, config.groupBy, config.fields);
//             if (!config.groups[group.value]) {
//                 config.groups[group.value] = {
//                     ...commonConfig,
//                     groupByFieldName: groupByField.name,
//                     isFolded:
//                         "__fold" in groupData ? groupData.__fold : !config.openGroupsByDefault,
//                     extraDomain: false,
//                     value: group.value,
//                     list: {
//                         ...commonConfig,
//                         groupBy,
//                     },
//                 };
//                 if (isRelational(config.fields[firstGroupByName]) && !group.value) {
//                     // fold the "unset" group by default when grouped by many2one
//                     config.groups[group.value].isFolded = true;
//                 }
//                 if (groupRecordConfig) {
//                     config.groups[group.value].record = {
//                         ...groupRecordConfig,
//                         resId: group.value ?? false,
//                     };
//                 }
//             }
//             if (groupRecordConfig) {
//                 const resId = config.groups[group.value].record.resId;
//                 if (resId) {
//                     groupRecordResIds.push(resId);
//                 }
//             }
//             const groupConfig = config.groups[group.value];
//             groupConfig.list.orderBy = config.orderBy;
//             groupConfig.initialDomain = group.domain;
//             if (groupConfig.extraDomain) {
//                 groupConfig.list.domain = Domain.and([
//                     group.domain,
//                     groupConfig.extraDomain,
//                 ]).toList();
//             } else {
//                 groupConfig.list.domain = group.domain;
//             }
//             const context = {
//                 ...config.context,
//                 [`default_${firstGroupByName}`]: group.serverValue,
//             };
//             groupConfig.list.context = context;
//             groupConfig.context = context;
//             if (groupBy.length) {
//                 group.groups = [];
//             } else {
//                 group.records = [];
//             }
//             if (!groupConfig.isFolded) {
//                 nbOpenGroups++;
//                 if (nbOpenGroups > this.constructor.MAX_NUMBER_OPENED_GROUPS) {
//                     groupConfig.isFolded = true;
//                 }
//             }
//             if (!groupConfig.isFolded && group.count > 0) {
//                 const prom = this._loadData(groupConfig.list).then((response) => {
//                     if (groupBy.length) {
//                         group.groups = response ? response.groups : [];
//                         group.length = response ? response.length : 0;
//                     } else {
//                         group.records = response ? response.records : [];
//                     }
//                 });
//                 proms.push(prom);
//             }
//             groups.push(group);
//         }
//         if (groupRecordConfig && Object.keys(groupRecordConfig.activeFields).length) {
//             const prom = this._loadRecords({
//                 ...groupRecordConfig,
//                 resIds: groupRecordResIds,
//             }).then((records) => {
//                 for (const group of groups) {
//                     if (!group.value) {
//                         group.values = { id: false };
//                         continue;
//                     }
//                     group.values = records.find((r) => group.value && r.id === group.value);
//                 }
//             });
//             proms.push(prom);
//         }
//         await Promise.all(proms);

//         // if a group becomes empty at some point (e.g. we dragged its last record out of it), and the view is reloaded
//         // with the same domain and groupbys, we want to keep the empty group in the UI
//         const params = JSON.stringify([
//             config.domain,
//             config.groupBy,
//             config.offset,
//             config.limit,
//             config.orderBy,
//         ]);
//         if (config.currentGroups && config.currentGroups.params === params) {
//             const currentGroups = config.currentGroups.groups;
//             currentGroups.forEach((group, index) => {
//                 if (
//                     config.groups[group.value] &&
//                     !groups.some((g) => JSON.stringify(g.value) === JSON.stringify(group.value))
//                 ) {
//                     const aggregates = Object.assign({}, group.aggregates);
//                     for (const key in aggregates) {
//                         aggregates[key] = 0;
//                     }
//                     groups.splice(
//                         index,
//                         0,
//                         Object.assign({}, group, { count: 0, length: 0, records: [], aggregates })
//                     );
//                 }
//             });
//         }
//         config.currentGroups = { params, groups };

//         return { groups, length };
//     }

// })

