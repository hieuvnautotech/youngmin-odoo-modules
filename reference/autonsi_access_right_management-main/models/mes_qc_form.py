from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MESQCForm(models.Model):
    _inherit = "mes.qc_form"

    def get_employee_list(self):
        users = self.env["res.users"].search([("qms_rights", "!=", False)])
        employee_list = []
        for emp in users:
            rights = emp.qms_rights or "manager"
            employee_list.append({
                "id": emp.id,
                "name": emp.name,
                "role": rights,
            })

        return employee_list

    def get_self_id(self):
        print(self.env.user.name)
        return {"id": self.env.user.id, "name": self.env.user.name, "role": self.env.user.qms_rights or "manager"}