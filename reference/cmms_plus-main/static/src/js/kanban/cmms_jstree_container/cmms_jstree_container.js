/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { useBus,useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted,onWillUnmount, useState } = owl;


export class CMMSJsTreeContainer extends Component {
    static template = "cmms.CMMSJsTreeContainer";
    static props = {
        jstreeTitle: { type: String },
        jstreeId: { type: String },
        onUpdateSearch: { type: Function },
        kanbanModel: { type: Object },
        canCreate: { type: Boolean },
        controller: { type: Object },
        navigator : { type: Object }
        
    };
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
      
        this.state = useState({ treeData: 1 });
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.rpcService = useService("rpc");

        this.ui = useService("ui");
        


        this.controller = this.props.controller;
        this.navigator = this.props.navigator

        this.kanbanDomain= this.controller.model.config.domain 

         console.log(this.kanbanDomain.length, this.kanbanDomain,'mmmmmmmmm')
           if (this.kanbanDomain.length <=5 ) {
                //đặt tính treeview nếu có 1 domain thì ko  filter các nodes
                    var json = JSON.stringify(this.kanbanDomain)
                    if (json.indexOf("equip_category_id") >0 || json.indexOf("is_jig") >0 || json.indexOf("is_machine") >0) {
                        this.kanbanDomain=[]
                    }
                }

         
      

        this.ui.jtree = this

        if (this.kanbanDomain.length ==1 ) {
            var json = JSON.stringify(this.kanbanDomain)
            if (json.indexOf("equip_category_id") >0 || json.indexOf("is_jig") >0 || json.indexOf("is_machine") >0) {
                this.kanbanDomain=[]
            }
        }


        this.isNodeClick = false;

        onWillStart(async () => {
           
            // await this._loadTreeData(this.props);
        });
        onMounted(() => {
            // this.jsTreeAnchor = $("#"+this.id);
            // this.jsTreeSearchInput = $("#jstr_input_" + this.id)[0];
            this._renderJsTree();
        })
         onWillUnmount(() => {

            //Nếu khi click vao tree Node  mà không click vào item record thì khi thoát ta xóa luôn node_selected
            var is_from_record = localStorage.getItem('cmms_record_click')
            if (!is_from_record) {
                localStorage.removeItem("cmms_node_selected");
            }

            $(":ui-fancytree").fancytree("destroy");
        });

