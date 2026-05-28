/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SearchModel } from "@web/search/search_model";
import { Domain } from "@web/core/domain";

export class CMMSSearchModel extends SearchModel {
    /*
    * Overwrite to introduce jsTreeDomain
    */
    setup(services) {

        this.jsTreeDomain = [];

        //  this.kanbanOrder = {name: "name", asc: true}; // this is default order
        super.setup(...arguments);
    }
    // _getFacets() {
    //     // Add workorder filter facet to the search bar if applicable
    //     const facets = super._getFacets();

    //     console.log(facets,'..............')
        
          
    //             facets.push({
    //                 groupId: 0,
    //                 type: "filter",
    //                 domain:[['id','=', 9 ]],
                  
    //                 values: ["Wood"],
    //                 separator: "or",
    //                 icon: "fa fa-filter",
    //                 color: "info",
    //             });
            
        
    //     return facets;
    // }


    /*
    * Overwrite to add our jsTree
    * Regretfully, none of child method can be triggered, so we have to redefine the whole return
    */
    _getDomain(params = {}) {
        let domain = super._getDomain(...arguments);
        try {
            // Kết hợp domain với jsTreeDomain
            domain = Domain.and([domain, this.jsTreeDomain]);

            // Nếu jsTreeDomain có chứa 'is_machine', thay toàn bộ 'is_jig' -> 'is_machine'
            const jsTreeStr = JSON.stringify(this.jsTreeDomain);

            // if (this.jsTreeDomain.ast && this.jsTreeDomain.ast.value.length ==0) {
                
            //       console.losg(domain,'..........................')
            //       domain=this.jsTreeDomain;
                  
            // } 
            
            // else {
            //     if (jsTreeStr.includes("is_machine")) {
            //         const domainList = domain.toList(
            //             Object.assign({}, this.globalContext, this.userService.context)
            //         );

            //         // 🔁 Thay thế trong mảng domain thay vì chuỗi
            //         const replacedDomain = domainList.map((cond) => {
            //             if (Array.isArray(cond) && cond[0] === "is_jig") {
            //                 return ["is_machine", cond[1], cond[2]];
            //             }
            //             return cond;
            //         });

            //         // Tạo lại Domain object mới
            //         domain = new Domain(replacedDomain);
            //     }

            // }


            var domains = params.raw
                ? domain
                : domain.toList(Object.assign({}, this.globalContext, this.userService.context));

            if (jsTreeStr != "[]") {
                //user click filter
                localStorage.setItem("cmms_domain", JSON.stringify(domains))
            }


            return domains;

        } catch (error) {
            throw new Error(
                _t("Failed to evaluate the domain: %(domain)s.\n%(error)s", {
                    domain: domain.toString(),
                    error: error.message,
                })
            );
        }
    }
    /*
    * Overwrite to introduce our own kanban order
    */
    // _getOrderBy() {
    //     return [this.kanbanOrder, {"name": "id"}];
    // }
    /*
    * The method to save received jsTree domain
    */
    toggleJSTreeDomain(domain, kanbanOrder) {
        this.jsTreeDomain = domain;
        // this.kanbanOrder = kanbanOrder;
        this._notify();
    }
    /*
    * The method to save the current kanban order
    */
    // updateOrderBy(kanbanOrder) {
    //     this.kanbanOrder = kanbanOrder;
    // }
}
