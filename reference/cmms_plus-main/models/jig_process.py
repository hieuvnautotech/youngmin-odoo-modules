from datetime import date, datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from psycopg2 import IntegrityError
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class JigProcess(models.Model):
    _name = 'jig.process'

    name= fields.Char("Name")
    code= fields.Char("Code")

    # @api.model
    # def init(self):
    #     # Nếu chưa có dữ liệu nào thì tự động tạo mẫu
    #     if not self.search_count([]):
    #         default_items = [
    #             {"name": "Inspection EMB", "code": "1"},
    #              {"name": "OQC visual​", "code": "2"},
    #               {"name": "Forming", "code": "3"},
    #             {"name": "Tape", "code": "4"},

    #         ]
    #         self.create(default_items)

