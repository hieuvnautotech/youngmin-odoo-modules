/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
const { Component, onWillStart, onMounted, onWillUnmount, useState } = owl;
import { useBus, useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.dialogService = useService("dialog");

        // ✅ Patch hook onMounted ở đây
        onMounted(() => {

            if (this.props.resModel == "product.product") {
                console.log("✅ ListController mounted:", this.props);
                $('.o_cp_switch_buttons').empty().append(`
                    <button class="btn btn-secondary o_switch_view o_kanban o_cmms_kanban" data-tooltip="Kanban" title=""><i class="oi oi-view-kanban"></i></button>
                    <button class="btn btn-secondary o_switch_view o_list o_cmms_list" data-tooltip="List Jig"><i class="oi mdi mdi-18px mdi-alpha-j-box"></i></button>                    
                    <button class="btn btn-secondary o_switch_view o_cmms_list_machine" data-tooltip="List Machine"><i class="oi mdi mdi-18px mdi-alpha-m-box"></i></button>
                                    `
                )

                $('.o_cmms_kanban').on('click', async () => {
                    
                       
                    // 🔹 Chạy song song cả 2 RPC call
                    const [view_kanban_id, view_form_id, search_view_id] = await Promise.all([
                        this.orm.call("product.product", "getKanbanViewId", [[]]),
                        this.orm.call("product.product", "getJigFormViewId", [[]]),
                        this.orm.call("product.product", "getSearchView", [[]]),
                        
                    ]);

                    // 🟢 Mở kanban
                    await this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: "product.product",
                        name: "Product Assets",
                        views: [

                            [view_kanban_id, "kanban"],
                            [false, "list"],
                            [view_form_id,'form']
                        ],
                        view_mode: "kanban,list",
                         search_view_id: [search_view_id], 
                      domain: ['|', ['is_jig', '=', true], ['is_machine', '=', true]],

                        target: "main",
                        context: {
                            cmms_quick_form:true
                        },
                    });

                    //    $('.o_switch_view').removeClass('active')
                    //  $('.o_cmms_kanban').addClass('active')


                     
                })


                $('.o_cmms_list').on('click', async () => {

                 

                          // 🔹 Chạy song song cả 2 RPC call
                    const [view_list_id, view_form_id, search_view_id] = await Promise.all([
                        this.orm.call("product.product", "getJigListViewId", [[]]),
                        this.orm.call("product.product", "getJigFormViewId", [[]]),
                        this.orm.call("product.product", "getSearchView", [[]]),
                        
                        
                    ]);


                      

                            // 🟢 Mở List
                            await this.actionService.doAction({
                                type: "ir.actions.act_window",
                                res_model: "product.product",
                                name: "Product Assets",
                                views: [

                                   
                                    [view_list_id, "list"],
                                     [false, "kanban"],
                                     [view_form_id,'form']
                                ],
                             
                                view_mode: "kanban,list",
                                domain: [["is_jig", "=", true]],
                                search_view_id:[search_view_id],
                                target: "main",
                                context: {
                                    cmms_quick_form:true
                                },
                            });


                            //    $('.o_switch_view').removeClass('active')
                            // $('.o_cmms_list').addClass('active')



                })

                 $('.o_cmms_list_machine').on('click',async ()=>{

                   


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
                                    // $('.o_cmms_list_machine').addClass('active')



                    })


            }

        });
    },


});
