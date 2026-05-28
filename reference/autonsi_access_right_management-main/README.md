# Hướng dẫn tìm channel từ partner id

Để tìm channel từ một partner (ví dụ: outsourcing company 1), thực hiện các bước sau:

1. Lấy đối tượng partner theo partner id (ví dụ: `partner = self.env['res.partner'].browse(partner_id)`).
2. Lấy trường `channel_ids` từ partner này.
3. Lọc các channel có `is_auto_channel = True` và `channel_type = 'group'`.

Ví dụ code Odoo:

```python
partner = self.env['res.partner'].browse(partner_id)
channels = partner.channel_ids.filtered(lambda c: c.is_auto_channel and c.channel_type == 'group')
```

- `channels` là danh sách các channel thỏa mãn điều kiện. main branch

dev branch