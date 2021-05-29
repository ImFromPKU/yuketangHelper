from time import time, sleep
from random import random, randint

from ykt_api import (get_video_complete_stat,
                     get_video_length_info,
                     get_video_watch_rate,
                     post_video_heartbeat)
from config import Config


class Sq:
    sq: int = 0

    @classmethod
    def get(cls) -> int:
        cls.sq += 1
        return cls.sq

    @classmethod
    def clear(cls):
        cls.sq = 0


def timstap() -> int:
    return int(round(time() * 1000))


def pause(long: bool = True):
    if long:
        sleep_time = randint(6, 15) + random()
    else:
        sleep_time = randint(1, 3)+random()
    print(f"暂停 {sleep_time} s")
    sleep(sleep_time)


def watch(video_id: int, video_name: str, course_id: int, user_id: int, classroom_id: int, skuid: str):

    def gen_heart_data(et: str, cp: int, d: int) -> dict:
        print(f"心跳包类型：{et}")
        data = {
            "i": 5,
            "et": et,  # loadeddata
            "p": "web",
            "n": "sjy-cdn.xuetangx.com",  # ws
            "lob": "ykt",  # clouod4
            "cp": cp,
            "fp": 0,
            "tp": 0,
            "sp": 1,
            "ts": str(timstap()),
            "u": user_id,
            "uip": "",
            "c": course_id,
            "v": video_id,
            "skuid": skuid,
            "classroomid": str(classroom_id),
            "cc": str(video_id),
            "d": d,
            "pg": "2257747_149az",  # 4512143_tkqx
            "sq": Sq.get(),
            "t": "video"
        }
        return data

    print(f"开始尝试学习 {video_id}: {video_name}")

    video_length = get_video_length_info(classroom_id, video_id)
    print(f"视频长度：{video_length}")

    post_video_heartbeat({}, classroom_id)
    if_completed = get_video_complete_stat(
        course_id, user_id, classroom_id, video_id)
    if if_completed:
        print("已经学习完毕，跳过")
        pause(long=False)
        return
    else:
        print("尚未学习，现在开始自动学习")

    watch_time = 0
    watch_rate = 0
    heartrate = Config().heartrate
    completed = False
    no_progress_retry = 0
    while watch_rate != 1:
        heart_data = []
        if Sq.sq == 0:
            heart_data += [gen_heart_data("loadstart", 0, 0),
                           gen_heart_data("loadeddata", 0, video_length),
                           gen_heart_data("play", 0, video_length),
                           gen_heart_data("playing", 0, video_length)]
        for i in range(Config().heartbeat_pack_size):
            sleep(5)
            heart_data.append(gen_heart_data(
                "heartbeat", watch_time, video_length))
            watch_time += heartrate
            if watch_time >= video_length:
                completed = True
                break
        if completed:
            heart_data += [gen_heart_data("pause", video_length, video_length),
                           gen_heart_data("videoend", video_length, video_length)]
        post_video_heartbeat({"heart_data": heart_data}, classroom_id)

        tmp_rate = get_video_watch_rate(
            course_id, user_id, classroom_id, video_id)
        if tmp_rate is None:
            if no_progress_retry >= 5:
                print("一直无法获取进度信息，跳过此视频")
                return
            no_progress_retry += 1
            print(f"进度第 {no_progress_retry} 次获取失败，继续学习")
            continue
        watch_rate = tmp_rate
        print(f"远程记录的最后进度：{watch_rate * 100}% 本次观看时长远程记录: {watch_time}")

    print("学习完成！")
    Sq.clear()
    pause()
    return
