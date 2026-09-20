import csv
import re
from pathlib import Path
from collections import Counter

# 1. Đường dẫn thư mục dữ liệu
D = Path('data/doi-tra-bao-hanh')

# 2. Đọc CSV và danh sách file MD
mds = sorted(D.glob('*.md'))

with open(D / 'sources.csv', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

csv_ids = [
    r['doc_id'].strip().strip('"').strip("'")
    for r in rows
    if r.get('doc_id') and r['doc_id'].strip()
]

md_ids = []
md_missing_doc_id = []

# 3. Đọc doc_id từ từng file MD
for p in mds:
    content = p.read_text(encoding='utf-8')

    # Cho phép:
    # doc_id: shopee-123
    # doc_id: "shopee-123"
    # doc_id: 'shopee-123'
    # và có khoảng trắng ở đầu dòng
    match = re.search(r'^\s*doc_id:\s*(.+?)\s*$', content, re.M)

    if match:
        doc_id = match.group(1).strip().strip('"').strip("'")
        md_ids.append(doc_id)
    else:
        md_missing_doc_id.append(p.name)

# 4. Kiểm tra chênh lệch
csv_set = set(csv_ids)
md_set = set(md_ids)

missing_md = csv_set - md_set
missing_csv = md_set - csv_set

# 5. Kiểm tra duplicate
csv_duplicates = [
    doc_id for doc_id, count in Counter(csv_ids).items()
    if count > 1
]

md_duplicates = [
    doc_id for doc_id, count in Counter(md_ids).items()
    if count > 1
]

# 6. In kết quả
print("--- KẾT QUẢ KIỂM TRA ---")
print("Tổng số dòng trong CSV:", len(csv_ids))
print("Tổng số file MD tìm thấy:", len(mds))
print()

print("ID chỉ có trong CSV nhưng THIẾU file MD:", missing_md)
print("ID có file MD nhưng THIẾU trong CSV:", missing_csv)
print()

print("doc_id bị trùng trong CSV:", csv_duplicates)
print("doc_id bị trùng trong MD:", md_duplicates)
print("File MD không có doc_id:", md_missing_doc_id)

# 7. Kết luận PASS / FAIL
passed = (
    len(csv_ids) == len(mds)
    and not missing_md
    and not missing_csv
    and not csv_duplicates
    and not md_duplicates
    and not md_missing_doc_id
)

print()
if passed:
    print("✅ PASS: CSV và Markdown khớp hoàn toàn.")
else:
    print("❌ FAIL: Có dữ liệu cần kiểm tra lại.")