from odoo import models, fields, api
import base64
import io
import xlrd
from odoo.exceptions import UserError, ValidationError


class MaterialImportKoreaIDWizard(models.TransientModel):
    _name = "material.import.korea.id.wizard"

    file = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")


    @staticmethod
    def excel_column_to_number(column_name):
        column_name = column_name.upper()
        length = len(column_name)
        number = 0
        for i, char in enumerate(column_name):
            number = number * 26 + (ord(char) - ord("A") + 1)
        return number - 1

    @staticmethod
    def format_cell_value_as_number(cell_value):
        if isinstance(cell_value, float) or isinstance(cell_value, int):
            return cell_value
        else:
            try:

                return float(cell_value)
            except ValueError:
                return 0

    def action_import_file(self):
        self.ensure_one()
        if not self.file:
            raise UserError("Please upload a file before importing.")

        import base64
        import xlrd

        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        # --- B1: Thu thập dữ liệu từ file ---
        raw_data = []
        for row in range(1, sheet.nrows):
            id_in_korea = sheet.cell_value(row, self.excel_column_to_number("K"))
            material_code = sheet.cell_value(row, self.excel_column_to_number("L"))
            standard_qty = sheet.cell_value(row, self.excel_column_to_number("AE"))
            if not (material_code and id_in_korea):
                continue
            raw_data.append({
                "id_in_korea": id_in_korea,
                "material_code": material_code,
                "standard_qty": standard_qty,
            })

        # --- B2: Lấy danh sách mã cần tìm ---
        material_codes = [d["material_code"] for d in raw_data]
        products = self.env["product.product"].search([("default_code", "in", material_codes)])

        # Tạo map code -> record
        product_map = {p.default_code: p for p in products}

        # --- B3: Chuẩn bị dữ liệu để ghi ---
        not_found = []
        to_update = []
        for item in raw_data:
            product = product_map.get(item["material_code"])
            if product:
                to_update.append((product, {
                    "standard_qty": item["standard_qty"],
                    "id_in_korea": item["id_in_korea"],
                }))
            else:
                not_found.append(item["material_code"])

        # --- B4: Ghi dữ liệu theo batch (nhanh hơn nhiều) ---
        for product, vals in to_update:
            product.write(vals)

        # (Tuỳ chọn) có thể dùng `self.env.cr.execute()` để update hàng loạt nhanh hơn nữa:
        # for item in to_update:
        #     self.env.cr.execute("""
        #         UPDATE product_product
        #         SET standard_qty = %s, id_in_korea = %s
        #         WHERE id = %s
        #     """, (item["standard_qty"], item["id_in_korea"], product.id))
        # self.env.cr.commit()

        # --- B5: Thông báo kết quả ---
        message = f"Imported {len(to_update)} materials successfully!"
        if not_found:
            message += f"\nNot found: {', '.join(not_found[:10])}..."

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Import Complete",
                "message": message,
                "type": "success",
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

