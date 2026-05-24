# youngmin-odoo-modules
Hiếu tập làm vibe code Odoo 17 custom modules for Youngmin Hi-Tech Vina
# Youngmin Odoo Modules

Custom Odoo 17 modules cho **Youngmin Hi-Tech Vina**  
Công ty sản xuất điện tử Hàn Quốc tại Việt Nam  
Domain: `ym.autovina.cloud`

---

## Modules

| Module | Tên hiển thị | Mô tả | Status |
|--------|-------------|-------|--------|
| `autonsi_standard_youngmin` | Standard Information | Master data: Project, Process, Common | 🚧 In Progress |
| `autonsi_ams` | Asset Management | Quản lý tài sản, lịch sử sửa chữa | ⬜ Planned |
| `autonsi_mms_youngmin` | Manufacturing MMS | Lệnh SX: MMO, PMO, MO, Production | ⬜ Planned |
| `autonsi_qms_youngmin` | Quality Management | Biểu mẫu QC, lịch sử kiểm tra | ⬜ Planned |
| `autonsi_wms_ym` | Warehouse Management | Pallet, receiving, shipping | ⬜ Planned |

---

## Yêu cầu môi trường

```
Odoo     : 17.0 (build 20250428)
Python   : 3.10+
PostgreSQL: 16.6
OS       : Windows 10/11 hoặc Ubuntu 22.04
```

---

## Setup lần đầu

### Bước 1 — Clone repo về máy

```bash
cd C:\odoo17\custom
git clone https://github.com/your-username/youngmin-odoo-modules.git
```

Sau khi clone xong, cấu trúc thư mục sẽ là:
```
C:\odoo17\
├── odoo\                          ← Odoo source code (đã có sẵn)
│   └── addons\                    ← Odoo standard modules
└── custom\
    └── youngmin-odoo-modules\     ← Repo này ← bạn vừa clone
        ├── autonsi_standard_youngmin\
        ├── autonsi_ams\
        └── docs\
```

---

### Bước 2 — Cấu hình addons_path trong odoo.conf

`odoo.conf` là file cấu hình của Odoo — nó cần biết thư mục nào chứa custom modules.

**Tìm file odoo.conf** (thường ở một trong các vị trí sau):
```
Windows : C:\odoo17\server\odoo.conf
          C:\Program Files\Odoo 17\server\odoo.conf
Ubuntu  : /etc/odoo/odoo.conf
          ~/odoo17/odoo.conf
```

**Mở file và tìm dòng `addons_path`**, sửa thành:

```ini
[options]
; addons_path = đường dẫn đến thư mục chứa modules
; Dùng dấu phẩy để thêm nhiều thư mục
; Odoo đọc từ trái sang phải → custom modules đặt SAU standard

addons_path = C:\odoo17\odoo\addons,C:\odoo17\custom\youngmin-odoo-modules

; Các cài đặt khác
db_host = localhost
db_port = 5432
db_name = youngmin_dev
db_user = odoo
db_password = odoo
```

> ⚠️ **Lưu ý đường dẫn Windows:** dùng dấu `/` hoặc `\\` đều được  
> ✅ `C:/odoo17/custom/youngmin-odoo-modules`  
> ✅ `C:\\odoo17\\custom\\youngmin-odoo-modules`  
> ❌ `C:\odoo17\custom\youngmin-odoo-modules` (1 dấu `\` có thể gây lỗi)

---

### Bước 3 — Khởi động lại Odoo

```bash
# Windows (chạy trong terminal với quyền admin)
net stop odoo-server-17
net start odoo-server-17

# Hoặc restart service trong Services.msc
# Tìm "Odoo Server 17" → Right click → Restart
```

---

### Bước 4 — Cài đặt module trong Odoo UI

1. Vào **Settings** → bật **Developer Mode**  
   (URL: `http://localhost:8069/web?debug=1`)

2. Vào **Apps** → bấm **Update Apps List**  
   (menu Apps → nút "Update" góc trên)

3. Tìm `Standard Information` → bấm **Install**

> 💡 Mỗi lần thêm module mới vào repo → phải **Update Apps List** lại  
> 💡 Mỗi lần sửa code Python → phải **restart Odoo service**  
> 💡 Mỗi lần sửa XML views → có thể chỉ cần **Upgrade module** (không cần restart)

---

## Workflow phát triển hàng ngày

```bash
# 1. Pull code mới nhất
git pull

# 2. Sửa code trong VS Code

# 3. Commit thay đổi
git add .
git commit -m "feat: add standard.project form view"
git push

# 4. Nếu sửa Python → restart Odoo
# Nếu sửa XML → Upgrade module trong UI
```

---

## Upgrade module sau khi sửa code

**Cách 1 — Qua UI (dễ nhất):**
```
Apps → Tìm module → nút "⋮" → Upgrade
```

**Cách 2 — Qua command line (nhanh hơn):**
```bash
python odoo-bin -d youngmin_dev -u autonsi_standard_youngmin --stop-after-init
```

**Cách 3 — Trong odoo.conf thêm:**
```ini
; Tự động upgrade khi restart (chỉ dùng khi dev)
upgrade_db = True
```

---

## Cấu trúc thư mục mỗi module

```
autonsi_standard_youngmin/
├── __manifest__.py     ← Thông tin module (tên, version, dependencies)
├── __init__.py         ← Import models
├── models/
│   ├── __init__.py     ← Import từng model file
│   ├── standard_project.py
│   ├── standard_process.py
│   └── standard_common.py
├── views/
│   ├── standard_project_views.xml   ← Tree + Form view
│   ├── standard_process_views.xml
│   ├── standard_common_views.xml
│   └── menu_views.xml               ← Menu + Action
├── security/
│   ├── security.xml         ← Định nghĩa groups/roles
│   └── ir.model.access.csv  ← Phân quyền CRUD cho từng model
└── data/
    └── demo_data.xml        ← Dữ liệu mẫu (optional)
```

---

## Tài liệu ERD

Toàn bộ sơ đồ database nằm trong thư mục `docs/erd/`:

| File | Nội dung |
|------|---------|
| `youngmin_MASTER_ERD.drawio` | Toàn bộ kiến trúc hệ thống (50+ bảng) |
| `youngmin_business_spine_erd.drawio` | Business Spine: SO→MRP→Picking→Invoice |
| `youngmin_qms_erd.drawio` | Quality Management System |
| `youngmin_wms_erd.drawio` | Warehouse Management System |
| `youngmin_ams_erd.drawio` | Asset Management System |
| `youngmin_mrp_production_deep_v3.drawio` | MMS hierarchy: MMO→PMO→MO→Production |

Mở bằng: [app.diagrams.net](https://app.diagrams.net) (miễn phí, không cần cài)

---

## Troubleshooting

**Module không hiện trong Apps list?**
```
→ Kiểm tra addons_path trong odoo.conf có đúng đường dẫn không
→ Bấm "Update Apps List" chưa?
→ Kiểm tra __manifest__.py có lỗi syntax không
```

**Lỗi "Module not found" khi import?**
```
→ Kiểm tra __init__.py đã import đúng chưa
→ Restart Odoo service
```

**View không cập nhật sau khi sửa XML?**
```
→ Upgrade module (không cần restart)
→ Xóa cache browser (Ctrl+F5)
```

---

## Liên hệ

- Developer: [Tên bạn]
- Email: [email]
- Odoo server: ym.autovina.cloud