         // when the search panel changed
        this.controller.env.searchModel.addEventListener(
            "update",
            () => {

                this.controller.model.bus.addEventListener(
                    "update",
                    this.onKanbanSearchModelChanged.bind(this),
                    { once: true },
                );

            },
        );

    }

    /**
         * Check if a domain contains a condition for a given field.
         * Recursively inspect nested domains.
         */
        hasDomainField(domain, fieldName) {
            if (!Array.isArray(domain)) return false;

            for (const item of domain) {
                if (Array.isArray(item) && item[0] === fieldName) {
                    return true;
                } else if (Array.isArray(item)) {
                    const has = hasDomainField(item, fieldName);
                    if (has) return true;
                }
            }
            return false;
        }


     /** Called when the something changed in the kanban search model. **/
    async onKanbanSearchModelChanged(){
        await this.withNewState(async (newState) => {
        
        

            if ($('#cmms_close_form').is(':visible')) {
                   var formViewComponent = this.navigator.__owl__.children.__2.component
                   formViewComponent.form_hidden(0)
                   this.kanbanDomain= this.controller.model.config.domain 
                   this.isNodeClick = false; 
                   
                   this._reloadTree();
                   return;
                   
            } 

                        
        // const facets =  this.controller.env.searchModel.facets;
        // console.log(facets,'...........')
        // const journalFilterItem = this.getJournalFilter();
        // for (const facet of facets) {
        //     if (facet.groupId !== journalFilterItem.groupId) {
        //         return true;
        //     }
        // }

            
            // if (this.reload_tree) {
            //      this.kanbanDomain=[]
            //      const tree = $("#tree1").fancytree("getTree");
            //          tree.reload();
            //     this.reload_tree = false
            // }

             // Nếu click node → KHÔNG reload tree

                console.log(this.isNodeClick,'<<<<<<<<<<<<<<<<<<<<<<<<')
                if (this.isNodeClick) {
                    this.isNodeClick = false;  // reset flag
                    return;
                }
                

                  console.log(this.isNodeClick,'>>>>>>>>>>>>>>>>>>>>>>')
           
            this.kanbanDomain= this.controller.model.config.domain 

           
            if (this.kanbanDomain.length <=5 ) {
                //đặt tính treeview nếu có 1 domain thì ko  filter các nodes
                    var json = JSON.stringify(this.kanbanDomain)
                    if (json.indexOf("equip_category_id") >0 || json.indexOf("is_jig") >0 || json.indexOf("is_machine") >0) {
                        this.kanbanDomain=[]
                    }
                }

           const tree = $("#tree1").fancytree("getTree");
            tree.reload();
                 
        });
    }

    async withNewState(func){
        const newState = {...this.state};
        await func(newState);
        if (newState.__commitChanges) {
            newState.__commitChanges();
            delete newState.__commitChanges;
        }
        Object.assign(this.state, newState);
    }



    _renderJsTree() {
        this.node_selected = localStorage.getItem("cmms_node_selected");
        var self= this
        

        $("#tree1").fancytree({
            source: [
                {
                    title: "<b style='color:blueviolet;'>Assets<b>", key: "equipment", expanded: true, children: [
                        { title: "<b style='font-size:16px;'>Jig<b>", folder: true, key: "jig", lazy: true },
                        { title: "<b>Machine<b>", folder: true, key: "machine", lazy: true,pagenode:true},
                        // { title: "<b>Parts<b>", folder: true, key: "part", lazy: false },
                        // { title: "<b>Tools<b>", folder: false, key: "tool", lazy: false, },
                        // { title: "<b>ETC<b>", folder: false, key: "etc", lazy: false }
                    ]
                },
            ],
            icon: (event, data) => {
                var type = data.node.data.extrainfo;
                var key = data.node.key;

                if (key == "jig") {
                    return "mdi mdi-18px mdi-alpha-j-box";
                }
                else if (key == "part") {
                    return "mdi mdi-18px mdi-alpha-p-box ";
                }
                else if (type == 'partmodel' || type == 'partmodel2') {

                    return "mdi mdi-18px mdi-gamepad-circle";
                }
                else if (type == 'part') {

                    return "mdi mdi-18px mdi-puzzle";
                }
                else if (type == 'partitem') {

                    return "mdi mdi-18px mdi-puzzle";
                }
                else if (key == 'bom') {

                    return "mdi mdi-18px mdi-alpha-b-circle";
                } else if (type == 'bomitem') {

                    return "mdi mdi-18px mdi-controller-classic-outline";
                }
                else if (key == "tool") {
                    return "mdi mdi-18px mdi-alpha-t-circle ";
                } else if (type == 'tool') {

                    return "mdi mdi-18px mdi-merge";
                }
                else if (key == 'machine') {

                    return "mdi mdi-18px mdi-alpha-m-box-outline";
                }
                else if (type == 'jig') {
                    return "mdi mdi-18px mdi-chart-donut-variant";
                }

                else if (key == 'mold') {

                    return "mdi mdi-18px mdi-alpha-m-box";
                }


                else if (key == 'equipment') {

                    return "mdi mdi-18px mdi-star-david";
                }
                else if (key == 'machinetype') {

                    return "mdi mdi-18px mdi-pan";
                }
                else if (type == 'jigtype') {

                    return "mdi mdi-18px mdi-cog";
                }
                else if (type == 'bom') {

                    return "mdi mdi-18px mdi-steam";
                }
                else if (type == "jig_unit") {

                    return "mdi mdi-18px mdi-rhombus-medium";
                }
                else if (type == "machine_unit") {

                    return "mdi mdi-18px mdi-rhombus-medium";
                }
                else if (key == "etc") {
                    return "mdi mdi mdi-18px mdi-alpha-e-box"
                } else {
                    return ""
                }
            },
            init: (event, data) => {
                // Set key from first part of title (just for this demo output)
                data.tree.visit((n) => {

                    if (n.key == "jig" || n.key == "machine") { //|| n.key=="part" 
                        n.setExpanded();
                    }

                       if (self.node_selected ) {
                            if ( n.key ==self.node_selected) {
                                n.setActive(true);   // focus + select
                                n.makeVisible();     // tự động scroll đến node đó
                            } 
                            
                        }


                });
                
              
                this.node_selected = localStorage.getItem("cmms_node_selected");
                this.controller.callEvents('tree_init')

            },
         
            lazyLoad:async (event, data) => {
                var dfd = new $.Deferred();
                data.result = dfd.promise();
                var key = data.node.key;
                var type = data.node.data.extrainfo;

                data.node.data.nextpage=data.node.data.nextpage??1

                if (key === 'jig') {
                    try {

                            const res = await this.rpcService("/web/dataset/call_kw/product.product/get_category_equipment_types", {
                                model: "product.product",
                                method: "get_category_equipment_types",
                                args: [0],
                                kwargs: {},
                            });



                            const lst = res.flatMap((r, i) => {
                                let arr = [{
                                    lazy: r.has_products === true,
                                    title: `<span style="font-size:14px;color:blue;"><b>${r.name}</b></span>`,
                                    name:r.name,
                                    jtype_id: r.id,
                                    extrainfo: "jigtype",
                                    pagenode: data.node.data.nextpage < r.total_pages
                                  
                                }];


                                return arr;
                            });

                            dfd.resolve(lst);

                        } catch (error) {
                            console.log("Failed to fetch child nodes:", error);
                            dfd.reject("Loading error");
                        }


                }

                else if (key === 'machine') {
                        try {
                            
                            const dataRes = await this.rpcService("/web/dataset/call_kw/product.product/get_machine_units", {
                                model: "product.product",
                                method:"get_machine_units",
                                args: [0, this.kanbanDomain,data.node.data.nextpage],
                                kwargs: {},
                            });

                            const lst = dataRes.items.map((item, i) => ({
                                title: `<span style="font-size:13px;font-family: Basote;"><span style='color:#b50394;'>${(dataRes.next_page-1)*i + 1}.${item.code}${item.no_number} - ${item.name}</span></span>`,
                                extrainfo: "machine_unit",
                                lazy: false,
                                machine_id: item.id,
                                num: i,

                            }));

                            data.node.data.nextpage = dataRes.next_page
                            data.node.setTitle("<b>Machine</b> (total: " + dataRes.total_count + ")")

                           
                            dfd.resolve(lst);
                        } catch (error) {
                            console.log("Failed to fetch child nodes:", error);
                            dfd.reject("Loading error");
                        }
                }
              

                else if (type === 'jigtype' ) {

                        try {
                            const dataRes = await this.rpcService("/web/dataset/call_kw/product.product/get_jig_units", {
                                model: "product.product",
                                method:"get_jig_units",
                                args: [0, data.node.data.jtype_id, this.kanbanDomain, data.node.data.nextpage],
                                kwargs: {},
                            });
                          
                            const lst = dataRes.items.map((item, i) => ({
                                title: `<span style="font-size:13px;font-family: Basote;"><span style='color:#a12424;'>${item.code} - ${item.name}</span></span>`,
                                extrainfo: "jig_unit",
                                lazy: item.is_lazy,
                                jig_id: item.id,
                                num: i,
                            }));

                            data.node.data.nextpage = dataRes.next_page
                            dfd.resolve(lst);
                        } catch (error) {
                            console.log("Failed to fetch child nodes:", error);
                            dfd.reject("Loading error");
                        }
                }

            },
            loadChildren: (event, data) => {
                 if (data.node.data.pagenode ===true) {
                  
                    data.node.addPagingNode({
                        title: "<span style='color:brown;font-size:12px;'>More...</span>",
                         statusNodeType: "paging",
                        pagenode:true,
                        nextpage : data.node.data.nextpage,
                        jtype_id: data.node.data.jtype_id,
                       
                    });
                }  else {
                           data.node.visit(function (subNode) {
                        if (subNode.data.extrainfo == "machinetype")
                            subNode.setExpanded(true);

                        if (subNode.data.extrainfo == "jigtype")
                            subNode.setExpanded(true);

                        let jig_type=subNode.data.jtype_id;

                        if ( self.node_selected ) {
                            if ( jig_type == self.node_selected) {
                                subNode.setActive(true);   // focus + select
                                subNode.makeVisible();     // tự động scroll đến node đó
                            } 
                            
                        }

                    });
                
                }

                 
            },
            click: async (e, data) => {
              
               
                // Check if the click target is the expander icon
                if ($(e.originalEvent.target).hasClass("fancytree-expander")) {
                    console.log("Expander icon was clicked. Prevent further actions.");
                    // Prevent the node activation or other actions
                    return true; // Returning false prevents the default click action
                }

                 this.isNodeClick = true;

                var key = data.node.key;
                let type_node = data.node.data.extrainfo;
                

                if (key=="equipment")  {
                        

                         this.controller.env.searchModel.query=[]
                        this.controller.env.searchModel.createNewFilters([{
                            
                                description:"All Assets",
                                domain: [],
                                type: 'filter',
                        }])

                        
                       
                    // this._onUpdateDomainShowAll()
                }
                else if (key=="jig") {
                         var formViewComponent = this.navigator.__owl__.children.__2.component
                        formViewComponent.form_hidden(0)
                       
                        this.controller.env.searchModel.query=[]
                        this.controller.env.searchModel.createNewFilters([{
                            
                                description:"Jigs",
                                domain: [['is_jig', '=', true]],
                                type: 'filter',
                            }])


                       // this._onUpdateDomain(false, false)
                }
                else if (key =='machine') {
                     localStorage.setItem("cmms_node_selected",key);
                         var formViewComponent = this.navigator.__owl__.children.__2.component
                        formViewComponent.form_hidden(0)

                     

                        this.controller.env.searchModel.query=[]
                        this.controller.env.searchModel.createNewFilters([{
                            
                                description:"Machines",
                                domain: [['is_machine', '=', true]],
                                type: 'filter',
                            }])



                         // this._onUpdateDomain(false, true)
                }
                else if (type_node =='jig_unit') {
                                // const dataRes = await this.rpcService("/web/dataset/call_kw/product.product/get_jig_info", {
                                //     model: "product.product",
                                //     method:"get_jig_info",
                                //     args: [0, data.node.data.jig_id],
                                //     kwargs: {},
                                // });

                               var formViewComponent = this.navigator.__owl__.children.__2.component
                               formViewComponent.composeFormProps({
                                    resModel:'product.product',
                                    resId:data.node.data.jig_id,
                                    resIds :[data.node.data.jig_id],
                                   

                                });

                }
                else if (type_node=="jigtype"  ) {

                    
                    localStorage.setItem("cmms_node_selected",data.node.data.jtype_id);

                
                    // // this.controller.env.searchModel.deactivateGroup()
                    

                      this.controller.env.searchModel.query=[]

                      this.controller.env.searchModel.createNewFilters([{
                         
                            description:"Jig - "  + data.node.data.name,
                            domain: [['equip_category_id', '=', data.node.data.jtype_id]],
                            type: 'filter',
                        }])

                    

                   
                   
                        var formViewComponent = this.navigator.__owl__.children.__2.component
                        formViewComponent.form_hidden(0)


                    //this._onUpdateDomain(data.node.data.jtype_id, false)
                    // this.controller.callEvents({type:'jigtype', data:data.node.data.jtype_id})
                    

                }
                else if (type_node=="machine_unit") {
                        const view_form_id = await  this.orm.call("product.product", "getMachineFormViewId", [[]])
                        var formViewComponent = this.navigator.__owl__.children.__2.component
                        formViewComponent.composeFormProps_2({
                            resModel:'product.product',
                            resId:data.node.data.machine_id,
                            resIds :[data.node.data.machine_id],
                            formViewId: view_form_id
                        });

                }


                 this.isNodeClick = true;
               

            },
            clickPaging:async  (event, data)=> {
                
                var dfd = new $.Deferred();
                data.node.replaceWith( dfd.promise());

               

                if (data.node.data.jtype_id) {
                            //là jig
                            const dataRes = await this.rpcService("/web/dataset/call_kw/product.product/get_jig_units", {
                                model: "product.product",
                                method:"get_jig_units",
                                args: [0, data.node.data.jtype_id, this.kanbanDomain, data.node.data.nextpage],
                                kwargs: {},
                            });
                          
                            const lst = dataRes.items.map((item, i) => ({
                                title: `<span style="font-size:13px;"><span style='color:#a12424;'>${item.code} - ${item.name}</span></span>`,
                                extrainfo: "jig_unit",
                                lazy: item.is_lazy,
                                jig_id: item.id,
                                num: i,
                            }));

                            data.node.data.nextpage = dataRes.next_page
                            data.node.data.pagenode = dataRes.current_page == dataRes.total_pages? false:true

                            dfd.resolve(lst);
                            //sau khi thực hiện hàm loadChildren sẽ chạy lại vì thế cần check điều kiện data.node.data.pagenode xem có phân trang kế tiếp ko

               } else {
                //là machine
                        try {

                            var next_page=data.node.data.nextpage
                            
                            const dataRes = await this.rpcService("/web/dataset/call_kw/product.product/get_machine_units", {
                                model: "product.product",
                                method:"get_machine_units",
                                args: [0, this.kanbanDomain, next_page],
                                kwargs: {},
                            });

                            const dict_colors = {};

                            for (let page = 2; page <= 10; page++) {
                                    const hue = (page * 36) % 360;

                                    if (page <= 4) {
                                        // Đậm hơn cho page 2,3,4
                                        dict_colors[page] = `hsl(${hue}, 90%, 38%)`;
                                    } else {
                                        // Màu bình thường cho page 5–10
                                        dict_colors[page] = `hsl(${hue}, 80%, 45%)`;
                                    }
                                }


                            const color = dataRes.nextpage > 10 ? "#080808ff" : dict_colors[data.node.data.nextpage];
                            const page_size=6

                            const lst = dataRes.items.map((item, i) => ({
                                title: `<span style="font-size:13px;"><span style='color:${color};'>${(next_page-1)*page_size + (i+1) }.${item.code} - ${item.name}</span></span>`,
                                extrainfo: "machine_unit",
                                lazy: false,
                                machine_id: item.id,
                                num: i,
                            }));

                            data.node.data.nextpage = dataRes.next_page



                            dfd.resolve(lst);
                        } catch (error) {
                            console.log("Failed to fetch child nodes:", error);
                            dfd.reject("Loading error");
                        }
               }
            },

        });
        $(".fancytree-container").toggleClass("fancytree-connectors");

    }

    /*
    * The method to calculate domain based on checks and trigger the parent search model to reload
    * For 'attributes' we need the full node info since parents will be under check
    */
    _onUpdateDomain(item_id, is_machine) {
            var domain = [];

            if (is_machine) {
                 domain = Domain.and([domain, [['is_machine', "=", true]]]).toList();
            } else {
                    if (item_id)
                        domain = Domain.and([domain, [['equip_category_id', "=", parseInt(item_id)]]]).toList();
                    else
                        domain = Domain.and([domain, [['is_jig', "=", true]]]).toList();
            }

        this.props.onUpdateSearch(1, domain);
        $('#cmms_close_form').trigger('click') //close formview

    }

    _onUpdateDomainShowAll() {
        this.props.onUpdateSearch(1, []);
        $('#cmms_close_form').trigger('click') //close formview
    }


    _reloadTree() {
        const tree = $("#tree1").fancytree("getTree");
        tree.reload();
    }

};
