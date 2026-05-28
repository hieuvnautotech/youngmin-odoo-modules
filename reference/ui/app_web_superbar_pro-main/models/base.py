# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
import re

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    _inherit = 'base'
    
    def _natural_sort_key(self, value):
        """
        Tạo key để sắp xếp tự nhiên (natural sorting)
        Ví dụ: 7I-504-006 sẽ được tách thành ['7', 'I', '504', '006']
        """
        if not value:
            return []
        
        # Tách chuỗi thành các phần số và chữ
        parts = re.split(r'(\d+)', str(value))
        result = []
        
        for part in parts:
            if part.isdigit():
                # Chuyển số thành integer để sắp xếp đúng
                result.append(int(part))
            else:
                # Giữ nguyên phần chữ
                result.append(part)
        
        return result
    
    def _sort_records_by_order(self, records, order):
        """
        Sắp xếp records theo order string
        """
        if not order or not records:
            return records
            
        # Parse order string
        order_specs = []
        for order_spec in order.split(','):
            order_spec = order_spec.strip()
            if ' ' in order_spec:
                field, direction = order_spec.rsplit(' ', 1)
                direction = direction.upper()
            else:
                field, direction = order_spec, 'ASC'
            order_specs.append((field.strip(), direction))
        
        def sort_key(record):
            key_parts = []
            for field, direction in order_specs:
                if hasattr(record, field):
                    value = getattr(record, field)
                    
                    # Lấy giá trị thực tế để sort
                    if hasattr(value, 'name'):  # Many2one field
                        actual_value = value.name
                    elif hasattr(value, 'display_name'):  # Many2one field
                        actual_value = value.display_name
                    else:
                        actual_value = value
                    
                    # Normalize values for consistent comparison
                    if isinstance(actual_value, str):
                        # Sử dụng natural sorting cho string values
                        sort_value = ('string', self._natural_sort_key(actual_value))
                    elif isinstance(actual_value, bool):
                        # Convert boolean to comparable format
                        sort_value = ('bool', int(actual_value))
                    elif isinstance(actual_value, (int, float)):
                        sort_value = ('number', actual_value)
                    elif actual_value is None:
                        sort_value = ('none', 0)
                    else:
                        # For other types, convert to string and use natural sorting
                        sort_value = ('string', self._natural_sort_key(str(actual_value)))
                    
                    key_parts.append((sort_value, direction))
                else:
                    key_parts.append((('none', 0), direction))
            
            return key_parts
        
        def compare_values(a, b):
            """So sánh hai giá trị với type safety"""
            # Extract type and value
            a_type, a_value = a
            b_type, b_value = b
            
            # If different types, sort by type priority
            type_priority = {'none': 0, 'bool': 1, 'number': 2, 'string': 3}
            if a_type != b_type:
                return type_priority.get(a_type, 99) - type_priority.get(b_type, 99)
            
            # Same type comparison
            if a_type == 'string':
                # Natural sorting comparison for lists
                for i in range(min(len(a_value), len(b_value))):
                    if a_value[i] != b_value[i]:
                        if isinstance(a_value[i], int) and isinstance(b_value[i], int):
                            return a_value[i] - b_value[i]
                        elif isinstance(a_value[i], str) and isinstance(b_value[i], str):
                            return -1 if a_value[i] < b_value[i] else (1 if a_value[i] > b_value[i] else 0)
                        else:
                            return -1 if str(a_value[i]) < str(b_value[i]) else (1 if str(a_value[i]) > str(b_value[i]) else 0)
                return len(a_value) - len(b_value)
            else:
                # Simple comparison for other types
                if a_value < b_value:
                    return -1
                elif a_value > b_value:
                    return 1
                else:
                    return 0
        
        def sort_comparison(record1, record2):
            """Hàm so sánh để sort"""
            key1 = sort_key(record1)
            key2 = sort_key(record2)
            
            for i in range(min(len(key1), len(key2))):
                value1, direction1 = key1[i]
                value2, direction2 = key2[i]
                
                comparison = compare_values(value1, value2)
                
                if comparison != 0:
                    # Đảo ngược nếu DESC
                    if direction1 == 'DESC':
                        comparison = -comparison
                    return comparison
            
            return 0
        
        # Python 3 không có cmp parameter, dùng key function thay thế
        from functools import cmp_to_key
        sorted_records = sorted(records, key=cmp_to_key(sort_comparison))
        
        return self.browse([r.id for r in sorted_records])
    
    # @api.model
    # def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
    #     if ['id', '=', '0'] in domain or ['id', '=', '-1'] in domain:

    #         return {
    #             'length': 0,
    #             'records': [],
    #         }
    #     # Tìm kiếm không có order
    #     all_records = self.search_fetch(domain, specification.keys(), offset=offset, limit=limit, order=None)
    #     # Sắp xếp sau khi có kết quả
    #     if order:
    #         sorted_records = self._sort_records_by_order(all_records, order)
    #     else:
    #         sorted_records = all_records
        
    #     values_records = sorted_records.web_read(specification)
    #     return self._format_web_search_read_results(domain, values_records, offset, limit, count_limit)
    
    def _get_superbar_supported_types(self):
        return ['many2one', 'many2many', 'char', 'integer', 'float', 'monetary', 'selection', 'boolean', 'date', 'datetime']