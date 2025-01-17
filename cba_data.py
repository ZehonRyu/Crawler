import base64
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import requests
import pandas as pd

def decrypt_data(s):
    aes = AES.new('uVayqL4ONKjFbVzQ'.encode("utf-8"), AES.MODE_ECB)
    bs = base64.b64decode(s)
    ming_bs = aes.decrypt(bs)
    ming_bs = unpad(ming_bs, 16)
    return ming_bs.decode("utf-8")

def send_request_with_payload(url, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Content-Type": "application/json"
    }
    if not kwargs:
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, data=json.dumps(kwargs))
    response.raise_for_status()
    return response.text

def map_fields_to_chinese(data):
    field_mapping = {
        "teamId": "球队ID",
        "playerId": "球员ID",
        "playerTimes": "球员出场次数",
        "position": "位置",
        "isColor": "是否主力",
        "type": "类型",
        "gameStart": "是否首发",
        "number": "球衣号码",
        "upTime": "上场时间",
        "cnAlias": "中文别名",
        "turnShare": "控球率",
        "turnShareSort": "控球率排序",
        "turnShareRank": "控球率排名",
        "trueShootingPercentage": "真实命中率",
        "trueShootingPercentageSort": "真实命中率排序",
        "trueShootingPercentageRank": "真实命中率排名",
        "assistsPercentage": "助攻率",
        "assistsPercentageSort": "助攻率排序",
        "assistsPercentageRank": "助攻率排名",
        "turnoversPercentage": "失误率",
        "turnoversPercentageSort": "失误率排序",
        "turnoversPercentageRank": "失误率排名",
        "stealsPercentage": "抢断率",
        "stealsPercentageSort": "抢断率排序",
        "stealsPercentageRank": "抢断率排名",
        "blockedPercentage": "盖帽数率",
        "blockedPercentageSort": "盖帽数率排序",
        "blockedPercentageRank": "盖帽数率排名",
        "reboundsOffensivePercentage": "进攻篮板率",
        "reboundsOffensivePercentageSort": "进攻篮板率排序",
        "reboundsOffensivePercentageRank": "进攻篮板率排名",
        "reboundsDefensivePercentage": "防守篮板率",
        "reboundsDefensivePercentageSort": "防守篮板率排序",
        "reboundsDefensivePercentageRank": "防守篮板率排名",
        "fieldGoalsAtRimPercentage": "篮下命中率",
        "fieldGoalsAtRimPercentageSort": "篮下命中率排序",
        "fieldGoalsAtRimPercentageRank": "篮下命中率排名",
        "fieldGoalsMidPercentage": "中距离命中率",
        "fieldGoalsMidPercentageSort": "中距离命中率排序",
        "fieldGoalsMidPercentageRank": "中距离命中率排名"
    }
    
    mapped_data = []
    for player in data:
        mapped_player = {field_mapping[k]: v for k, v in player.items()}
        mapped_data.append(mapped_player)
    
    return mapped_data

if __name__ == "__main__":
    url = "https://data-server.cbaleague.com/api/player-match-datas/advance-count"
    start_schedule_id = 100098300
    end_schedule_id = 100098411
    
    # 使用绝对路径并确保目录存在
    output_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, "data.xlsx")
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for schedule_id in range(start_schedule_id, end_schedule_id + 1):
            try:
                # 动态定义要发送的负载，并通过关键字参数传递
                response = send_request_with_payload(
                    url,
                    scheduleId=str(schedule_id)
                )

                origin_data = decrypt_data(response)
                data = json.loads(origin_data)
                
                # 映射字段到中文
                mapped_data = map_fields_to_chinese(data['homes'])
                
                # 将数据写入 Excel 文件的不同 sheet
                df = pd.DataFrame(mapped_data)
                df.to_excel(writer, sheet_name=str(schedule_id), index=False)
                print(f"Data for scheduleId {schedule_id} successfully written to {file_path}")
            except PermissionError:
                print(f"Permission denied when trying to write to {file_path}. Please check the file permissions.")
            except Exception as e:
                print(f"An error occurred for scheduleId {schedule_id}: {e}")

    print(f"All data successfully written to {file_path}")