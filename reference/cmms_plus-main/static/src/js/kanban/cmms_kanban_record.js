/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
const notGlobalActions = ["a", ".dropdown", ".oe_kanban_action", ".cmms-kanban-copy"].join(",");
import { ListController } from '@web/views/list/list_controller';
import { useBus, useService } from "@web/core/utils/hooks";
//const originalOpenRecord = ListController.prototype.openRecord;

export class CMMSKanbanRecord extends KanbanRecord {
       setup() {
        super.setup();
      
        this.orm = useService("orm");
       }
    /*
    * Re-write to add its own classes for selected kanban record
    */
    getRecordClasses() {
        let result = super.getRecordClasses();
        if (this.props.record.selected) {
            result += " cmms-kanban-selected";
        };
       // console.log(result,'.........666.....')
        //dòng này cho phép mỗi card đều xuống dòng
        //result += " w-100";

        result = result.replace('flex-grow-1','')
        return result += " w-432";
    }
    /*
    * The method to manage clicks on kanban record
    */
   async onGlobalClick(ev) {
        
        if (ev.target.closest(notGlobalActions)) {
            return;
        }
        else if (ev.target.closest(".cmms-kanban-select-box")) {
            this.props.record.onRecordClick(ev, {});
        }
        else {
            const { openRecord, record } = this.props;

                        localStorage.setItem('cmms_record_click', 1)
                       // console.log(record.model.config.resModel,record,'xxxxxxxxxxxxxxxxxxxxxxx')
                       if (record.data.is_machine) {
                                        const resid = record.resId;
                                        const view_form_id = await  this.orm.call("product.product", "getMachineFormViewId", [[]])
                                        this.env.services.action.doAction({
                                            type: 'ir.actions.act_window',
                                            name: 'Machine Info',
                                            res_model: 'product.product',
                                            res_id: resid,
                                            views: [[view_form_id, 'form']],
                                        });

                       } else {
                                //default jig
                             openRecord(record);
                       }

            }

    }
    /*
    * The method to get a record to change its values
    */
    onDragStart(event) {
        event.preventDefault(); // to avoid standard drag&drop
        // if (!this.props.record.selected) {
        //    this.props.record.toggleSelection(true); // before moving, a record should be added to the selection
        // };
        // const selectedRecords = this.props.record.model.selectedRecords.map(function(record) {
        //     return { id: "nodex_" + record.id, text: record.name, icon: "nodex_update" }
        // });
        // const draggableElement = document.createElement("div");
        // draggableElement.classList.add("jstree-default");
        // draggableElement.id = "jstree-dnd";
        // const draggableIcon = document.createElement("i");
        // draggableIcon.classList.add("jstree-icon", "jstree-er");
        // $(draggableIcon).appendTo(draggableElement);
        // const dragText = selectedRecords.length == 1 ? selectedRecords[0].text : selectedRecords.length + _t(" article(s)");
        // draggableElement.append(dragText);
        // $.vakata.dnd.start(event, {
        //     jstree: true,
        //     obj: $("<a>", { id: "dnd_anchor", class: "jstree-anchor", href: "#" }),
        //     nodes: selectedRecords,
        // }, draggableElement);
    }
};

CMMSKanbanRecord.template = "cmms.CMMSKanbanRecord";
