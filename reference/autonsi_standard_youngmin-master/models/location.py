from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class LocationStock(models.Model):
    _inherit = "stock.location"
    _order = "sequence desc"

    sequence = fields.Integer("Sequence")
    location_type = fields.Selection(
        [("area", "area"), ("location", "location"), ("bin", "bin")], string="Type"
    )
    description = fields.Char("Description")
    row = fields.Integer("Rows", default=0)
    column = fields.Integer("Columns", default=0)
    bin_ids = fields.One2many(
        "standard.binview",
        "location_id",
        string="Detail",
        ondelete="cascade",
        store=False,
    )
    check_type = fields.Selection(
        [
            # stock 1
            ("m_rec", "Material Receiving"),
            ("m_input", "Material Input"),
            ("m_stock", "Material Stock 1"),
            ("m_ng", "Material NG"),
            ("wip_input", "WIP Input"),
            ("wip_stock", "WIP Stock 1"),
            ("wip_ng", "WIP NG"),
            ("oqc", "OQC"),
            ("fg_input", "FG Input"),
            ("fg_stock", "FG Stock"),
            ("fg_ng", "FG NG"),
            ("repair", "Repair"),
            # stock 2
            ("m_stock_2", "Material Stock 2"),
            ("m_ng_2", "Material NG 2"),
            ("wip_input_2", "WIP Input 2"),
            ("wip_stock_2", "WIP Stock 2"),

            ("wip_1", "WIP 1"),
            ("wip_2", "WIP 2"),
            ("scrap", "Scrap"),
            ("w_ng_1", "WIP NG 1"),
            ("w_ng_2", "WIP NG 2"),
        ],
        string="Check Type",
        default="m_input",
    )
    product_category_ids = fields.Many2many(
        "product.category",
        string="Product Category",
        domain=lambda self: [
            (
                "parent_id",
                "=",
                self.env.ref("autonsi_standard_youngmin.product_category_fg").id,
            )
        ],
    )
    process_id = fields.Many2one("standard.process", string="Process")
    is_line = fields.Boolean(string="Is Line", default=False)

    def default_get(self, fields):
        res = super(LocationStock, self).default_get(fields)
        if res.get("location_type") == "area":
            default = self.env["stock.location"].search([("name", "=", "WH")])
            if default:
                res["location_id"] = default.id

        return res

    @api.onchange("row", "column", "location_id")
    def _onchange_fields(self):
        if self.location_type == "bin":
            self.bin_ids = [(5, 0, 0)]
            list = []
            if self.location_id and self.row > 0 and self.column > 0:
                stt = 0
                for i in range(1, self.row + 1):
                    for j in range(1, self.column + 1):
                        stt += 1
                        stri = "0" + str(i) if i < 10 else i
                        strj = "0" + str(j) if j < 10 else j
                        list.append(
                            (
                                0,
                                0,
                                {
                                    "stt": stt,
                                    "column": j,
                                    "row": i,
                                    "bin_code": f"{self.location_id.name} - {str(stri)} - {str(strj)}",
                                },
                            )
                        )
                self.name = self.location_id.name + " - 01 - 01"
            self.bin_ids = list
            self.row = self.row

    @api.constrains("check_type", "name", "location_id")
    def _check_unique_check_type_and_name(self):
        for record in self:
            if record.check_type and record.name:
                if record.check_type in ["ng", "input", "m_stock", "oqc", "repair"]:
                    duplicate = self.search(
                        [
                            ("id", "!=", record.id),
                            ("check_type", "=", record.check_type),
                            ("name", "=", record.name),
                            ("location_id", "=", record.location_id.id),
                        ],
                        limit=1,
                    )
                    if duplicate:
                        raise ValidationError(
                            _(
                                f'Location "{record.name}" with check type "{record.check_type}" already exists (duplicate with "{duplicate.display_name}").'
                            )
                        )

    def create_bin_auto(self):
        if self.location_type == "bin":
            for i in range(1, self.row + 1):
                for j in range(1, self.column + 1):
                    if not (i == 1 and j == 1):
                        stri = "0" + str(i) if i < 10 else i
                        strj = "0" + str(j) if j < 10 else j
                        location = self.env["stock.location"].create(
                            {
                                "name": f"{self.location_id.name} - {str(stri)} - {str(strj)}",
                                "location_type": "bin",
                                "location_id": self.location_id.id,
                                "description": self.description,
                                "comment": self.comment,
                            }
                        )

    @api.model
    def create(self, values):
        if values.get("location_type") == "area" and (
            "location_id" not in values or not values["location_id"]
        ):
            default = self.env["stock.location"].search([("name", "=", "WH")])
            if default:
                values["location_id"] = default.id

        result = super(LocationStock, self).create(values)
        if "row" in values and "column" in values:
            result.create_bin_auto()

        return result

    def unlink(self):
        check = 0
        for rec in self:
            duplicate_records = self.search([("location_id", "=", rec.id)])
            if duplicate_records:
                check = 1
                break
        if check == 1:
            raise UserError(
                "This code is already linked to another code, if you delete it you will lose the previously linked data, Delete linked first."
            )

        result = super(LocationStock, self).unlink()
        return result


class Model(models.Model):
    _name = "standard.binview"

    location_id = fields.Many2one("stock.location", string="location")
    stt = fields.Char("Seq", store=False)
    column = fields.Char("Columns no", store=False)
    row = fields.Char("Rows no", store=False)
    bin_code = fields.Char("Bin #", store=False)
