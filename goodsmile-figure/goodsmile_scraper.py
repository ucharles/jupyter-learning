import requests
from bs4 import BeautifulSoup
import json
import sys, os
import re
from tqdm import tqdm

start = 2010
end = 2011


def figure_release_list():
    try:
        years = list(range(start, end))
        months = []
        figure_release_list = []
        temp_dic = {}

        for year in years:
            url = "https://www.goodsmile.info/ja/products/announced/" + str(year)

            # Send a GET request to the URL and retrieve the page content
            response = requests.get(url)

            # Create a BeautifulSoup object to parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the table element on the page (you may need to inspect the HTML source
            # of the web page to determine the table's structure and class or ID)

            current_date = soup.find_all("h3", class_="current-date")

            # shimelist 제외
            current_date = [
                current_date
                for current_date in current_date
                if "shimelist" not in "".join(current_date["class"])
            ]

            # 안내 월 리스트 작성
            for i in current_date:
                months.append(
                    i.get_text().strip().replace("\n", "").replace("案内商品", "")
                )

            # 안내 월별 리스트 추출
            hit_list = soup.find_all("div", class_="hitList")

            month_count = 0
            for hit in hit_list:
                hit_items = hit.find_all("div", class_="hitItem")

                # shimeproduct 제외
                hit_items = [
                    hit_items
                    for hit_items in hit_items
                    if "shimeproduct" not in "".join(hit_items["class"])
                ]
                # 안내 월 출력
                if len(hit_items) > 0:
                    print(months[month_count])
                    y, m = months[month_count].strip().split("年")
                    m = m.replace("月", "")
                    announce_month = y + "/" + m.zfill(2)
                    month_count += 1

                hit_items_len = len(hit_items)
                for hit_item in tqdm(
                    hit_items, total=hit_items_len, desc="Processing", ncols=80
                ):
                    temp_dic.update({"案内年月": announce_month})
                    temp_dic.update(figure_info(hit_item.find("a")["href"]))
                    figure_release_list.append(temp_dic)
                    temp_dic = {}
                # 월 단위로 출력
                write_file(figure_release_list)

            # 연 단위 출력 완료 후 초기화
            months = []
    except Exception as e:
        print(url, e)


def figure_info(url):
    try:
        session = requests.Session()
        cookies = {"age_verification_ok": "true"}
        session.cookies.update(cookies)
        # Send a GET request to the URL and retrieve the page content
        response = session.get(url)

        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        item_num = soup.find("div", class_="itemNum")

        detail = soup.find_all("div", class_="detailBox")

        image = soup.find("a", class_="imagebox")

        if detail is not None:
            for detail in detail:
                dl_tag = detail.find("dl")
                if dl_tag is None:
                    continue
                key_value_dict = {}

                key_value_dict["番号"] = (
                    item_num.get_text() if item_num is not None else None
                )

                key_value_dict["詳細URL"] = url

                key_value_dict["画像"] = (
                    "https:" + image["href"] if image is not None else None
                )

                # Iterate over the <dt> and <dd> pairs
                for dt_tag, dd_tag in zip(dl_tag.find_all("dt"), dl_tag.find_all("dd")):
                    # Extract the text content of <dt> and <dd>
                    key = dt_tag.get_text(strip=True)
                    value = dd_tag.get_text(strip=True)

                    # Store the key-value pair in the dictionary
                    if "※" in key:
                        key_value_dict["etc"] = key
                    else:
                        key_value_dict[key] = value.replace("  ", "").replace("\n", "")

                key_value_dict["価格"] = (
                    re.sub(r"\D", "", key_value_dict["価格"])
                    if "価格" in key_value_dict
                    else None
                )
                return key_value_dict
            return {}
        else:
            return {}
    except Exception as e:
        print(url, e)

    # Print the key-value dictionary
    # for key, value in key_value_dict.items():
    #     print(key + ": " + str(value))


def write_file(list):
    fo = open("product_list_" + str(start) + ".json", "w", encoding="utf-8")
    fo.write(json.dumps(list, ensure_ascii=False))
    # fo.writelines(str(list))
    fo.close()


figure_release_list()
