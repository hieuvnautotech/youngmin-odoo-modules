from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.fields import Datetime


class MESQCFormHistory(models.Model):
    _name = "mes.qc_form.history"
    _order = "id DESC"

    name = fields.Char(string="Name")
    type_material = fields.Char(string="Type Material")

    stock_move_line_id = fields.Many2one("stock.move.line", string="stock_move_line_id")
    jig_id = fields.Many2one("product.product", string="Jig")
    category_id = fields.Many2one(related="product_id.categ_id", string="Category")
    stock_quant_id = fields.Many2one("stock.quant", string="Stock Quant")
    mrp_material_id = fields.Many2one("mrp.material", string="MRP Material")
    mrp_mo_material_id = fields.Many2one("mrp.mo.material", string="MRP Material")
    mrp_production_id = fields.Many2one("mrp.production", string="MRP Production")
    mrp_workorder_id = fields.Many2one("mrp.workorder", string="MRP Workorder")
    picking_wizard_id = fields.Many2one("picking.wizard.line", string="Picking Line")

    mes_qc_form_id = fields.Many2one("mes.qc_form", string="Form Title")

    item_group_re_use = fields.Selection(
        related="mes_qc_form_id.item_group", string="Item Group"
    )

    form_type = fields.Selection(
        [
            ("iqc", "IQC"),
            ("pqc", "PQC"),
            ("oqc", "OQC"),
            ("re_use", "Re-Use for Expired"),
            ("jig", "Jig"),
            ("item_qc", "Item QC"),
            ("pallet_qc", "Pallet QC"),
        ],
        string="Form Type",
    )
    status = fields.Selection(
        [("hide", "HIDE"), ("hold", "HOLDING"), ("release", "RELEASE")],
        string="Status",
        default="hide",
    )
    item_group = fields.Selection(
        [("material", "MATERIAL"), ("semi", "SEMI"), ("fg", "FG")],
        string="Item Group",
        default="material",
    )

    # po = fields.Many2one(string="Form Title")
    # receiving_order = fields.Many2one(string="Form Title")
    overall_result = fields.Char(string="Overall Result")
    # qc_staff = fields.Char(string="QC Staff")
    check_date = fields.Datetime(string="Check Date")
    unit = fields.Char(string="Unit")
    supplier = fields.Char(string="Supplier")
    material_code = fields.Char(string="Material Code")
    material_name = fields.Char(string="Material Name")
    lot_id = fields.Many2one("stock.lot", string="Lot ID")
    lot_ng_id = fields.Many2one(related="mrp_production_id.lot_ng_id", string="NG Lot")
    lot_ok_id = fields.Many2one(related="mrp_production_id.lot_ok_id", string="OK Lot")
    product_id = fields.Many2one(related="lot_id.product_id", string="Product")
    product_name = fields.Char(related="product_id.name", string="Product")
    uom_id = fields.Many2one(related="product_id.uom_id", string="UOM")
    qty_uom = fields.Char(string="Uom")
    staff_id = fields.Many2one("res.users", string="Staff")
    staff_name = fields.Char(string="Staff name")
    confirm_staff_id = fields.Many2one("res.users", string="Staff")
    confirm_staff_name = fields.Char(string="Staff name")
    qty = fields.Float(string="Qty", digits=(16, 2))

    question_ids = fields.One2many(
        "mes.qc_form.history.line", "history_id", string="Questions"
    )

    # ng_location = fields.Many2one('stock.location', string="From", domain=lambda self: [('location_id', '=', self.env.ref("autonsi_standard_youngmin.area_material").id)])
    # ok_location = fields.Many2one('stock.location', string="To", domain=lambda self: [('location_id', '=', self.env.ref("autonsi_standard_youngmin.area_material").id)])
    ng_location = fields.Many2one("stock.location", string="From")
    ok_location = fields.Many2one("stock.location", string="To")

    is_history = fields.Boolean(string="Is History")

    result = fields.Char(string="Result", compute="_compute_result", store=True)
    # =============
    process = fields.Char(string="Process")
    process_id = fields.Many2one("standard.process", string="Process")
    qty_sampling = fields.Float(string="Quantity Sampling", digits=(16, 2))
    defect_ratio = fields.Float(string="Defect Ratio", digits=(16, 2))
    ok_qty = fields.Float(string="Ok Quantity", digits=(16, 2))
    ng_qty = fields.Float(string="Ng Quantity", digits=(16, 2))

    type_roll = fields.Selection(
        [
            ("first", "Initial"),
            ("mid", "In-process"),
            ("final", "Final"),
        ],
        default="first",
        string="Type",
    )

    # ==========
    file_upload = fields.Binary(
        "File",
        attachment=True,
    )
    file_upload_name = fields.Char("File Name")

    # ==============
    # oqc related
    is_resistance = fields.Boolean()
    is_final_process = fields.Boolean()

    # iqc related
    po_name = fields.Char(related="stock_move_line_id.picking_id.origin")
    picking_id = fields.Many2one(related="stock_move_line_id.picking_id")
    # pqc related
    pmo_id = fields.Many2one(related="mrp_production_id.pmo_id")
    # pallet_qc related
    pallet_no = fields.Many2one(related="picking_wizard_id.pallet_no_id")
    project_code = fields.Many2one(related="product_id.project_id")

    remark = fields.Char(string="Remark")
    rev_no = fields.Char(string="Rev No")

    # ok_location_check_type = fields.Selection(
    #     selection=[
    #         ('m_stock', 'M Stock'),
    #         ('m_stock_2', 'M Stock 2'),
    #     ],
    #     compute='_compute_ok_location_check_type',
    #     store=False,
    # )
    #
    # ng_location_check_type = fields.Selection(
    #     selection=[
    #         ('m_ng', 'M NG'),
    #         ('m_ng_2', 'M NG 2'),
    #     ],
    #     compute='_compute_ng_location_check_type',
    #     store=False,
    # )
    #
    # @api.depends('ng_location', 'form_type')
    # def _compute_ok_location_check_type(self):
    #     for rec in self:
    #         rec.ok_location_check_type = (
    #             'm_stock' if rec.form_type == 'item_qc' and rec.ng_location.check_type == 'm_ng'
    #             else 'm_stock_2' if rec.form_type == 'item_qc' and rec.ng_location.check_type == 'm_ng_2'
    #             else False
    #         )
    #
    # @api.depends('ok_location', 'form_type')
    # def _compute_ng_location_check_type(self):
    #     for rec in self:
    #         rec.ng_location_check_type = (
    #             'm_ng' if rec.form_type == 'item_qc' and rec.ok_location.check_type == 'm_stock'
    #             else 'm_ng_2' if rec.form_type == 'item_qc' and rec.ok_location.check_type == 'm_stock_2'
    #             else False
    #         )

    @api.depends("overall_result")
    def _compute_result(self):
        for record in self:
            record.result = record.overall_result

    def open_form_create_log_hold(self):
        StockLocation = self.env["stock.location"]
        StockQuant = self.env["stock.quant"]
        for rec in self:
            if not rec.ng_location or not rec.ok_location:
                raise UserError(
                    _(
                        "You cannot create a release log when NG/OK location is already set."
                    )
                )
            if rec.mrp_material_id:
                if (
                    rec.mrp_material_id
                    and rec.mrp_material_id.remain_actual_qty
                    != rec.mrp_material_id.received_qty
                ):
                    raise UserError(_("This lot has already been used (quantity changed)."))
            else:
                if (
                    rec.mrp_mo_material_id
                    and rec.mrp_mo_material_id.remain_actual_qty
                    != rec.mrp_mo_material_id.received_qty
                ):
                    raise UserError(_("This lot has already been used (quantity changed)."))

            if rec.form_type == "iqc":
                quants = StockQuant.search(
                    [
                        ("lot_id", "=", rec.lot_id.id),
                        ("location_id.check_type", "in", ["m_stock", "m_stock_2", "m_input"]),
                        ("quantity", ">", 0),
                    ]
                )

                total_qty = sum(quants.mapped("quantity"))
            else:
                quants = StockQuant.search(
                    [
                        ("lot_id", "=", rec.lot_id.id),
                        ("location_id", "=", rec.ok_location.id),
                    ]
                )

                total_qty = sum(quants.mapped("quantity"))

            if total_qty < rec.qty:
                raise UserError(_("This lot has already been used (quantity changed)."))
        return {
            "name": "Hold",
            "type": "ir.actions.act_window",
            "res_model": "mes.qc_form.log",
            "view_mode": "form",
            "view_id": self.env.ref(
                "autonsi_qms_youngmin.view_mes_qc_form_log_form"
            ).id,
            "target": "new",
            "context": {"default_history_ids": self.ids},
        }

    def open_form_create_log_release(self):
        for rec in self:
            if not rec.ng_location or not rec.ok_location:
                raise UserError(
                    _(
                        "You cannot create a release log when NG/OK location is already set."
                    )
                )
            # if rec.mrp_material_id and rec.mrp_material_id.remain_actual_qty != rec.mrp_material_id.received_qty:
            #     raise UserError(_("This lot has already been used (quantity changed)."))
            stock = self.env["stock.quant"].search(
                [
                    ("location_id", "=", rec.ng_location.id),
                    ("lot_id", "=", rec.lot_id.id),
                ]
            )
            if stock.quantity < rec.qty:
                raise UserError(_("This lot has already been scrapped."))
        return {
            "name": "Release",
            "type": "ir.actions.act_window",
            "res_model": "mes.qc_form.log",
            "view_mode": "form",
            "view_id": self.env.ref(
                "autonsi_qms_youngmin.view_mes_qc_form_log_form"
            ).id,
            "target": "new",
            "context": {"default_history_ids": self.ids},
        }

    @api.model
    def create_history_iqc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        self.env["stock.move.line"].search(
            [("id", "=", inspectionData.get("stock_move_line_id"))]
        ).write(
            {
                "iqc_state": (
                    "ok" if inspectionData.get("final_result") == "OK" else "ng"
                ),
                "qc_date": Datetime.now(),
            }
        )

        self.env["mes.qc_form.history"].search(
            [("stock_move_line_id", "=", inspectionData.get("stock_move_line_id"))]
        ).unlink()

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "type_material": inspectionData.get("category_material"),
            "supplier": inspectionData.get("supplier"),
            "material_code": inspectionData.get("material_code"),
            "material_name": inspectionData.get("material_name"),
            "qty_uom": inspectionData.get("qty_uom"),
            "staff_id": inspectionData.get("staff_id"),
            "confirm_staff_id": inspectionData.get("confirm_staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "confirm_staff_name": inspectionData.get("confirm_staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "stock_move_line_id": inspectionData.get("stock_move_line_id"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
            "item_group": "material",
            "is_history": True,
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.stock_move_line_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                "X1": item.get("X1"),
                "X2": item.get("X2"),
                "X3": item.get("X3"),
                "X4": item.get("X4"),
                "X5": item.get("X5"),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_iqc_data(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        self.env["stock.move.line"].search(
            [("id", "=", inspectionData.get("stock_move_line_id"))]
        ).write(
            {
                "iqc_state": "in_progress",
                # 'qc_date': Datetime.now(),
            }
        )

        self.env["mes.qc_form.history"].search(
            [("stock_move_line_id", "=", inspectionData.get("stock_move_line_id"))]
        ).unlink()

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "type_material": inspectionData.get("category_material"),
            "supplier": inspectionData.get("supplier"),
            "material_code": inspectionData.get("material_code"),
            "material_name": inspectionData.get("material_name"),
            # 'lot': inspectionData.get('lot'),
            "qty_uom": inspectionData.get("qty_uom"),
            "staff_id": inspectionData.get("staff_id"),
            "confirm_staff_id": inspectionData.get("confirm_staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "confirm_staff_name": inspectionData.get("confirm_staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "stock_move_line_id": inspectionData.get("stock_move_line_id"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
            "item_group": "material",
            "is_history": False,
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.stock_move_line_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                "X1": item.get("X1"),
                "X2": item.get("X2"),
                "X3": item.get("X3"),
                "X4": item.get("X4"),
                "X5": item.get("X5"),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_jig_qc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        if inspectionData.get("jig_id"):
            self.env["product.product"].search(
                [("id", "=", inspectionData.get("jig_id"))]
            ).write(
                {
                    "jig_status_qc": (
                        "ok" if inspectionData.get("final_result") == "OK" else "ng"
                    ),
                }
            )

        if inspectionData.get("mrp_workorder_id"):
            mrp_workorder_id = self.env["mrp.workorder"].search(
                [("id", "=", inspectionData.get("mrp_workorder_id"))]
            )
            if mrp_workorder_id:
                mrp_workorder_id.write(
                    {
                        "jig_status": "done",
                        "jig_status_qc": (
                            "ok" if inspectionData.get("final_result") == "OK" else "ng"
                        ),
                    }
                )
                mrp_workorder_id.jig_code.jig_status_qc = (
                    "ok" if inspectionData.get("final_result") == "OK" else "ng"
                )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "jig_id": inspectionData.get("jig_id"),
            "mrp_workorder_id": inspectionData.get("mrp_workorder_id"),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        # if history.jig_id:
        #     self.env["jig.history"].create(
        #         {
        #             "jig_id": history.jig_id.id,
        #             "history_id": history.id,
        #         }
        #     )
        if history.mrp_workorder_id:
            self.env["jig.history"].create(
                {
                    "jig_id": history.mrp_workorder_id.jig_code.id,
                    "history_id": history.id,
                    "mo": mrp_workorder_id.mo_id.name,
                }
            )

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                # 'X1': item.get('X1'),
                # 'X2': item.get('X2'),
                # 'X3': item.get('X3'),
                # 'X4': item.get('X4'),
                # 'X5': item.get('X5'),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_re_use(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        quant = self.env["stock.quant"].search(
            [("id", "=", inspectionData.get("stock_quant_id"))]
        )
        quant.write(
            {
                "iqc_state": (
                    "ok" if inspectionData.get("final_result") == "OK" else "ng"
                ),
                "disposal_date": Datetime.now(),
                "disposal_state": "re_use",
            }
        )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "stock_quant_id": inspectionData.get("stock_quant_id"),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.stock_quant_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        history_stock_id = quant.action_disposal(history.mes_qc_form_id.item_group)
        history_stock_id.re_use_history = history

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                # 'X1': item.get('X1'),
                # 'X2': item.get('X2'),
                # 'X3': item.get('X3'),
                # 'X4': item.get('X4'),
                # 'X5': item.get('X5'),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_multi_re_use(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        quant_ids = self.env["stock.quant"].search(
            [("id", "in", inspectionData.get("stock_quant_ids"))]
        )

        for quant_id in quant_ids:
            quant_id.write(
                {
                    "iqc_state": (
                        "ok" if inspectionData.get("final_result") == "OK" else "ng"
                    ),
                    "disposal_date": Datetime.now(),
                    "disposal_state": "re_use",
                }
            )

            history_vals = {
                "name": inspectionData.get("title"),
                "mes_qc_form_id": inspectionData.get("form_id"),
                "stock_quant_id": quant_id.id,
                "staff_id": inspectionData.get("staff_id"),
                "check_date": Datetime.now(),
                "staff_name": inspectionData.get("staff_name"),
                "overall_result": inspectionData.get("final_result"),
                "qty": quant_id.available_quantity,
            }
            history = self.env["mes.qc_form.history"].create(history_vals)
            history.lot_id = history.stock_quant_id.lot_id
            history.form_type = history.mes_qc_form_id.form_type
            history.mes_qc_form_id.used = True

            history_stock_id = quant_id.action_disposal(
                history.mes_qc_form_id.item_group
            )
            history_stock_id.re_use_history = history

            for item in inspectionData.get("check_list", []):
                line_vals = {
                    "history_id": history.id,
                    "mes_qc_form_question_id": item.get("id"),
                    # 'X1': item.get('X1'),
                    # 'X2': item.get('X2'),
                    # 'X3': item.get('X3'),
                    # 'X4': item.get('X4'),
                    # 'X5': item.get('X5'),
                    "result": item.get("result"),
                    "remark": item.get("remark"),
                }
                self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_item_qc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        mrp_material_id = self.env["mrp.material"].search(
            [("id", "=", inspectionData.get("mrp_material_id"))]
        )
        mrp_material_id.write(
            {
                "qc_status": (
                    "done" if inspectionData.get("final_result") == "OK" else "not_yet"
                ),
                # "qc_status": "done",
                "is_ng": (
                    False if inspectionData.get("final_result") == "OK" else True
                ),
            }
        )
        if inspectionData.get("final_result") == "OK":
            mrp_material_id.action_reserved_material_qty(
                mrp_material_id.received_qty, 0.0
            )
        else:
            mrp_material_id.action_reserved_material_qty(
                0.0, mrp_material_id.received_qty
            )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "mrp_material_id": inspectionData.get("mrp_material_id"),
            "material_code": inspectionData.get("material_code"),
            "material_name": inspectionData.get("material_name"),
            "qty_uom": inspectionData.get("qty_uom"),
            "type_material": inspectionData.get("category_material"),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.mrp_material_id.quant_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True
        if inspectionData.get("final_result") == "NG":
            history.ng_location = self.env.ref(
                "autonsi_standard_youngmin.location_ng_stock_1"
            )
        else:
            history.ok_location = self.env.ref(
                "autonsi_standard_youngmin.location_wip_fabric_cutting_stock_1"
            )
        history.status = (
            "release" if inspectionData.get("final_result") == "OK" else "hold"
        )

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                # 'X1': item.get('X1'),
                # 'X2': item.get('X2'),
                # 'X3': item.get('X3'),
                # 'X4': item.get('X4'),
                # 'X5': item.get('X5'),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_pallet_qc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        picking_wizard_id = self.env["picking.wizard.line"].search(
            [("id", "=", inspectionData.get("picking_wizard_id"))]
        )
        picking_wizard_id.write(
            {
                "qc_state": (
                    "ok" if inspectionData.get("final_result") == "OK" else "ng"
                ),
                "qc_date": Datetime.now(),
            }
        )

        for line in picking_wizard_id.move_id:
            line.write(
                {
                    "iqc_state": (
                        "ok" if inspectionData.get("final_result") == "OK" else "ng"
                    ),
                    "qc_date": Datetime.now(),
                }
            )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "picking_wizard_id": inspectionData.get("picking_wizard_id"),
            "qty_uom": inspectionData.get("qty_uom"),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.mrp_material_id.quant_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_item_qc_mo(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        if not inspectionData.get("final_result"):
            raise UserError("No Final Result Data")

        mrp_mo_material_id = self.env["mrp.mo.material"].search(
            [("id", "=", inspectionData.get("mrp_mo_material_id"))]
        )
        mrp_mo_material_id.write(
            {
                "qc_status": (
                    "done" if inspectionData.get("final_result") == "OK" else "not_yet"
                ),
                # "qc_status": "done",
                "is_ng": (
                    False if inspectionData.get("final_result") == "OK" else True
                ),
            }
        )
        if inspectionData.get("final_result") == "OK":
            mrp_mo_material_id.action_reserved_material_qty(
                mrp_mo_material_id.received_qty, 0.0
            )
        else:
            mrp_mo_material_id.action_reserved_material_qty(
                0.0, mrp_mo_material_id.received_qty
            )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "mrp_mo_material_id": inspectionData.get("mrp_mo_material_id"),
            "material_code": inspectionData.get("material_code"),
            "material_name": inspectionData.get("material_name"),
            "qty_uom": inspectionData.get("qty_uom"),
            "type_material": inspectionData.get("category_material"),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.mrp_mo_material_id.quant_id.lot_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        if inspectionData.get("final_result") == "NG":
            if mrp_mo_material_id.mo_id.factory== "fac1":
                history.ng_location = self.env.ref(
                    "autonsi_standard_youngmin.location_ng_stock_1"
                )
            else:
                history.ng_location = self.env.ref(
                    "autonsi_standard_youngmin.location_ng_stock_2"
                )
        else:
            history.ok_location = mrp_mo_material_id.material_workorder_id.line_location_id

        history.status = (
            "release" if inspectionData.get("final_result") == "OK" else "hold"
        )

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                # 'X1': item.get('X1'),
                # 'X2': item.get('X2'),
                # 'X3': item.get('X3'),
                # 'X4': item.get('X4'),
                # 'X5': item.get('X5'),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_pqc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")
        # if not inspectionData.get('ng_qty'):
        #     raise UserError("No NG Quantity Data")

        mrp_production_id = self.env["mrp.production"].search(
            [("id", "=", inspectionData.get("mrp_production_id"))]
        )
        mrp_production_id.write(
            {
                "ok_qty": round(float(inspectionData.get("ok_qty", 0)), 2),
                "ng_qty": round(float(inspectionData.get("ng_qty", 0)), 2),
                "pqc_date": Datetime.now(),
            }
        )

        mrp_production_id.action_reserved_semi_product_qty(
            inspectionData.get("ok_qty"), inspectionData.get("ng_qty")
        )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "mrp_production_id": inspectionData.get("mrp_production_id"),
            "process": inspectionData.get("process"),
            "process_id": inspectionData.get("process_id"),
            "qty_sampling": inspectionData.get("qty_sampling"),
            "defect_ratio": inspectionData.get("defect_ratio"),
            "ok_qty": round(float(inspectionData.get("ok_qty", 0)), 2),
            "ng_qty": round(float(inspectionData.get("ng_qty", 0)), 2),
            "type_roll": inspectionData.get("type_roll"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "overall_result": inspectionData.get("final_result"),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.mrp_production_id.lot_producing_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                "HD1": item.get("HD1"),
                "HD2": item.get("HD2"),
                "HD3": item.get("HD3"),
                "HD4": item.get("HD4"),
                "HD5": item.get("HD5"),
                "HD6": item.get("HD6"),
                "HD7": item.get("HD7"),
                "HD8": item.get("HD8"),
                "HD9": item.get("HD9"),
                "HD10": item.get("HD10"),
                "HD11": item.get("HD11"),
                "HD12": item.get("HD12"),
                "HD13": item.get("HD13"),
                "HD14": item.get("HD14"),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    @api.model
    def create_history_oqc(self, inspectionData=None):
        if not inspectionData:
            raise ValueError("No inspectionData received")

        mrp_production_id = self.env["mrp.production"].search(
            [("id", "=", inspectionData.get("mrp_production_id"))]
        )
        mrp_production_id.action_callback_oqc()
        mrp_production_id.write(
            {
                "ok_qty": round(float(inspectionData.get("ok_qty", 0)), 2),
                "ng_qty": round(float(inspectionData.get("ng_qty", 0)), 2),
                "pqc_date": Datetime.now(),
            }
        )
        mrp_production_id.action_reserved_semi_product_qty(
            inspectionData.get("ok_qty"), inspectionData.get("ng_qty")
        )

        history_vals = {
            "name": inspectionData.get("title"),
            "mes_qc_form_id": inspectionData.get("form_id"),
            "mrp_production_id": inspectionData.get("mrp_production_id"),
            "is_resistance": inspectionData.get("is_resistance"),
            "is_final_process": inspectionData.get("is_final_process"),
            "qty_sampling": inspectionData.get("qty_sampling"),
            "defect_ratio": inspectionData.get("defect_ratio"),
            "ok_qty": round(float(inspectionData.get("ok_qty", 0)), 2),
            "ng_qty": round(float(inspectionData.get("ng_qty", 0)), 2),
            "type_roll": inspectionData.get("type_roll"),
            "qty": round(float(inspectionData.get("qty", 0)), 2),
            "staff_id": inspectionData.get("staff_id"),
            "check_date": Datetime.now(),
            "staff_name": inspectionData.get("staff_name"),
            "remark": inspectionData.get("remark"),
            "rev_no": inspectionData.get("rev_no"),
        }
        history = self.env["mes.qc_form.history"].create(history_vals)
        history.lot_id = history.mrp_production_id.lot_producing_id
        history.form_type = history.mes_qc_form_id.form_type
        history.mes_qc_form_id.used = True

        for item in inspectionData.get("check_list", []):
            line_vals = {
                "history_id": history.id,
                "mes_qc_form_question_id": item.get("id"),
                "result": item.get("result"),
                "remark": item.get("remark"),
            }
            self.env["mes.qc_form.history.line"].create(line_vals)

        return history

    def action_open_iqc_form_history(self):
        for record in self:

            context_data = {
                "title": record.mes_qc_form_id.name,
                "category_material": record.stock_move_line_id.product_id.categ_id.name,
                "supplier": record.stock_move_line_id.picking_id.partner_id.name,
                "material_code": record.stock_move_line_id.product_id.code,
                "material_name": record.stock_move_line_id.product_name,
                "lot": record.stock_move_line_id.lot_id.name,
                "qty_uom": record.stock_move_line_id.product_id.uom_id.name,
                "isHistory": record.is_history,
                "isPreview": False,
                "qty": record.qty,
                "employee_list": record.mes_qc_form_id.get_employee_list(),
                "self_id": record.mes_qc_form_id.get_self_id(),
                "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                "staff_id": record.staff_id.id,
                "staff_name": record.staff_id.name,
                "confirm_staff_id": record.confirm_staff_id.id,
                "confirm_staff_name": record.confirm_staff_id.name,
                "check_date": record.check_date,
                "final_result": record.overall_result,
                "columns": record.mes_qc_form_id.get_iqc_column_config(),
                "check_list": record.prepare_check_list_data_history(),
                "form_id": record.mes_qc_form_id.id,
                "stock_move_line_id": record.stock_move_line_id.id,
            }

            tag = "qms_question_iqc_action"
            name = _(f"QMS IQC - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_re_use_form_history(self):
        for record in self:

            context_data = {
                "title": record.mes_qc_form_id.name,
                "item_group": record.mes_qc_form_id.item_group,
                "remaining_days": record.stock_quant_id.remaining_days,
                "life_days": record.stock_quant_id.material_life,
                "category_material": record.stock_quant_id.product_id.categ_id.name,
                "supplier": record.stock_quant_id.partner_id.name,
                "material_code": record.product_id.code,
                "material_name": record.product_name,
                "lot": record.lot_id.name,
                "qty_uom": record.stock_quant_id.product_id.uom_id.name,
                "isHistory": True,
                "isPreview": False,
                "employee_list": record.mes_qc_form_id.get_employee_list(),
                "self_id": record.mes_qc_form_id.get_self_id(),
                "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                "staff_id": record.staff_id.id,
                "staff_name": record.staff_name,
                "check_date": record.check_date,
                "final_result": record.overall_result,
                "columns": record.mes_qc_form_id.get_pqc_column_config(),
                "check_list": record.prepare_check_list_data_history(),
                "form_id": record.mes_qc_form_id.id,
                "stock_quant_id": record.stock_quant_id.id,
                "qty": record.qty,
            }

            tag = "qms_question_re_use_action"
            name = _(f"QMS RE-USE - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_item_qc_form_history(self):
        for record in self:

            if record.mrp_material_id:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "category_material": record.mrp_material_id.material_id.categ_id.name,
                    # 'supplier': record.stock_quant_id.partner_id.name,
                    "material_code": record.mrp_material_id.material_id.code,
                    "material_name": record.mrp_material_id.material_id.name,
                    "spec": record.mrp_material_id.material_id.spec,
                    "lot": record.mrp_material_id.lot_id.name,
                    "qty_uom": record.mrp_material_id.product_uom_id.name,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "mrp_material_id": record.mrp_material_id.id,
                    "qty": record.qty,
                }
            else:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "category_material": record.mrp_mo_material_id.material_id.categ_id.name,
                    # 'supplier': record.stock_quant_id.partner_id.name,
                    "material_code": record.mrp_mo_material_id.material_id.code,
                    "material_name": record.mrp_mo_material_id.material_id.name,
                    "spec": record.mrp_mo_material_id.material_id.spec,
                    "lot": record.mrp_mo_material_id.lot_id.name,
                    "qty_uom": record.mrp_mo_material_id.product_uom_id.name,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "mrp_mo_material_id": record.mrp_mo_material_id.id,
                    "qty": record.qty,
                }

            tag = "qms_question_item_qc_action"
            name = _(f"QMS Item QC - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_pallet_qc_form_history(self):
        for record in self:

            context_data = {
                "title": record.mes_qc_form_id.name,
                "pallet_no": record.picking_wizard_id.pallet_no_id.name,
                "project_code": record.picking_wizard_id.product_id.project_id.name,
                "material_code": record.picking_wizard_id.product_id.code,
                "material_name": record.picking_wizard_id.product_id.name,
                "lot": record.picking_wizard_id.total_lot_qty,
                "qty_uom": record.picking_wizard_id.product_id.uom_id.name,
                "isHistory": True,
                "isPreview": False,
                "employee_list": record.mes_qc_form_id.get_employee_list(),
                "self_id": record.mes_qc_form_id.get_self_id(),
                "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                "staff_id": record.staff_id.id,
                "staff_name": record.staff_name,
                "check_date": record.check_date,
                "final_result": record.overall_result,
                "columns": record.mes_qc_form_id.get_pqc_column_config(),
                "check_list": record.prepare_check_list_data_history(),
                "form_id": record.mes_qc_form_id.id,
                "picking_wizard_id": record.picking_wizard_id.id,
                "qty": record.picking_wizard_id.total_qty,
            }

            tag = "qms_question_pallet_qc_action"
            name = _(f"QMS Pallet QC - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_pqc_form_history(self):
        for record in self:
            if record.mrp_production_id:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "category_material": record.mrp_production_id.semi_product_id.categ_id.name,
                    # 'supplier': record.stock_quant_id.partner_id.name,
                    "material_code": record.mrp_production_id.semi_product_id.code,
                    "material_name": record.mrp_production_id.semi_product_id.name,
                    "line_no": record.mrp_production_id.workorder_ids[:1].name or "",
                    "lot": record.mrp_production_id.lot_producing_id.name,
                    "qty_uom": record.mrp_production_id.semi_product_id.uom_id.name,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "mrp_production_id": record.mrp_production_id.id,
                    "qty": record.qty,
                    "process": record.process,
                    "process_id": record.process_id,
                    "qty_sampling": record.qty_sampling,
                    "defect_ratio": record.defect_ratio,
                    "ok_qty": record.ok_qty,
                    "ng_qty": record.ng_qty,
                    "type_roll": record.type_roll,
                }
            else:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "category_material": record.mrp_mo_production_id.semi_product_id.categ_id.name,
                    # 'supplier': record.stock_quant_id.partner_id.name,
                    "material_code": record.mrp_mo_production_id.semi_product_id.code,
                    "material_name": record.mrp_mo_production_id.semi_product_id.name,
                    "line_no": record.mrp_mo_production_id.workorder_ids[:1].name or "",
                    "lot": record.mrp_mo_production_id.lot_producing_id.name,
                    "qty_uom": record.mrp_mo_production_id.semi_product_id.uom_id.name,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "mrp_mo_production_id": record.mrp_mo_production_id.id,
                    "qty": record.qty,
                    "process": record.process,
                    "process_id": record.process_id,
                    "qty_sampling": record.qty_sampling,
                    "defect_ratio": record.defect_ratio,
                    "ok_qty": record.ok_qty,
                    "ng_qty": record.ng_qty,
                    "type_roll": record.type_roll,
                }

            tag = "qms_question_pqc_action"
            name = _(f"QMS Pqc - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_oqc_form_history(self):
        for record in self:
            context_data = {
                "title": record.mes_qc_form_id.name,
                "material_code": record.mrp_production_id.product_id.code,
                "material_name": record.mrp_production_id.product_id.name,
                "line_no": record.mrp_production_id.workorder_ids[:1].name or "",
                "lot": record.mrp_production_id.lot_producing_id.name,
                "isHistory": True,
                "isPreview": False,
                "employee_list": record.mes_qc_form_id.get_employee_list(),
                "self_id": record.mes_qc_form_id.get_self_id(),
                "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                "staff_id": record.staff_id.id,
                "staff_name": record.staff_name,
                "check_date": record.check_date,
                "columns": record.mes_qc_form_id.get_pqc_column_config(),
                "check_list": record.prepare_check_list_data_history(),
                "form_id": record.mes_qc_form_id.id,
                "mrp_production_id": record.mrp_production_id.id,
                "type_roll": record.type_roll,
                "qty": record.qty,
                "is_resistance": record.is_resistance,
                "is_final_process": record.is_final_process,
                "ok_qty": record.ok_qty,
                "ng_qty": record.ng_qty,
                "qty_sampling": record.qty_sampling,
                "defect_ratio": record.defect_ratio,
                "remark": record.remark,
                "rev_no": record.rev_no,
            }

            tag = "qms_question_oqc_action"
            name = _(f"QMS OQC - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def action_open_jig_form_history(self):
        for record in self:
            if record.mrp_workorder_id:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "product_code": record.mrp_workorder_id.jig_code.jig_product_id.code,
                    "supplier": record.mrp_workorder_id.jig_code.equip_partner_id.name,
                    "jig_code": record.mrp_workorder_id.jig_code.asset_code,
                    "jig_name": record.mrp_workorder_id.jig_code.name,
                    "process": record.mrp_workorder_id.jig_code.process_id.name,
                    "rev": record.mrp_workorder_id.jig_code.rev,
                    "remark": record.mrp_workorder_id.jig_code.remark,
                    "create_date": record.mrp_workorder_id.jig_code.create_date,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "mrp_workorder_id": record.mrp_workorder_id.id,
                }
            else:
                context_data = {
                    "title": record.mes_qc_form_id.name,
                    "product_code": record.jig_id.jig_product_id.code,
                    "supplier": record.jig_id.equip_partner_id.name,
                    "jig_code": record.jig_id.asset_code,
                    "jig_name": record.jig_id.name,
                    "process": record.jig_id.process_id.name,
                    "rev": record.jig_id.rev,
                    "remark": record.jig_id.remark,
                    "create_date": record.jig_id.create_date,
                    "isHistory": True,
                    "isPreview": False,
                    "employee_list": record.mes_qc_form_id.get_employee_list(),
                    "self_id": record.mes_qc_form_id.get_self_id(),
                    "doc_list": record.mes_qc_form_id.get_doc_ids_list(),
                    "staff_id": record.staff_id.id,
                    "staff_name": record.staff_name,
                    "check_date": record.check_date,
                    "final_result": record.overall_result,
                    "columns": record.mes_qc_form_id.get_pqc_column_config(),
                    "check_list": record.prepare_check_list_data_history(),
                    "form_id": record.mes_qc_form_id.id,
                    "jig_id": record.jig_id.id,
                }

            tag = "qms_question_jig_action"
            name = _(f"QMS JIG - {record.mes_qc_form_id.name}")
            return {
                "type": "ir.actions.client",
                "tag": tag,
                "name": name,
                "context": context_data,
                "target": "new",
            }

    def prepare_check_list_data_history(self):
        check_list = []

        for question in self.question_ids:
            base_data = {
                "id": question.mes_qc_form_question_id.id,
                "qc_type": question.mes_qc_form_question_id.mes_qc_type_id.name
                or "Visual",
                "qc_process": question.mes_qc_form_question_id.mes_qc_item_id.display_name
                or "",
                "qc_code": question.mes_qc_form_question_id.mes_qc_standard_id.name
                or "",
                "method": question.mes_qc_form_question_id.mes_qc_tool_id.display_name
                or "By Eyes",
                "frequency": question.mes_qc_form_question_id.mes_qc_frequency_id.name
                or "",
                "standard": question.mes_qc_form_question_id.mes_qc_standard_sees_id.name
                or "",
                "result": question.result,
                "remark": question.remark,
                "input_type": question.mes_qc_form_question_id.mes_qc_tool_id.input_type
                or "ok_ng",
                "X1": question.X1,
                "X2": question.X2,
                "X3": question.X3,
                "X4": question.X4,
                "X5": question.X5,
                "HD1": question.HD1,
                "HD2": question.HD2,
                "HD3": question.HD3,
                "HD4": question.HD4,
                "HD5": question.HD5,
                "HD6": question.HD6,
                "HD7": question.HD7,
                "HD8": question.HD8,
                "HD9": question.HD9,
                "HD10": question.HD10,
                "HD11": question.HD11,
                "HD12": question.HD12,
                "HD13": question.HD13,
                "HD14": question.HD14,
                # Metadata
                "mes_qc_type_id": question.mes_qc_form_question_id.mes_qc_type_id.id
                or False,
                "mes_qc_item_id": question.mes_qc_form_question_id.mes_qc_item_id.id
                or False,
                "mes_qc_form_question_id": question.mes_qc_form_question_id.id or False,
                "mes_qc_tool_id": question.mes_qc_form_question_id.mes_qc_tool_id.id
                or False,
                "mes_qc_standard_sees_id": question.mes_qc_form_question_id.mes_qc_standard_sees_id.id
                or False,
                "mes_qc_frequency_id": question.mes_qc_form_question_id.mes_qc_frequency_id.id
                or False,
            }

            check_list.append(base_data)

        return check_list

    def create_picking_shipping(self, vals):
        """
        Shipping Lot Location

        :param vals:
          {
              "origin": str ,
              "lot_id": recordset ,
              "from_location": recordset ,
              "to_location": recordset ,
              "quantity": float,
              "message": str
          }`
        """
        # --- Validation ---
        required_fields = ["lot_id", "from_location", "to_location", "quantity"]
        for field in required_fields:
            if not vals.get(field):
                raise ValidationError(_(f"Missing required field: {field}!"))

        # --- Extract values ---
        lot_id = vals["lot_id"]
        from_location = vals["from_location"]
        to_location = vals["to_location"]
        quantity = vals["quantity"]
        origin = vals.get("origin", "")
        message = vals.get("message", "")

        picking = self.env["stock.picking"].create(
            {
                "origin": origin,
                "note": message,
                "location_id": from_location.id,
                "location_dest_id": to_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            }
        )

        move_val = {
            "name": message,
            "product_id": lot_id.product_id.id,
            "product_uom": lot_id.product_id.uom_id.id,
            "product_uom_qty": quantity,
            "state": "confirmed",
            "location_id": from_location.id,
            "location_dest_id": to_location.id,
            "is_inventory": True,
            "picked": True,
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": lot_id.product_id.id,
                        "product_uom_id": lot_id.product_id.uom_id.id,
                        "quantity": quantity,
                        "location_id": from_location.id,
                        "location_dest_id": to_location.id,
                        "lot_id": lot_id.id,
                    },
                )
            ],
        }
        move = self.env["stock.move"].create(move_val)

        move.picking_id = picking.id
        return picking


class MESQCFormHistoryLine(models.Model):
    _name = "mes.qc_form.history.line"
    # _order = "id DESC"

    history_id = fields.Many2one("mes.qc_form.history", string="History")
    mes_qc_form_question_id = fields.Many2one("mes.qc_form_question", string="Question")

    X1 = fields.Char(string="X1")
    X2 = fields.Char(string="X2")
    X3 = fields.Char(string="X3")
    X4 = fields.Char(string="X4")
    X5 = fields.Char(string="X5")

    HD1 = fields.Char(string="HD1")
    HD2 = fields.Char(string="HD2")
    HD3 = fields.Char(string="HD3")
    HD4 = fields.Char(string="HD4")
    HD5 = fields.Char(string="HD5")
    HD6 = fields.Char(string="HD6")
    HD7 = fields.Char(string="HD7")
    HD8 = fields.Char(string="HD8")
    HD9 = fields.Char(string="HD9")
    HD10 = fields.Char(string="HD10")
    HD11 = fields.Char(string="HD11")
    HD12 = fields.Char(string="HD12")
    HD13 = fields.Char(string="HD13")
    HD14 = fields.Char(string="HD14")

    result = fields.Char(string="Result")
    remark = fields.Char(string="Remark")
