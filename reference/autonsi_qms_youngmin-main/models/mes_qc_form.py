from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MESQCForm(models.Model):
    _inherit = "mes.qc_form"

    type_roll = fields.Selection([
        ("first", "Initial"),
        ("mid", "In-process"),
        ("final", "Final"),
    ], default="first", string="Type")

    is_emb = fields.Boolean(string="Is EMB Inspection", compute="_compute_is_emb", store=True)

    @api.depends("process_ids")
    def _compute_is_emb(self):
        ref_ids = [
            self.env.ref("autonsi_standard_youngmin.common_record_process_040_emb_hm").id,
            self.env.ref("autonsi_standard_youngmin.common_record_process_400_emb_swh").id,
        ]
        for rec in self:
            rec.is_emb = bool(rec.process_ids.filtered(lambda p: p.id in ref_ids))

    def get_employee_list(self):
        employees = self.env["res.users"].search([])
        employees_list = []
        for employee in employees:
            employees_list.append(
                {"id": employee.id, "name": employee.name, "role": "manager"})
        return employees_list

    def get_self_id(self):
        print(self.env.user.name)
        return {"id": self.env.user.id, "name": self.env.user.name, "role": "manager"}

    def get_doc_ids_list(self):
        for record in self:
            doc_list = []
            for doc in record.doc_ids:
                doc_list.append(
                    {"id": doc.id, "name": doc.file_upload_name})
            return doc_list

    def preview_form(self):
        if self.form_type == "iqc":
            return self.preview_iqc_form()
        if self.form_type == "pqc":
            return self.preview_pqc_form()
        if self.form_type == "jig":
            return self.preview_jig_form()
        if self.form_type == "re_use":
            return self.preview_re_use_form()
        if self.form_type == "item_qc":
            return self.preview_item_qc_form()
        if self.form_type == "oqc":
            return self.preview_oqc_form()
        if self.form_type == "pallet_qc":
            return self.preview_pallet_qc_form()
        return self.preview_iqc_form()

    
    def preview_iqc_form(self):
        context_data = {
            "title": self.name,
            'category_material': self.category_material,
            'supplier': _("YM Korea"),
            'material_code': _("2102"),
            'material_name': _("Black Fabric – 1"),
            'lot': _("T08/6958/UJ2A/200"),
            'qty_uom': _("200M"),
            'isHistory': False,
            'isPreview': True,
            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            'confirm_staff_id': self.env.user.id,
            'confirm_staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_iqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_iqc_action"
        name = _(f"QMS IQC")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def preview_pqc_form(self):
        context_data = {
            "title": self.name,
            'category_material': self.category_material,
            'supplier': _("YM Korea"),
            'material_code': _("2102"),
            'material_name': _("Black Fabric – 1"),
            'line_no': _("01"),
            'lot': _("T08/6958/UJ2A/200"),
            'qty_uom': _("200M"),
            'isHistory': False,
            'isPreview': True,
            'isEMB': self.is_emb,
            'type_roll': "first",

            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_pqc_action"
        name = _(f"QMS PQC")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def preview_oqc_form(self):
        context_data = {
            "title": self.name,
            'material_code': _("2102"),
            'material_name': _("Black Fabric – 1"),
            'line_no': _("01"),
            'lot': _("T08/6958/UJ2A/200"),
            'qty_uom': _("200M"),
            'isHistory': False,
            'isPreview': True,
            'is_resistance': self.id == self.env.ref("autonsi_qms.item_qc_form_oqc_resistance").id,
            'is_final_process': self.id == self.env.ref("autonsi_qms.item_qc_form_oqc_resistance").id,
            'isEMB': self.is_emb,
            'type_roll': "first",

            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_oqc_action"
        name = _(f"QMS PQC")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def preview_jig_form(self):
        context_data = {
            "title": self.name,
            'product_code': "xxx",
            'supplier': "xxx",
            'jig_code': "xxx",
            'jig_name': "xxx",
            'process': "xxx",
            'rev': "xxx",
            'remark': "xxx",
            'create_date': "xxx",
            'isHistory': False,
            'isPreview': True,
            'type_roll': "first",

            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_jig_action"
        name = _(f"QMS JIG")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }


    def prepare_check_list_data(self):
        check_list = []

        for question in self.question_ids:
            base_data = {
                "id": question.id,
                "qc_type": question.mes_qc_type_id.name or 'Visual',
                "qc_process": question.mes_qc_item_id.display_name or '',
                "qc_code": question.mes_qc_standard_id.name or '',
                "method": question.mes_qc_tool_id.display_name or 'By Eyes',
                "frequency": question.mes_qc_frequency_id.name or '',
                "standard": question.mes_qc_standard_sees_id.name or '',

                "result": "",  # Default value
                "result_pqc": False,  # Default value
                "pqc_worker_id": False,  # Default value
                "pqc_fixed": False,  # Default value
                "remark": "",  # Default empty
                "input_type": question.mes_qc_tool_id.input_type or 'ok_ng',

                "X1": "", "X2": "", "X3": "", "X4": "", "X5": "",
                "HD1": "", "HD2": "", "HD3": "", "HD4": "", "HD5": "", "HD6": "", "HD7": "", "HD8": "", "HD9": "",
                "HD10": "", "HD11": "", "HD12": "", "HD13": "", "HD14": "",

                # Metadata
                "mes_qc_type_id": question.mes_qc_type_id.id or False,
                "mes_qc_item_id": question.mes_qc_item_id.id or False,
                "mes_qc_form_question_id": question.id or False,
                "mes_qc_tool_id": question.mes_qc_tool_id.id or False,
                "mes_qc_standard_sees_id": question.mes_qc_standard_sees_id.id or False,
                "mes_qc_frequency_id": question.mes_qc_frequency_id.id or False,
            }

            check_list.append(base_data)

        return check_list

    def preview_re_use_form(self):
        context_data = {
            "title": self.name,
            "item_group": self.item_group,
            'remaining_days': 365,
            'life_days': 365,
            'category_material': self.category_material,
            'supplier': _("YM Korea"),
            'material_code': _("2102"),
            'material_name': _("Black Fabric – 1"),
            'lot': _("T08/6958/UJ2A/200"),
            'qty_uom': _("200M"),
            'isHistory': False,
            'isPreview': True,
            'type_roll': "first",

            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_re_use_action"
        name = _(f"QMS RE-USE")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def preview_item_qc_form(self):
        context_data = {
            "title": self.name,
            'category_material': "xxx",
            'supplier': _("YM Korea"),
            'material_code': _("2102"),
            'material_name': _("Black Fabric – 1"),
            'spec': _("xxx"),
            'lot': _("T08/6958/UJ2A/200"),
            'qty_uom': _("200M"),
            'isHistory': False,
            'isPreview': True,
            'type_roll': "first",

            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'form_id': self.id,
        }
        tag = "qms_question_item_qc_action"
        name = _(f"QMS ITEM QC")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }

    def preview_pallet_qc_form(self):
        context_data = {
            "title": self.name,
            'pallet_no': _("P001 - A"),
            'project_code': _("VF33"),
            'material_code': _("56185K2500"),
            'material_name': _("PAD LEA"),
            'lot': _("2"),
            'qty_uom': _("EA"),
            'isHistory': False,
            'isPreview': True,
            'employee_list': self.get_employee_list(),
            'self_id': self.get_self_id(),
            'doc_list': self.get_doc_ids_list(),
            'staff_id': self.env.user.id,
            'staff_name': self.env.user.name,
            'confirm_staff_id': self.env.user.id,
            'confirm_staff_name': self.env.user.name,
            # 'check_date': "",
            # 'final_result': "OK",
            'columns': self.get_pqc_column_config(),
            'check_list': self.prepare_check_list_data(),
            'qty':100,
            'form_id': self.id,
        }
        tag = "qms_question_pallet_qc_action"
        name = _(f"QMS Pallet QC")
        return {
            "type": "ir.actions.client",
            "tag": tag,
            "name": name,
            "context": context_data,
            "target": "new",
        }


    def get_iqc_column_config(self, isHistory = False):
        editable = True if not isHistory else False
        base_columns = [
            # {
            #     'field': 'qc_type',
            #     'title': _('QC Type'),
            #     'width': '80px',
            #     'visible': True,
            #     'sortable': False
            # },
            # {
            #     'field': 'qc_process',
            #     'title': _('QC Process'),
            #     'width': '200px',
            #     'visible': True,
            #     'sortable': True
            # },
            {
                'field': 'qc_code',
                'title': _('QC Code'),
                'width': '150px',
                'visible': True,
                'sortable': True
            },
            {
                'field': 'method',
                'title': _('Method'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'frequency',
                'title': _('Frequency'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'standard',
                'title': _('UoM'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'X1',
                'title': 'X1',
                'width': '120px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': '',
            },
            {
                'field': 'X2',
                'title': 'X2',
                'width': '120px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': '',
            },
            {
                'field': 'X3',
                'title': 'X3',
                'width': '120px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': '',
            },
            {
                'field': 'X4',
                'title': 'X4',
                'width': '120px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': '',
            },
            {
                'field': 'X5',
                'title': 'X5',
                'width': '120px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': '',
            },
            {
                'field': 'result',
                'title': _('Result'),
                'width': '80px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': 'select',
            },
            {
                'field': 'remark',
                'title': _('Remark'),
                'width': '150px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': 'text'
            }
        ]

        return base_columns

    def get_pqc_column_config(self, isHistory = False):
        editable = True if not isHistory else False
        base_columns = [
            # {
            #     'field': 'qc_type',
            #     'title': _('QC Type'),
            #     'width': '80px',
            #     'visible': True,
            #     'sortable': False
            # },
            # {
            #     'field': 'qc_process',
            #     'title': _('QC Process'),
            #     'width': '200px',
            #     'visible': True,
            #     'sortable': True
            # },
            {
                'field': 'qc_code',
                'title': _('QC Code'),
                'width': '150px',
                'visible': True,
                'sortable': True
            },
            {
                'field': 'method',
                'title': _('Method'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'frequency',
                'title': _('Frequency'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'standard',
                'title': _('UoM'),
                'width': '100px',
                'visible': True,
                'sortable': False
            },
            {
                'field': 'result',
                'title': _('Result'),
                'width': '80px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': 'select',
            },
            {
                'field': 'remark',
                'title': _('Remark'),
                'width': '150px',
                'visible': True,
                'sortable': False,
                'editable': True,
                'type': 'text'
            }
        ]

        if self.is_emb:
            base_columns = [col for col in base_columns if col['field'] != 'result']
            hd_columns = [
                {
                    'field': f'HD{i}',
                    'title': f'HD {i}',
                    'width': '80px',
                    'visible': True,
                    'sortable': False,
                }
                for i in range(1, 15)
            ]
            idx = next(
                (i for i, col in enumerate(base_columns) if col['field'] == 'standard'),
                None
            )

            if idx is not None:
                base_columns[idx + 1:idx + 1] = hd_columns

        return base_columns