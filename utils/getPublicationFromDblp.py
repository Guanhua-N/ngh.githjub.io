import requests
from rispy import load
import re
import io

# === 设置 DBLP PID ===
pid = "96/2572"
url = f"https://dblp.org/pid/{pid}.ris"

# === 下载 RIS 数据 ===
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"❌ 下载失败，HTTP 状态码: {response.status_code}")

ris_data_raw = response.text

# === 跳过开头非 RIS 数据 ===
ris_lines = ris_data_raw.splitlines()
for i, line in enumerate(ris_lines):
    if line.strip().startswith("TY  -"):
        ris_clean = "\n".join(ris_lines[i:])
        break
else:
    raise Exception("❌ 未找到合法 RIS 开头 (TY  -)")

# === 使用 rispy 解析 ===
entries = load(io.StringIO(ris_clean))

# 调试打印，查看第一条的字段结构
print(entries[0])

# === 分类存储 ===
journals = []
confs = []

def format_authors(author_list):
    return ", ".join(author_list)

def format_entry(entry):
    authors = format_authors(entry.get("authors", []))
    title = entry.get("title", "").strip(". ")
    year = entry.get("year", "")
    journal = entry.get("journal", "")
    booktitle = entry.get("booktitle", "")
    doi = entry.get("doi", "")
    url = entry.get("url", "")

    title = re.sub(r"{|}", "", title)
    venue = journal or booktitle or "Unknown Venue"
    link = f" [DOI](https://doi.org/{doi})" if doi else f" [Link]({url})" if url else ""

    return f"{authors}.  \n*{title}*.  \n**{venue}**, {year}.{link}"

for entry in entries:
    # 试用 'type_of_reference' 或 'TY' 字段判断类型
    typ = entry.get("type_of_reference", "").lower()
    if not typ:
        typ = entry.get("TY", "").lower()
    # RIS常用类型
    if typ == "jour":  # 期刊
        journals.append(format_entry(entry))
    elif typ in ["conf", "proceedings", "cpaper"]:  # 会议，常见的RIS会议类型
        confs.append(format_entry(entry))
    else:
        # 可以打印不识别的类型方便调试
        print(f"未识别类型: {typ}")

# === 输出 Markdown 文件 ===
with open("publications.txt", "w", encoding="utf-8") as f:
    f.write("# Publications\n\n")
    f.write("## Journal Articles\n\n")
    for i, pub in enumerate(journals, 1):
        f.write(f"[j{i}] {pub}\n\n")
    f.write("## Conference Papers\n\n")
    for i, pub in enumerate(confs, 1):
        f.write(f"[c{i}] {pub}\n\n")

print(f"✅ 成功生成 publications.md，包含 {len(journals)} 篇期刊论文 和 {len(confs)} 篇会议论文。")
