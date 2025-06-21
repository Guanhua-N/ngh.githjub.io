import requests
from rispy import load
import re
import io
import json
from titlecase import titlecase

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
with open("risWithoutPreprocess.json", "w", encoding="utf-8") as f:
    for entry in entries:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# === 分类存储 ===
jour_num = 0
conf_num = 0
other_num = 0

# 用于存储所有期刊和会议的 venue
venues_list = []

# 用于存储处理后的 JSON 格式的条目
json_entries = []


# === 辅助函数 ===

# 格式化作者列表
def format_authors(authors_list):
    formatted_authors = []
    for author in authors_list:
        # author 形如 "姓, 名"
        parts = author.split(",")
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            formatted_authors.append(f"{first_name} {last_name}")
        else:
            # 万一格式不标准，直接保留原字符串
            formatted_authors.append(author.strip())
    return ", ".join(formatted_authors)
# 格式化年份
def format_year(year_str):
    match = re.match(r"(\d{4})", year_str)
    if match:
        return match.group(1)
    else:
        return ""  # 找不到年份就返回空字符串
# 格式化论文类型
def format_type(typ):
    if typ == "JOUR":
        return "J"
    elif typ == "CPAPER":
        return "C"
    else:
        return "I"
    
# 格式化标题
def format_title(title):
    return titlecase(title)

# 获取会议/期刊名称
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

for entry in entries:
    # 收集所有 venue
    venue = get_venue(entry)
    if venue:
        venues_list.append(venue)
# 输出所有 venue 到文件中
with open("venues.txt", "w", encoding="utf-8") as f:
    for venue in venues_list:
        f.write(f"{venue}\n")

# === 遍历所有条目，根据类型分类 ===
for entry in entries:
    # 用 'type_of_reference'判断是期刊还是会议
    typ = entry.get("type_of_reference", "")
    # RIS常用类型
    if typ == "JOUR":  # 期刊
        jour_num+=1
    elif typ == "CPAPER":  # 会议
        conf_num+=1
    else:
        other_num+=1

# === 生成并输出处理后的文件 ===
junm=0
cnum=0
inum=0
for entry in entries:
    if entry.get("type_of_reference", "") == "JOUR":
        entry["no"] = jour_num-junm
        junm += 1
    elif entry.get("type_of_reference", "") == "CPAPER":
        entry["no"] = conf_num-cnum
        cnum += 1
    else:
        entry["no"] = other_num-inum
        inum += 1
    json_entry = {
        "type": format_type(entry.get("type_of_reference", "")),
        "no": entry.get("no", -1),  # 使用之前计算的编号
        "venue": get_venue(entry),
        "authors": format_authors(entry.get("authors", [])),
        "title": format_title(entry.get("title", "").strip(". ")),
        "vol": entry.get("volume", ""),
        "num": entry.get("number", ""),
        "start_page": entry.get("start_page", ""),
        "end_page": entry.get("end_page", ""),
        "year": format_year(entry.get("year", "")),
        "doi": entry.get("doi", ""),
        "urls": entry.get("urls", []),
    }
    json_entries.append(json_entry)

with open("risProcess.json", "w", encoding="utf-8") as f:
    json.dump(json_entries, f, indent=2, ensure_ascii=False)

print(f"✅ 成功生成 risProcess.json 包含 {jour_num} 篇期刊论文 和 {conf_num} 篇会议论文，以及 {other_num} 篇其他论文")
print(f"✅ 已生成 risProcess.json 共 {len(json_entries)} 篇论文。")

"""
# 示例输出格式
{
    "type": 会议/期刊/其他
    "no":改论文在对应type中的编号,
    "venue": 会议/期刊名称,
    "authors": string格式的作者列表,
    "title": 论文名,
    "vol": 期刊卷号,
    "num": 期刊期号,
    "start_page": ,
    "end_page": ,
    "year": 年份,
    "doi": "10.1109/ICPADS47876.2019.00017",
    "urls": [
      "https://doi.org/10.1109/ICPADS47876.2019.00017",
      ...
    ]
}

"""
