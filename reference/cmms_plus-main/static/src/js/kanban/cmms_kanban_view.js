/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { CMMSKanbanController } from "./cmms_kanban_controller";
import { CMMSKanbanModel } from "./cmms_kanban_model";
import { CMMSKanbanRenderer } from "./cmms_kanban_renderer";

import { CMMSSearchModel } from "./cmms_search_model";

export const CMMSKanbanView = Object.assign({}, kanbanView, {
   SearchModel: CMMSSearchModel,
    Controller: CMMSKanbanController,
    Model: CMMSKanbanModel,
    Renderer: CMMSKanbanRenderer,
    searchMenuTypes: ["filter", "favorite"],
    display: {
            controlPanel: true,  
           
        },
});

registry.category("views").add("cmms_kanban", CMMSKanbanView);
