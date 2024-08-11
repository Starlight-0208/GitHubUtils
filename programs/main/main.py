import re
import os
import json
import time
import datetime
import pandas
import requests

RES_DIR = f'{os.getcwd()}\\data'
rate_limit = False
interval = 1
retry: bool = False
retry_count:int = 3

# This is the filename list of Github-Ranking Markdown files
langs = ["ActionScript", "C", "CPP", "CSS", "CSharp", 
         "Clojure", "CoffeeScript", "DM", "Dart", "Elixir", 
         "Go", "Groovy", "HTML", "Haskell", "Java", "JavaScript", 
         "Julia", "Kotlin", "Lua", "MATLAB", "Objective-C", "PHP", 
         "Perl", "PowerShell", "Python", "R", "Ruby", "Rust", 
         "Scala", "Shell", "Swift", "TeX", "TypeScript", "Vim-script"]

failed_list = []

def process_func(raw_text: str):
    res = []
    for i in raw_text.split("\n\n")[2].split("\n")[2:]:
        line = i.strip().split("|")[1:-1]
        # name, link = getLink(line[1].strip())
        link = re.findall(r'\[(.*?)\]\((.*?)\)', line[1])[0][1]
        res.append({
            'rank': int(line[0].strip()),
            # 'name': name,
            'name': link.split('/')[-1],
            'author': link.split('/')[-2],
            'link': link,
            'star': int(line[2].strip()),
            'fork': int(line[3].strip()),
            'language': line[4].strip(),
            'issues': int(line[5].strip()),
            'description': line[6].strip(),
            'last_commit': line[7].strip()
        })
    return res

getData = lambda baseUrl: process_func(requests.get(baseUrl, timeout=10).text)

def nativeMode():
    for i in langs:
        start_time = time.perf_counter()
        print(f"Processing Language: {i}".ljust(60), end="")
        baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/{i}.md"
        try:
            ps = getData(baseUrl)
        except Exception:
            print("[FAILED]")
            failed_list.append(i)
            continue
        pandas.DataFrame(ps).to_csv(f'{RES_DIR}\\csv\\{i.lower}.csv', index=False)
        with open(f"{RES_DIR}\\json\\{i.lower()}.json", 'w', encoding='utf-8') as f:
            json.dump(ps, f, ensure_ascii=False)
            f.close()
        end_time = time.perf_counter()
        print(f"[OK] {end_time - start_time:.4f} seconds")
        if (rate_limit): time.sleep(interval)
    
    print(f"Processing Language: Top 100 Stars".ljust(60), end="")
    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-stars.md"
    try:
        ps = getData(baseUrl)
    except Exception as e:
        print("[FAILED]")
        failed_list.append("Top-100-stars")
        ps = []
    pandas.DataFrame(ps).to_csv(f"{RES_DIR}\\csv\\top-stars.csv", index=False)
    with open(f"{RES_DIR}\\json\\top-stars.json", 'w', encoding='utf-8') as f:
        json.dump(TopStars, f, ensure_ascii=False)
        f.close()
    end_time = time.perf_counter()
    if ps != []: print(f"[OK] {end_time - start_time:.4f} seconds")

    print(f"Processing Language: Top 100 Forks".ljust(60), end="")
    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-forks.md"
    try:
        ps = getData(baseUrl)
    except Exception as e:
        print("[FAILED]")
        failed_list.append("Top-100-forks")
        ps = []
    pandas.DataFrame(ps).to_csv(f"{RES_DIR}\\csv\\top-forks.csv", index=False)
    with open(f"{RES_DIR}\\json\\top-forks.json", 'w', encoding='utf-8') as f:
        json.dump(TopForks, f, ensure_ascii=False)
        f.close()
    end_time = time.perf_counter()
    if ps != []: print(f"[OK] {end_time - start_time:.4f} seconds")

def retry_func():
    for n in range(retry_count):
        for i in failed_list:
            print(f"Retrying... {n+1}/{retry_count}")
            start_time = time.perf_counter()
            print(f"Retrying Language: {i}".ljust(60), end="")
            baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/{i}.md"
            try:
                ps = getData(baseUrl)
            except Exception:
                print("[FAILED]")
                continue
            failed_list.remove(i)
            pandas.DataFrame(ps).to_csv(f'{RES_DIR}\\csv\\{i.lower}.csv', index=False)
            with open(f"{RES_DIR}\\json\\{i.lower()}.json", 'w', encoding='utf-8') as f:
                json.dump(ps, f, ensure_ascii=False)
                f.close()
            end_time = time.perf_counter()
            print(f"[OK] {end_time - start_time:.4f} seconds")
        if len(failed_list) == 0: break


if __name__ == "__main__":
    nativeMode()
    print(f"failed: {' '.join(failed_list)}")
    retry_func()