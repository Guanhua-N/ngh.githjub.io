import requests
from rispy import load
import re
import io
import json

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

# 生成未经处理的ris文件，查看字段结构
with open("publications_preprocess.txt", "w", encoding="utf-8") as f:
    for entry in entries:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# === 分类存储 ===
journals = []
confs = []
others = []


# === 辅助函数 ===
def format_authors(authors):
    if isinstance(authors, list):
        return ", ".join(authors)
    else:
        return authors

def get_venue(entry):
    # 尝试直接字段
    for key in ["journal_name", "booktitle", "t2"]:
        if key in entry:
            return entry[key]

    # 从 unknown_tag 中提取 BT 或 JO
    unknown = entry.get("unknown_tag", {})
    for tag in ["BT", "JO"]:
        venue = unknown.get(tag)
        if venue:
            return venue[0] if isinstance(venue, list) else venue

    return "Unknown Venue"

def format_entry(entry):
    authors = format_authors(entry.get("authors", entry.get("AU", [])))
    title = entry.get("title", entry.get("TI", "")).strip(". ")
    year = entry.get("year", entry.get("PY", ""))
    venue = get_venue(entry)
    doi = entry.get("doi", entry.get("DO", ""))
    url = entry.get("url", entry.get("UR", ""))

    title = re.sub(r"[{}]", "", title)
    link = f" [DOI](https://doi.org/{doi})" if doi else f" [Link]({url})" if url else ""

    return f"{authors}.  \n*{title}*.  \n**{venue}**, {year}.{link}"


# === 遍历所有条目，根据类型分类 ===
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
        others.append(format_entry(entry))

# === 输出 Markdown 文件 ===
with open("publications.txt", "w", encoding="utf-8") as f:
    f.write("# Publications\n\n")
    
    f.write("## Journal Articles\n\n")
    for i, pub in enumerate(journals, 1):
        f.write(f"[j{i}] {pub}\n\n")
        
    f.write("## Conference Papers\n\n")
    for i, pub in enumerate(confs, 1):
        f.write(f"[c{i}] {pub}\n\n")
        
    f.write("## Other Publications\n\n")
    for i, pub in enumerate(others, 1):
        f.write(f"[i{i}] {pub}\n\n")

print(f"✅ 成功生成 publications.txt，包含 {len(journals)} 篇期刊论文 和 {len(confs)} 篇会议论文，以及 {len(others)} 篇其他论文")
