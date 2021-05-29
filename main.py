from ykt_api import get_courses, get_skuid, get_user_id, get_videos
from video import watch


if __name__ == "__main__":
    user_id = get_user_id()
    courses = get_courses()
    for index, value in enumerate(courses):
        print("编号："+str(index+1)+" 课名："+str(value["course_name"]))
    number = input("你想刷哪门课呢？请输入编号。输入 0 表示全部课程都刷一遍\n")
    if int(number) == 0:
        # 0 表示全部刷一遍
        for ins in courses:
            video_dic = get_videos(ins["course_name"], ins["classroom_id"])
            sku_id = get_skuid(int(ins["classroom_id"]))
            for video in video_dic.items():
                watch(video[0], video[1], int(ins["course_id"]),
                      user_id, int(ins["classroom_id"]), sku_id)
    else:
        # 指定序号的课程刷一遍
        number = int(number) - 1
        video_dic = get_videos(
            courses[number]["course_name"], courses[number]["classroom_id"])
        sku_id = get_skuid(int(courses[number]["classroom_id"]))
        for video in video_dic.items():
            watch(video[0], video[1], int(courses[number]["course_id"]),
                  user_id, int(courses[number]["classroom_id"]), sku_id)
