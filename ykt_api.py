from requests import get, post
import re
from typing import List, Dict
import json
from time import sleep

from config import Config


headers = {
    "classroom-id": "3029924",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': f'csrftoken={Config().csrftoken}; sessionid={Config().sessionid}; university_id={Config().uni_id}; platform_id=3; user_role=-1',
    "dnt": "1",
    "referer": f"https://{Config().ykt_addr}/v2/web/index",
    'x-csrftoken': Config().csrftoken,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Microsoft Edge\";v=\"90\"",
    'university-id': str(Config().uni_id),
    "uv-id": str(Config().uni_id),
    'xtbz': 'ykt',
    "x-client": "web",
    "xt-agent": "web"
}


def classroom_headers(classroom_id: int) -> Dict[str, str]:
    try:
        type(eval("get_hw_header"))
    except:
        c_header = headers.copy()
    c_header["classroom-id"] = str(classroom_id)
    return c_header


def get_user_id() -> int:
    user_id_url = f"https://{Config().ykt_addr}/v/course_meta/user_info"
    id_response = get(url=user_id_url, headers=headers)
    try:
        user_id = int(re.search(r'"user_id":(.+?)[,}]+',
                                id_response.text).group(1).strip())
    except:
        raise Exception("获取 user_id 失败")
    return user_id


def get_courses() -> List[Dict]:
    courses = []
    get_classroom_id = f"https://{Config().ykt_addr}/v2/api/web/courses/list?identity=2"
    classroom_id_response = get(url=get_classroom_id, headers=headers)
    try:
        for ins in json.loads(classroom_id_response.text)["data"]["list"]:
            courses.append({
                "course_name": ins["course"]["name"],
                "classroom_id": ins["classroom_id"],
                "course_id": ins["course"]["id"]
            })
    except Exception as e:
        raise Exception("获取 classroom_id 失败，请重试")
    return courses


def get_skuid(classroom_id: int) -> str:
    get_homework_ids = f"https://{Config().ykt_addr}/c27/online_courseware/xty/kls/pub_news/625/"
    get_hw_header = classroom_headers(classroom_id)
    homework_ids_response = get(url=get_homework_ids, headers=get_hw_header)
    homework_json = json.loads(homework_ids_response.text)
    return homework_json["data"]["s_id"]


def get_videos(course_name: str, classroom_id: int) -> Dict[int, str]:
    leaf_type = {
        "video": 0,
        "homework": 6,
        "exam": 5,
        "recommend": 3,
        "discussion": 4
    }

    get_homework_ids = f"https://{Config().ykt_addr}/c27/online_courseware/xty/kls/pub_news/625/"
    get_hw_header = classroom_headers(classroom_id)
    homework_ids_response = get(url=get_homework_ids, headers=get_hw_header)
    homework_json = json.loads(homework_ids_response.text)
    homework_dic = {}
    leaf_lists = []
    try:
        for j in homework_json["data"]["content_info"]:
            if "section_list" in j:
                for z in j["section_list"]:
                    if "leaf_list" in z:
                        leaf_lists.append(z["leaf_list"])
            if "leaf_list" in j:
                leaf_lists.append(j["leaf_list"])
        for leaf_list in leaf_lists:
            for leaf in leaf_list:
                if leaf["leaf_type"] == leaf_type["video"]:
                    homework_dic[leaf["id"]] = leaf["title"]
        print(course_name+" 共有 "+str(len(homework_dic))+" 个作业")
        return homework_dic
    except:
        raise Exception("获取作业列表失败，请重试")


def get_video_length_info(classroom_id: int, video_id: int) -> int:
    video_headers = classroom_headers(classroom_id)
    length_url = f"https://{Config().ykt_addr}/mooc-api/v1/lms/learn/leaf_info/{classroom_id}/{video_id}/"
    length_info = get(url=length_url, headers=video_headers)
    try:
        video_length = json.loads(length_info.text)[
            "data"]["content_info"]["media"]["duration"]
    except:
        raise Exception("获取视频长度错误！")
    return int(video_length)


def get_video_complete_stat(course_id: int, user_id: int, classroom_id: int, video_id: int) -> int:
    video_headers = classroom_headers(classroom_id)
    get_url = f"https://{Config().ykt_addr}/video-log/get_video_watch_progress/?cid={course_id}&user_id={user_id}&classroom_id={classroom_id}&video_type=video&vtype=rate&video_id={video_id}&snapshot=1&term=latest&uv_id={Config().uni_id}"
    progress = get(url=get_url, headers=video_headers)
    if_completed = 0
    progress = json.loads(progress.text)
    try:
        if_completed = progress["data"][str(video_id)]["completed"]
    except:
        print("未能成功获取学习完成情况")
    return if_completed


def get_video_watch_rate(course_id: int, user_id: int, classroom_id: int, video_id: int) -> float:
    video_headers = classroom_headers(classroom_id)
    get_url = f"https://{Config().ykt_addr}/video-log/get_video_watch_progress/?cid={course_id}&user_id={user_id}&classroom_id={classroom_id}&video_type=video&vtype=rate&video_id={video_id}&snapshot=1&term=latest&uv_id={Config().uni_id}"
    progress = get(url=get_url, headers=video_headers)
    try:
        rate = float(re.search(r'"rate":(.+?)[,}]', progress.text).group(1))
    except:
        print("获取进度信息失败")
        return None
    return rate


def post_video_heartbeat(heartbeat: Dict[str, List], classroom_id: int):
    video_headers = classroom_headers(classroom_id)
    url = f"https://{Config().ykt_addr}/video-log/heartbeat/"
    r = post(url=url, headers=video_headers, json=heartbeat)
    try:
        delay_time = re.search(
            r'Expected available in(.+?)second.', r.text).group(1).strip()
        print("由于网络阻塞，阻塞" + str(delay_time) + "s")
        sleep(float(delay_time) + 0.5)
        print("恢复工作")
        r = post(url=url, headers=video_headers, json=heartbeat)
    except:
        pass
    if not json.loads(r.text) == {}:
        raise Exception(f"心跳错误！{r.text}")
