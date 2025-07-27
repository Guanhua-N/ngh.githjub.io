import json

def load_json_data(filename):
    """读取JSON文件内容"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# namelist = ['会议/期刊完整名称', '会议/期刊简称']
def format_entries(entry,namelist):
    type = entry['type']
    if(type=='I'):
        return ""
    no = entry['no']
    authors = entry['authors']
    title = entry['title']
    year = entry['year']
    if(year==""):
        raise ValueError(f"[错误] 记录{entry}的年份为空，请检查数据。")
    totalNmae_venue = namelist[0]
    if(totalNmae_venue=="unknown"):
        raise ValueError(f"[错误] 记录{entry}的会议/期刊完全名称为 'unknown'，请检查数据。")
    abbreviation_venue = namelist[1]
    if(abbreviation_venue=="unknown"):
        abbreviation_venue = ""
    else:
        if(type == 'C'):
            abbreviation_venue = f"({abbreviation_venue} {year})"
        else:
            abbreviation_venue = f"({abbreviation_venue})"

    vol = entry['vol']
    if(vol!=""):
        vol = f",Vol.{vol}"

    num = entry['num']
    if(num!=""):
        if(vol==""):
            raise ValueError(f"[错误] 记录{entry}的num非空但vol为空 ，请检查数据。")
        num = f"({num})"
        
    start_page = entry['start_page']
    if(start_page!=""):
        start_page = f",{year}:{start_page}"
    end_page = entry['end_page']
    if(end_page!=""):
        if(start_page!=""):
            end_page = f"-{end_page}"
        else:
            raise ValueError(f"[错误] 记录{entry}的end_page非空但start_page为空 ，请检查数据。")
        
    line = f'''
<div class="pub-entry">
<div class="pub-label">[{type}{no}]</div>
<div class="pub-text">{authors}. {title}. <i>{totalNmae_venue} {abbreviation_venue}</i>{vol}{num}{start_page}{end_page}</div>
</div>
            '''
    
    return line

result = []

def main():
    # JSON文件路径
    risProcess = 'risProcess.json'
    manualMap = 'manualMap.json'

    risProcess_entry = load_json_data(risProcess)
    manualMap_entry = load_json_data(manualMap)
    last_year = ""
    for i, entry in enumerate(risProcess_entry, start=1):
        if(entry['year'] != last_year):
            result.append(f"## {entry['year']}")
            last_year = entry['year']
        namelist = manualMap_entry[entry["venue"]]
        line = format_entries(entry,namelist)
        result.append(line)


    
    with open("result.txt", "w", encoding="utf-8") as f:
        for entry in result:
            f.write(f"{entry}\n\n")

if __name__ == '__main__':
    main()