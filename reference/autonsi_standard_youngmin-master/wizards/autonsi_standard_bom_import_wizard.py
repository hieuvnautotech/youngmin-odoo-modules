from odoo import models, fields, api
import base64
import io
import xlrd
from odoo.exceptions import UserError, ValidationError


class AutonsiStandardBomImportWizard(models.TransientModel):
    _name = "autonsi.standard.bom.import.wizard"
    _description = "Import BOM Wizard"

    file = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename", ondelete="can")
    product_category_id = fields.Many2one('product.category',
                                          string='Product Category', domain=lambda self: [('parent_id', '=', self.env.ref('autonsi_standard_youngmin.product_category_fg').id)],
                                          required=True)
    is_vision_inspection = fields.Boolean(string="Vision Inspection", default=False)
    is_double_inspection_and_packing = fields.Boolean(string="Double Insp & Packing", default=False)

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

    def sort_bom_data(self, data):
        # Lọc chỉ lấy các item product_type = semi product (bán thành phẩm)
        filtered_data = [item for item in data if item.get("product_type") == "semi product"]

        # Tạo map bom_code -> item
        bom_map = {item["bom_code"]: item for item in filtered_data}
        # Tạo map quan hệ cha-con
        children_map = {}
        for item in filtered_data:
            parent = item.get("high_bom_code")
            if parent:
                children_map.setdefault(parent, []).append(item)

        # Hàm đệ quy để duyệt cây theo DFS từ sâu đến nông
        def traverse_deepest_first(bom_code, result, visited):
            if bom_code in visited:
                return
            visited.add(bom_code)

            children = children_map.get(bom_code, [])

            if children:
                # Sắp xếp con theo bom_code tăng dần
                children.sort(key=lambda x: x["bom_code"])

                # Duyệt từng con trước
                for child in children:
                    traverse_deepest_first(child["bom_code"], result, visited)

            # Thêm node hiện tại sau khi duyệt hết con (postorder traversal)
            if bom_code in bom_map:
                result.append(bom_map[bom_code])

        # Tìm node gốc trong filtered_data (có high_bom_code nhưng parent không nằm trong filtered_data)
        root_nodes = []
        parent_codes_in_filtered = {item["bom_code"] for item in filtered_data}
        for item in filtered_data:
            parent = item.get("high_bom_code")
            if not parent or parent not in parent_codes_in_filtered:
                root_nodes.append(item)
        # Sắp xếp root nodes theo bom_code
        root_nodes.sort(key=lambda x: x["bom_code"])
        result = []
        visited = set()
        for root in root_nodes:
            traverse_deepest_first(root["bom_code"], result, visited)
        return result

    def create_bom_hierarchy(self, data_list):
        Bom = self.env['mrp.bom']
        BomLine = self.env['mrp.bom.line']
        Product = self.env['product.product']
        Uom = self.env['uom.uom']

        # map bom_code -> record đã tạo (để truy xuất parent)
        bom_map = {}

        # danh sách bom gốc (root)
        roots = []

        # Duyệt theo thứ tự input (đã đúng thứ tự bom_code)
        for idx, item in enumerate(data_list):
            ptype = (item.get('product_type') or '').strip().lower()
            product_id = item.get('product_id')
            qty = item.get('quantity', 1.0) or 1.0
            uom_id = item.get('uom') or False
            product_code = item.get('product_code') or False
            bom_code = (item.get('bom_code') or '').strip()
            high_bom_code = (item.get('high_bom_code') or '').strip()

            # lookup product & uom an toàn
            product = Product.browse(product_id) if product_id else False
            uom = Uom.browse(uom_id) if uom_id else False

            parent_bom = bom_map.get(high_bom_code)

            # Nếu là bán thành phẩm / thành phẩm => tạo BOM riêng
            if ptype in ('semi product', 'fg product'):
                product_tmpl_id = product.product_tmpl_id.id if product and product.product_tmpl_id else False

                bom_vals = {
                    'product_id': product.id if product else False,
                    'product_tmpl_id': product_tmpl_id,
                    'product_qty': float(qty),
                    'product_uom_id': uom.id if uom else False,
                    'code': bom_code or product_code or f'AUTO_{idx}',
                    'type': 'normal',
                }
                bom = Bom.create(bom_vals)

                # lưu vào map
                bom_map[bom_code] = bom

                # nếu không có parent => root
                if not parent_bom:
                    roots.append(bom)
                else:
                    # tạo dòng trong parent (tham chiếu sub-assembly)
                    BomLine.create({
                        'bom_id': parent_bom.id,
                        'product_id': product.id if product else False,
                        'product_qty': float(qty),
                        'product_uom_id': uom.id if uom else False,
                    })

            # Nếu là nguyên vật liệu (material)
            elif ptype == 'material':
                # nếu có parent, gắn trực tiếp vào
                if parent_bom:
                    BomLine.create({
                        'bom_id': parent_bom.id,
                        'product_id': product.id if product else False,
                        'product_qty': float(qty),
                        'product_uom_id': uom.id if uom else False,
                    })
                else:
                    # nếu không có parent, coi như root BOM (hiếm khi xảy ra)
                    product_tmpl_id = product.product_tmpl_id.id if product and product.product_tmpl_id else False
                    bom_vals = {
                        'product_id': product.id if product else False,
                        'product_tmpl_id': product_tmpl_id,
                        'product_qty': float(qty),
                        'product_uom_id': uom.id if uom else False,
                        'code': bom_code or f'MAT_{idx}',
                        'type': 'normal',
                    }
                    bom = Bom.create(bom_vals)
                    bom_map[bom_code] = bom
                    roots.append(bom)

            else:
                print('⚠️ Unknown product_type:', ptype, '→ skipped item:', item)

        return roots

    def create_bom_process_hierarchy(self, bom, data_list):
        BomProcess = self.env['mrp.bom.process']
        Material = self.env['mrp.bom.process.material']  # hoặc model thực tế của bạn
        sequence = 1

        # Tạo mapping nhanh để tra cứu theo bom_code
        bom_map = {item.get('bom_code'): item for item in data_list if item.get('bom_code')}

        for item in data_list:
            process_id = item.get('process_id')
            if not process_id:
                continue

            bom_code = item.get('bom_code')
            high_bom_code = item.get('high_bom_code')
            product_id = item.get('product_id')
            qty = float(item.get('quantity', 1.0) or 1.0)
            uom_id = item.get('uom') or False

            # Tìm hoặc tạo process trong BOM hiện tại
            process = BomProcess.search([
                ('bom_id', '=', bom.id),
                ('name', '=', process_id)
            ], limit=1)

            if not process:
                process = BomProcess.create({
                    'bom_id': bom.id,
                    'name': process_id,
                    'sequence': sequence,
                    'target_product_id': product_id,
                })
                sequence += 1

            # Tìm tất cả con có high_bom_code == bom_code hiện tại
            children = [itm for itm in data_list if itm.get('high_bom_code') == bom_code]


            # Nếu không có con → coi đây là process cuối (có vật tư trực tiếp)
            if not children:

                Material.create({
                    'name': product_id,
                    'quantity': qty,
                    'unit': uom_id,
                    'bomprocess_id': process.id,
                })
            else:
                # Có con → lặp qua từng con để tạo vật tư
                for child in children:
                    Material.create({
                        'name': child.get('product_id'),
                        'quantity': float(child.get('quantity', 1.0) or 1.0),
                        'unit': child.get('uom') or False,
                        'bomprocess_id': process.id,
                    })

        # Debug xem kết quả
        return bom.process_ids

    def create_bom_process(self, bom, process_data, all_data):
        BomProcess = self.env['mrp.bom.process']
        Material = self.env['mrp.bom.process.material']  # hoặc model thực tế của bạn
        sequence = 1

        for item in process_data:
            process = item.get('process')
            product = item.get('product')
            bom_code = item.get('bom_code')

            children = [itm for itm in all_data if itm.get('high_bom_code') == bom_code]


            bom_process = BomProcess.create({
                'bom_id': bom.id,
                'name': process.id,
                'sequence': sequence,
                'target_product_id': product.id,
            })
            for child in children:
                uom = child.get('uom') or False
                # if uom == 64:
                #     raise ValidationError("UOM KG chưa được cấu hình trong BOM Process Material.")
                Material.create({
                    'name': child.get('product_id'),
                    'quantity': float(child.get('quantity', 1.0) or 1.0),
                    'unit': child.get('uom') or False,
                    'bomprocess_id': bom_process.id,
                })
            sequence += 1
        return bom.process_ids

    def create_semi_product(self, process_code, process_name, fg_item):
        fg_product_code = fg_item['product_code']
        semi_product = self.env["product.product"].search(
            [("default_code", "=", f"{fg_product_code}-{process_code}")], limit=1)
        if not semi_product:
            print("uom name", fg_item['product'].uom_id.name)
            semi_product = self.env["product.product"].create(
                {
                    "name": f"{fg_item['product_name']}",
                    "default_code": f"{fg_product_code}-{process_code}",
                    "product_type": "semi product",
                    "uom_id": fg_item['product'].uom_id.id,
                }
            )
        process = self.env["standard.process"].search(
            [("code", "=", process_code)], limit=1
        )
        if not process:
            process = self.env["standard.process"].create(
                {
                    "name": process_name,
                    "code": process_code,
                }
            )
        return semi_product, process

    def action_import_bom(self):
        self.ensure_one()
        if not self.file:
            raise UserError("Please upload a file before importing.")
        
        # remove context default_product_category_id
        self = self.with_context(default_product_category_id=None)
        is_from_sale_order = self._context.get('is_from_sale_order', False)



        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        data = []
        is_hm = self.product_category_id == self.env.ref('autonsi_standard_youngmin.product_category_hm')
        for row in range(1, sheet.nrows):
            # B F K L R S Q P
            level_raw = sheet.cell_value(row, self.excel_column_to_number("B"))
            # Convert dotted format level to integer
            if isinstance(level_raw, str):
                # Count dots/periods before the number to determine the level depth
                dot_count = level_raw.count(".")
                # Extract the numeric part
                numeric_part = level_raw.strip(".")
                level = int(numeric_part) if numeric_part else dot_count // 3
            else:
                level = int(level_raw) if level_raw else 0
            item_group = sheet.cell_value(row, self.excel_column_to_number("F"))
            project_code = sheet.cell_value(row, self.excel_column_to_number("K"))
            project_name = project_code
            product_code = sheet.cell_value(row, self.excel_column_to_number("L"))
            process_code = sheet.cell_value(row, self.excel_column_to_number("R"))
            product_name = sheet.cell_value(row, self.excel_column_to_number("N"))
            bom_code = sheet.cell_value(row, self.excel_column_to_number("D"))
            high_bom_code = sheet.cell_value(row, self.excel_column_to_number("E"))
            quantity = self.format_cell_value_as_number(
                sheet.cell_value(row, self.excel_column_to_number("Q"))
            )
            uom_name = sheet.cell_value(row, self.excel_column_to_number("P"))
            # = sheet.cell_value(row, self.excel_column_to_number("U"))
            # if is_hm or is_swh:
            #     buyer_supplier = sheet.cell_value(row, self.excel_column_to_number("S"))
            # check uom_name is not string
            # if not isinstance(uom_name, str):
            #     uom_name = sheet.cell_value(row, self.excel_column_to_number("Q"))
            #     if not isinstance(uom_name, str):
            #         uom_name = sheet.cell_value(row, self.excel_column_to_number("U"))
            # print("uom name", uom_name)

            process = self.env["standard.process"]
            product_types = {
                "자재": "material",
                "반제품": "semi product",
                "완제품": "fg product",
            }
            product_type = product_types.get(item_group, "material")
            original_process_code = process_code

            if process_code:
                if process_code == "050":
                    if is_hm:
                        process_code = "220"
                if process_code == "240" or process_code == "260" or process_code == "290":
                    process_code = "260"

                if process_code == "270" or process_code == "300":
                    process_code = "300"

                if process_code == "330" or process_code == "410" or process_code == "420" or process_code == "430":
                    process_code = "430"

                if process_code == "040" and not is_hm:
                    process_code = "400"

                process = self.env["standard.process"].search(
                    [("code", "=", process_code)], limit=1
                )
                if not process and product_type != "fg product":
                    raise ValidationError(f"Process with code {process_code} not found.")
                # if not process:
                #     process = self.env["standard.process"].create(
                #         {
                #             "name": process_name,
                #             "code": process_code,
                #         }
                #     )


            project = self.env["standard.project"]
            if project_code:
                project = self.env["standard.project"].search(
                    [("code", "=", project_code)], limit=1
                )
                if not project:
                    project = self.env["standard.project"].create(
                        {
                            "name": project_name,
                            "code": project_code,
                        }
                    )

            product = self.env["product.product"].search(
                [("default_code", "=", product_code)], limit=1
            )

            if not product:
                uom = self.env["uom.uom"].search([("name", "=", uom_name.upper())], limit=1)
                if not uom:
                    uom = self.env["uom.uom"].create(
                        {
                            "name": uom_name.upper(),
                            "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                            "uom_type": "smaller",
                            "ratio": 1,
                        }
                    )
                product = self.env["product.product"].create(
                    {
                        "name": product_name,
                        "default_code": product_code,
                        "product_type": product_types.get(item_group, "material"),
                        "uom_id": uom.id,
                        "categ_id": self.product_category_id.id if product_type == "fg product" else self.env.ref('product.product_category_all').id,
                    }
                )

            if product.project_id != project and project:
                product.project_id = project.id
            if product.categ_id != self.product_category_id and product_type == "fg product":
                product.categ_id = self.product_category_id


            # Create the new item data
            # check exist level, plus 0.1
            # existing_levels = [item['level'] for item in data]
            # while level in existing_levels:
            #     level += 0.1

            new_item = {
                "level": level,
                "item_group": item_group,
                "product_type": product_types.get(item_group, "material"),
                "project_name": project_name,
                "project_code": project_code,
                "product_code": product_code,
                "process_code": process_code,
                # "process_name": process_name,
                "process_id": process.id,
                "product_name": product_name,
                "product_id": product.id,
                "quantity": quantity,
                "uom": product.uom_id.id,
                # "buyer_supplier": buyer_supplier,
                "project": project,
                "product": product,
                "process": process,
                "bom_code": bom_code,
                "high_bom_code": high_bom_code,
                "original_process_code": original_process_code
            }

            data.append(new_item)
        

        print("data", data)
        for idx, item in enumerate(data):
            if item['original_process_code'] == "400":
                # remove item
                # data.pop(idx)
                # get previous item
                if idx > 0:
                    previous_item = data[idx - 1]
                    # set high_bom_code of previous item to current item's high_bom_code
                    #get next item
                    if idx + 1 < len(data):
                        next_item = data[idx + 1]
                        next_item['high_bom_code'] = previous_item['bom_code']
                    data.pop(idx)

        # raise ValidationError("CCC")


        fg_level = -2
        fg_item = next((item for item in data if item['product_type'] == 'fg product'), None)
        if self.is_vision_inspection:
            fg_level -= 1
        if self.is_double_inspection_and_packing:
            fg_level -= 1

        for item in data:
            if item['level'] == 0:
                item['level'] = fg_level

        level = 0
        fg_product_code = fg_item['product_code']

        semi_product_structure_inps, structure_inspection_process = self.create_semi_product("490", "Structure Inspection", fg_item )
        semi_product_circuit_inps, circuit_inspection_process = self.create_semi_product("500", "Circuit Insp & Packing", fg_item )
        semi_product_vision_inps, vision_inspection_process = None, None

        # process Vision Inspection
        if self.is_vision_inspection:
            semi_product_vision_inps, vision_inspection_process = self.create_semi_product("480", "Vision Inspection", fg_item )
            data.append({
                "level": level,
                "product_type": "semi product",
                "project_name": None,
                "project_code": None,
                "process_code": vision_inspection_process.code,
                "process_name": vision_inspection_process.name,
                "process_id": vision_inspection_process.id,
                "product_name": semi_product_structure_inps.name,
                "product_id": semi_product_structure_inps.id,
                "product_code": semi_product_structure_inps.default_code,
                "quantity": 1,
                "uom": semi_product_structure_inps.uom_id.id,
                # "buyer_supplier": buyer_supplier,
                # "project": project,
                "product": semi_product_structure_inps,
                "process": vision_inspection_process,
                "bom_code": "480",
                "high_bom_code": "490",
            })
            level -= 1

        data.append({
            "level": level,
            "product_type": "semi product",
            "project_name": None,
            "project_code": None,
            "product_code": semi_product_circuit_inps.default_code,
            "process_code": structure_inspection_process.code,
            "process_name": structure_inspection_process.name,
            "process_id": structure_inspection_process.id,
            "product_name": semi_product_circuit_inps.name,
            "product_id": semi_product_circuit_inps.id,
            "quantity": 1,
            "uom": semi_product_circuit_inps.uom_id.id,
            # "buyer_supplier": buyer_supplier,
            # "project": project,
            "product": semi_product_circuit_inps,
            "process": structure_inspection_process,
            "bom_code": structure_inspection_process.code,
            "high_bom_code": "500",
        })
        level -= 1

        semi_product_double_insp_packing, double_insp_packing_process = None, None
        if self.is_double_inspection_and_packing:
            semi_product_double_insp_packing, double_insp_packing_process = self.create_semi_product("510", "Final Insp & Packing", fg_item )
        fg_product = fg_item['product']
        data.append({
            "level": level,
            "product_type": "semi product",
            "project_name": None,
            "project_code": None,
            "product_code": semi_product_double_insp_packing.default_code if semi_product_double_insp_packing else fg_product.default_code,
            "process_code": circuit_inspection_process.code,
            "process_name": circuit_inspection_process.name,
            "process_id": circuit_inspection_process.id,
            "product_name": semi_product_double_insp_packing.name if semi_product_double_insp_packing else fg_product.name,
            "product_id": semi_product_double_insp_packing.id if semi_product_double_insp_packing else fg_product.id,
            "quantity": 1,
            "uom": semi_product_double_insp_packing.uom_id.id if semi_product_double_insp_packing else fg_product.uom_id.id,
            # "buyer_supplier": buyer_supplier,
            # "project": project,
            "product": semi_product_double_insp_packing if semi_product_double_insp_packing else fg_product,
            "process": circuit_inspection_process,
            "bom_code": circuit_inspection_process.code,
            "high_bom_code": "510" if self.is_double_inspection_and_packing else fg_item['bom_code'],
        })
        level -= 1

        # process Double Insp & Packing
        if self.is_double_inspection_and_packing:

            semi_product, process = fg_product, double_insp_packing_process
            data.append({
                "level": level,
                "product_type": "semi product",
                "project_name": None,
                "project_code": None,
                "product_code": semi_product.default_code,
                "process_code": process.code,
                "process_name": process.name,
                "process_id": process.id,
                "product_name": semi_product.name,
                "product_id": semi_product.id,
                "quantity": 1,
                "uom": semi_product.uom_id.id,
                # "buyer_supplier": buyer_supplier,
                # "project": project,
                "product": semi_product,
                "process": process,
                "bom_code": double_insp_packing_process.code,
                "high_bom_code": fg_item['bom_code'],
            })
            level -= 1

        test_data = []
        for idx, item in enumerate(data):
            test_data.append({
                'level': item['level'],
                'bom_code': item['bom_code'],
                'high_bom_code': item['high_bom_code'],
                'process_code': item['process_code'],
                'product_code': item['product_code'],
            })
            item['index'] = idx  # giữ thứ tự gốc để sắp xếp lại sau
            if item['high_bom_code'] == fg_item['bom_code'] and item['level'] == 1:
                if item['product_type'] == 'material':
                    item['high_bom_code'] = "500"
                else:
                    item['high_bom_code'] = "480" if self.is_vision_inspection else "490"
            if item['process_code'] == "020":
                childs = [itm for itm in data if itm.get('high_bom_code') == item['bom_code']]
                if childs:
                    child = childs[0]
                    semi_product = item['product']
                    material_product = child['product']
                    semi_code = f"{material_product.default_code}-{semi_product.default_code}"
                    semi_product_search = self.env["product.product"].search(
                        [("default_code", "=", semi_code)], limit=1)
                    if semi_product_search:
                        semi_product = semi_product_search
                    else:
                        semi_product.default_code = semi_code
                    semi_product.name = semi_code
                    # Update item product to semi_product
                    item['product'] = semi_product
                    item['product_id'] = semi_product.id
                    item['product_code'] = semi_product.default_code
                    item['quantity'] = 0.5
                    # if semi_product.default_code and material_product.default_code and not semi_product.default_code.startswith(material_product.default_code):
                    #     semi_product.default_code = f"{material_product.default_code}-{semi_product.default_code}"
                    #     semi_product.name = semi_product.default_code


        # bom = self.create_bom_hierarchy(data)
        bom = self.env['mrp.bom'].create({
            'product_id': fg_item['product_id'],
            'product_tmpl_id': fg_item['product'].product_tmpl_id.id,
            'product_qty': 1.0,
            'product_uom_id': fg_item['uom'],
            'code': fg_item['bom_code'],
            'type': 'normal',
            'file_imported': self.file,
            'filename_imported': self.filename,
        })

        sorted_data = self.sort_bom_data(data)
        # print("sorted_data", sorted_data)
        # for item in sorted_data:
        #     # print("process_code", item['process_code'])
        #     print("item sorted", item)
        #
        #
        #
        # # sắp xếp giảm dần theo level để xử lý từ dưới lên
        # data.sort(key=lambda x: int(x['bom_code']), reverse=True)
        #
        # fg_bom_code = fg_item['bom_code']
        # new_data_sort = []
        # for item in data:
        #     if item['process_code'] not in ("480", "490", "500", "510") or item['bom_code'] == fg_bom_code:
        #         new_data_sort.append(item)
        #
        # # process 480, 490, 500, 510 cuối cùng
        # process_480 = [item for item in data if item['process_code'] == "480"]
        # process_490 = [item for item in data if item['process_code'] == "490"]
        # process_500 = [item for item in data if item['process_code'] == "500"]
        # process_510 = [item for item in data if item['process_code'] == "510"]
        # process_fg = [item for item in data if item['bom_code'] == fg_bom_code]
        # new_data_sort += process_480 + process_490 + process_500 + process_510 + process_fg
        #
        # data = new_data_sort
        #
        # for item in data:
        #     print("bomcode", item['bom_code'])

        bom = bom[0]  # Giả sử chỉ lấy bom root đầu tiên để tạo process
        # process_ids = self.create_bom_process_hierarchy(bom, data)
        process_ids = self.create_bom_process(bom, sorted_data, data)

        # raise ValidationError("CCC")


        for process in process_ids:
            location = process.name.location_ids.filtered(lambda loc: self.product_category_id in loc.product_category_ids )
            if not location:
                raise ValidationError(f"No location found for process {process.name.code} and product category {self.product_category_id.name}.")
            location = location[0]

            process.source_location_id = location

        process_list = process_ids.sorted(key=lambda r: r.sequence)

        for index, process in enumerate(process_list):
            # Tìm process tiếp theo dựa trên target_product_id trong material_ids
            if process.target_product_id:
                next_process = process_list.filtered(
                    lambda p: process.target_product_id.id in p.material_ids.mapped('name').ids
                )
                if next_process:
                    process.destination_location_id = next_process[0].source_location_id
                else:
                    # Nếu không tìm thấy process tiếp theo, đây là process cuối
                    if is_hm:
                        process.destination_location_id = self.env.ref('autonsi_standard_youngmin.location_fg_stock_2').id
                    else:
                        process.destination_location_id = self.env.ref('autonsi_standard_youngmin.location_fg_stock_1').id
            else:
                # Nếu không có target_product_id, đây là process cuối
                if is_hm:
                    process.destination_location_id = self.env.ref('autonsi_standard_youngmin.location_fg_stock_2').id
                else:
                    process.destination_location_id = self.env.ref('autonsi_standard_youngmin.location_fg_stock_1').id





        # raise ValidationError("Import functionality is under development.")

        bom.action_confirm()

        if is_from_sale_order:
            return bom

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Import Complete",
                "message": "BOMs imported successfully!",
                "type": "success",
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
