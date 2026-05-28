/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { CMMSJsTreeContainer } from "../cmms_jstree_container/cmms_jstree_container";
import { CMMSFormviewContainer } from "../cmms_formview_container/cmms_formview_container";

import { loadCSS, loadJS } from "@web/core/assets";
import { useBus, useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useState } = owl;

async function loadAssets({ jsLibs = [], cssLibs = [], images = [] }) {
    await Promise.all([
        // Load CSS
        ...cssLibs.map((href) => {
            if (document.querySelector(`link[href="${href}"]`)) return Promise.resolve();
            return new Promise((resolve, reject) => {
                const link = document.createElement("link");
                link.rel = "stylesheet";
                link.href = href;
                link.onload = resolve;
                link.onerror = reject;
                document.head.appendChild(link);
            });
        }),

        // Load JS
        ...jsLibs.map((src) => {
            if (document.querySelector(`script[src="${src}"]`)) return Promise.resolve();
            return new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }),

        // Preload Images
        ...images.map((src) => {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = resolve;
                img.onerror = reject;
                img.src = src;
            });
        }),
    ]);
}


export class CMMSNavigation extends Component {
    static template = "cmms.CMMSNavigation";
    static components = { CMMSJsTreeContainer, CMMSFormviewContainer };
    static props = {
        kanbanList: { type: Object },
        canCreate: { type: Boolean },
        canDelete: { type: Boolean },
        controller :{ type: Object },
    };
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.orm = useService("orm");
        this.kanbanOrder = "views_number_internal"; // this is default order
        this.asc = true;
        this.jsTreeDomain = [];
        this.jsTreeDomains = {};
        this.state = useState({ sortings: [] });

        onWillStart(async () => {
            await loadAssets({
                    jsLibs:[
                        '/cmms_plus/static/src/lib/jquery.fancytree-all-deps.min.js'
                    ],
                    cssLibs:[
                        '/cmms_plus/static/src/lib/skin-lion/ui.fancytree.min.css',
                         'https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/css/materialdesignicons.min.css'
                        
                    ],
                    images: [
                                '/cmms_plus/static/src/lib/skin-lion/icons.gif',
                                    '/cmms_plus/static/src/lib/skin-lion/loading.gif',
                                        '/cmms_plus/static/src/lib/skin-lion/vline.gif'
                            ],
                })
            });
    }

    /*
    * The method to get available sorting criteria and the default sorting
    */
    // async _onSortingLoad() {
    //     const sortingsDict = await this.orm.call(componentModel, "action_get_sorting_settings", {});
    //     this.kanbanOrder = sortingsDict.default_sorting;
    //     const selectedOptions = sortingsDict.sortings.filter((sortOption) => sortOption.key == this.kanbanOrder)
    //     this.asc = selectedOptions.length ? selectedOptions[0].asc : false;
    //     this.state.sortings = sortingsDict.sortings;
    // }
    /*
    * The method to prepare jstreecontainer props
    */
    getJsTreeProps(key) {
        return {
            jstreeTitle: key,
            jstreeId: key,
            kanbanModel: this.props.kanbanList.model,
            controller:this.props.controller,
            onUpdateSearch: this.onUpdateSearch.bind(this),
            canCreate: key != "types" ? this.props.canCreate : this.props.canDelete,
             navigator: this

        }
    }


    getFormViewProps() {
        return {
           
            kanbanModel: this.props.kanbanList.model,
            controller:this.props.controller,
            onUpdateSearch: this.onUpdateSearch.bind(this),
           // canCreate: key != "types" ? this.props.canCreate : this.props.canDelete,
            navigator: this

        }
    }
    
    /*
    * The method to prepare the domain by all JScontainers and notify searchmodel
    */
    onUpdateSearch(jstreeId, domain) {
        var jsTreeDomain = this._prepareJsTreeDomain(jstreeId, domain);
        if (this.jsTreeDomain != jsTreeDomain) {
            this.jsTreeDomain = jsTreeDomain;
         
            this.env.searchModel.toggleJSTreeDomain(this.jsTreeDomain, {name: this.kanbanOrder, asc: !this.asc});
        };
    }
    /*
    * The method to prepare domain based on all jstree components
    */
    _prepareJsTreeDomain(jstreeId, domain) {
        var jsTreeDomain = [];
        this.jsTreeDomains[jstreeId] = domain;
        Object.values(this.jsTreeDomains).forEach(function (val_domain) {
            jsTreeDomain = Domain.and([jsTreeDomain, val_domain])
        });
        return jsTreeDomain
    }
    /*
    * The method to select all records that satisfy search criteria
    * It requires orm.call since not all records are shown on the view
    */
    async _onSelectAll() {
        const kanbanModel = this.props.kanbanList.model;
        var fullDomain = this.env.searchModel._getDomain();
        if (fullDomain.length != 0) {
            const selectedRecords = kanbanModel.selectedRecords.map((rec) => rec.id);
            fullDomain = Domain.or([fullDomain, [["id", "in", selectedRecords]]]).toList();
        };
        kanbanModel.selectedRecords = await this.orm.searchRead(componentModel, fullDomain, ["name"]);
        await kanbanModel.root.load();
        kanbanModel.notify();
    }
    /*
    * The method to reseqeunce kanban list
    * We clear orderBy each time since the UI assumes sorting only by a single criteria
    */
    async _applySorting() {
        this.props.kanbanList.config.orderBy = [];
        this.props.kanbanList.config.orderBy.push({name: this.kanbanOrder, asc: this.asc});
        this.props.kanbanList.config.orderBy.push({name: "id"});
        this.env.searchModel.updateOrderBy({name: this.kanbanOrder, asc: !this.asc});
        await this.props.kanbanList.sortBy(this.kanbanOrder);
    }
    /*
    * The method to sort records by specific field (always in desc order)
    */
    async _onApplySorting(event) {
        this.kanbanOrder = event.currentTarget.value;
        const selectedOptions = this.state.sortings.filter((sortOption) => sortOption.key == this.kanbanOrder)
        this.asc = selectedOptions.length ? selectedOptions[0].asc : false;
        await this._applySorting();
    }
    /*
    * The method to sort records by previously chosen field in the reverse (to the previously adapted) order
    */
    async _onApplyReverseSorting() {
        this.asc = !this.asc;
        await this._applySorting();
    }
};
