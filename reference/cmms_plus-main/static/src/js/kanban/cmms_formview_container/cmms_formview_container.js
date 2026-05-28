/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { useBus,useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted,onWillUnmount, useState, onWillUpdateProps } = owl;
import { View } from "@web/views/view";   // ✅ import component View



export class CMMSFormviewContainer extends Component {
    static template = "cmms.CMMSFormviewContainer";
     static components = { View };

    static props = {
      
        onUpdateSearch: { type: Function },
        kanbanModel: { type: Object },
        canCreate: { type: Boolean },
        controller: { type: Object },
        navigator : { type: Object }
        
    };
   
    setup() {
      
        this.state = useState({ showForm:0 });
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.rpcService = useService("rpc");
        this.notification = useService("notification");

        this.controller = this.props.controller;
        this.navigator = this.props.navigator
    
        this.yy = useState({ formProps: null });
      

        onWillStart(async () => {
          
        });
        onMounted(() => {
          
           
        })
         onWillUnmount(() => {
  
        });

        onWillUpdateProps((nextProps)=>{
           
        })

    }

    async form_hidden() {
    // Check if form is being edited (discard button visible)
    // if (!$('.cmms_quick_form .o_form_status_indicator_buttons').hasClass('invisible')) {
    //     this.notification.add("Please discard your changes on form.", {
    //         title: "Warning",
    //         type: "warning",
    //     });
    //     return;
    // }

    // Hide form
    this.state.showForm = false;
   $('.o_kanban_renderer').removeClass('my-hide');
    // if ($('.o_kanban_renderer').is(':visible')) {
    //     $('.o_kanban_renderer').show();
    // }

}


async composeFormProps_2(record) {
    const { active_id, active_ids, ...splitCtx } = this.controller.props.context;
    //for machine
    this.yy.formProps = {
        type: "form",
        display: {
            controlPanel: true, 

        },
      
        actionMenus: {},
        viewId: record.formViewId,
        loadActionMenus: false,     
        resModel: record.resModel,
        resId: record.resId,
        resIds: [record.resId],
        context: { ...splitCtx, splited_form: true, from_cmms_quick_form:true },
        className: "cmms_quick_form",
    };

    this.state.showForm =1;
   $('.o_kanban_renderer').addClass('my-hide');

}



  async composeFormProps(record) {
    const { active_id, active_ids, ...splitCtx } = this.controller.props.context;

    this.yy.formProps = {
        type: "form",
        display: {
            controlPanel: true,   // ✅ Ẩn toàn bộ thanh điều hướng
            searchPanel: false
             
           
        },
      
        actionMenus: {},
        loadActionMenus: false,     // ✅ Không load menu hành động
        searchViewId: false,
        resModel: record.resModel,
        resId: record.resId,
        resIds: [record.resId],
        context: { ...splitCtx, cmms_quick_form: true,from_cmms_quick_form:true },
        className: "cmms_quick_form",
    };

    this.state.showForm =1;
    $('.o_kanban_renderer').addClass('my-hide');

}



};
