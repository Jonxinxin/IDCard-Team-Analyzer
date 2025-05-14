import datetime
import json
import csv

# 1. 加载地址码 → 城市名 映射
def load_address_codes(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    address_map = {}
    for item in data['T_Location']:
        code = item.get("bm", "").strip()
        name = item.get("dq") or f"{item.get('province', '')}{item.get('qy', '')}"
        if code:
            address_map[code] = name
    return address_map

# 2. 提取身份证信息
def get_info_from_id(id_number, address_map):
    address_code = id_number[:6]
    city = address_map.get(address_code, "未知地址")

    birth_year = int(id_number[6:10])
    birth_month = int(id_number[10:12])
    birth_day = int(id_number[12:14])
    birthday = datetime.date(birth_year, birth_month, birth_day)

    today = datetime.date.today()
    age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))

    gender = "男" if int(id_number[16]) % 2 == 1 else "女"

    return birthday.strftime("%Y-%m-%d"), age, gender, city

# 3. 读取人员名单
def process_team_file(team_file, address_map):
    results = []
    with open(team_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    pairs = content.split()
    for pair in pairs:
        try:
            name, id_number = pair.split("----")
            birthday, age, gender, city = get_info_from_id(id_number, address_map)
            results.append({
                "姓名": name,
                "身份证号": id_number,
                "出生年月": birthday,
                "年龄": age,
                "性别": gender,
                "城市": city
            })
        except Exception as e:
            print(f"跳过错误数据：{pair}，错误原因：{e}")
    return results

# 4. 排序交互逻辑（年龄为正序/倒序）
def ask_sort_and_sort(results):
    print("\n是否需要对结果进行排序？")
    choice = input("输入 Y 进行排序，或直接回车跳过：").strip().lower()

    if choice != 'y':
        return results

    print("\n请选择排序方式：")
    print("1. 根据年龄排序")
    print("2. 根据性别排序（女在前）")
    print("3. 根据城市排序（拼音顺序）")
    sort_option = input("请输入选项编号（1/2/3）：").strip()

    if sort_option == "1":
        order = input("年龄排序方式：输入 A 从小到大，输入 D 从大到小（默认 A）：").strip().upper()
        reverse = (order == 'D')
        results.sort(key=lambda x: x["年龄"], reverse=reverse)

    elif sort_option == "2":
        results.sort(key=lambda x: x["性别"])

    elif sort_option == "3":
        results.sort(key=lambda x: x["城市"])

    else:
        print("无效选项，跳过排序。")

    return results

# 5. 输出CSV文件（含身份证号）
def save_to_csv(results, output_file="结果.csv"):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["姓名", "身份证号", "出生年月", "年龄", "性别", "城市"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ 成功导出：{output_file}")

# 6. 主程序
if __name__ == "__main__":
    address_file = "T_Location_202206181755.json"
    team_file = "card.txt"

    address_map = load_address_codes(address_file)
    results = process_team_file(team_file, address_map)

    results = ask_sort_and_sort(results)
    save_to_csv(results)
