/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { CMMSKanbanRecord } from "./cmms_kanban_record";
import { CMMSNavigation } from "../kanban/cmms_navigation/cmms_navigation";
import { useBus, useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted,onWillUnmount, useState } = owl;


export class CMMSKanbanRenderer extends KanbanRenderer {
    static template = "cmms.CMMSKanbanRenderer";



    static components = {
        ...KanbanRenderer.components,
        CMMSNavigation,
        KanbanRecord: CMMSKanbanRecord,
    };

     setup() {
        super.setup();
        this.ui= useService('ui');
        this.rpcService = useService("rpc");
        this.actionService = useService("action");
        this.orm = useService("orm");
        //const { actionId, actionType } = this.env.config || {};

    


        onMounted(() => {
            //khi vào menu hoặc chuyển view
           // const is_act_window =  !this.env.inDialog && actionType === "ir.actions.act_window";
            $('.o_last_breadcrumb_item').empty().append(`<h6>ASSETS</h6>`);
             $('.o_cp_switch_buttons').empty().append(`
                    <button class="btn btn-secondary o_switch_view o_kanban o_cmms_kanban" data-tooltip="Kanban" title=""><i class="oi oi-view-kanban"></i></button>
                    <button class="btn btn-secondary o_switch_view o_list o_cmms_list" data-tooltip="List Jig"><i class="oi mdi mdi-18px mdi-alpha-j-box"></i></button>                    
                    <button class="btn btn-secondary o_switch_view o_cmms_list_machine" data-tooltip="List Machine"><i class="oi mdi mdi-18px mdi-alpha-m-box"></i></button>
                                    `
                )

            $('.o_cmms_list_machine').on('click',()=>{
                this._showListMachine();
            })
             $('.o_cmms_list').on('click',()=>{
                this._showListJig();
            })

         


        });

        onWillUnmount(()=>{
           
        })


    }

    async _showListJig(){
   
       
                    const [view_list_id, view_form_id, search_view_id] = await Promise.all([
                        this.orm.call("product.product", "getJigListViewId", [[]]),
                        this.orm.call("product.product", "getJigFormViewId", [[]]),
                         this.orm.call("product.product", "getSearchView", [[]]),
                    ]);



                    // 🟢 Mở form view đã chỉ định
                    await this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: "product.product",
                        name: "Jig List",
                         views: [
                                  
                                    [view_list_id, "list"],
                                      [false, "kanban"], 
                                       [view_form_id, "form"], 
                                ],
                         view_mode: "list,kanban",
                         search_view_id:[search_view_id],
                        domain: [["is_jig", "=", true]],
                        target: "main",
                        context: {
                            cmms_quick_form:true
                        },
                    });


                    //   $('.o_switch_view').removeClass('active')
                    //  $('.o_cmms_list').addClass('active')


    
    }



   async _showListMachine(){
     
    // 🔹 Chạy song song cả 2 RPC call
                    const [view_list_id, view_form_id, search_view_id] = await Promise.all([
                        this.orm.call("product.product", "getMachineListViewId", [[]]),
                        this.orm.call("product.product", "getMachineFormViewId", [[]]),
                        this.orm.call("product.product", "getSearchView", [[]]),
                    ]);



                    // 🟢 Mở form view đã chỉ định
                    await this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: "product.product",
                        name: "Machine List",
                         views: [
                                  
                                    [view_list_id, "list"],
                                      [false, "kanban"], 
                                       [view_form_id, "form"], 
                                ],
                         view_mode: "list,kanban",
                        domain: [["is_machine", "=", true]],
                        search_view_id:[search_view_id],
                        target: "main",
                        context: {
                            
                        },
                    });

                    // $('.o_switch_view').removeClass('active')
                    //  $('.o_cmms_list_machine').addClass('active')

    
    }

    
     /*
    * The method to CMMSNavigation (left navigation)
    */
    getCMMSNavigationProps() {
        const cmmsActiveActions = this.props.archInfo.activeActions;
        return {
            kanbanList: this.props.list,
            canCreate: cmmsActiveActions.create,
            canDelete: cmmsActiveActions.delete,
            controller: this.ui.controller
        }
    }

    getCMMSFormProps() {

    }
   
};
