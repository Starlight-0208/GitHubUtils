import re
import os
import json
import time
import datetime
import pandas
import requests

RES_DIR = f'{os.getcwd()}\\data'
useRawMode = False
rate_limit = False
interval = 1

# This is the filename list of Github-Ranking Markdown files
langs = ["ActionScript", "C", "CPP", "CSS", "CSharp", 
         "Clojure", "CoffeeScript", "DM", "Dart", "Elixir", 
         "Go", "Groovy", "HTML", "Haskell", "Java", "JavaScript", 
         "Julia", "Kotlin", "Lua", "MATLAB", "Objective-C", "PHP", 
         "Perl", "PowerShell", "Python", "R", "Ruby", "Rust", 
         "Scala", "Shell", "Swift", "TeX", "TypeScript", "Vim-script"]

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
        baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/{i}.md"
        ps = getData(baseUrl)
        print(f"Processing Language: {i}".ljust(60), end="")
        pandas.DataFrame(ps).to_csv(f'{RES_DIR}\\csv\\{i.lower}.csv')
        with open(f"{RES_DIR}\\json\\{i.lower()}.json", 'w', encoding='utf-8') as f:
            json.dump(ps, f, ensure_ascii=False)
            f.close()
        end_time = time.perf_counter()
        print(f"[OK] {end_time - start_time:.4f} seconds")
        if (rate_limit): time.sleep(interval)
    
    print(f"Processing Language: {i}".ljust(60), end="")
    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-stars.md"
    TopStars = pandas.DataFrame(baseUrl)
    with open(f"{RES_DIR}\\json\\top-stars.json", 'w', encoding='utf-8') as f:
        json.dump(TopStars, f, ensure_ascii=False)
        f.close()
    end_time = time.perf_counter()
    print(f"[OK] {end_time - start_time:.4f} seconds")

    print(f"Processing Language: {i}".ljust(60), end="")
    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-forks.md"
    TopForks = pandas.DataFrame(baseUrl)
    with open(f"{RES_DIR}\\json\\top-forks.json", 'w', encoding='utf-8') as f:
        json.dump(TopForks, f, ensure_ascii=False)
        f.close()
    end_time = time.perf_counter()
    print(f"[OK] {end_time - start_time:.4f} seconds")

def dictMode(): 
    resultSet = {}
    for i in langs:
        baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/{i}.md"
        ps = getData(baseUrl)
        print(f"Processing Language: {i}".ljust(60), end="")
        resultSet[i] = ps
        print("[OK]")
        if (rate_limit): time.sleep(interval)
    

    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-stars.md"
    ps = getData(baseUrl)
    resultSet["TopStars"] = ps
    end_time = time.perf_counter()
    print(f"[OK] {end_time - start_time:.4f} seconds")

    print(f"Processing Language: {i}".ljust(60), end="")
    start_time = time.perf_counter()
    baseUrl = f"https://github.com/EvanLi/Github-Ranking/raw/master/Top100/Top-100-forks.md"
    ps = getData(baseUrl)
    resultSet["TopForks"] = ps
    end_time = time.perf_counter()
    print(f"[OK] {end_time - start_time:.4f} seconds")

    for k, v in resultSet.items():
        if not v:
            continue
        pandas.DataFrame(v, index=False).to_csv(f"{RES_DIR}\\{i.lower}.json")
        with open(f"{RES_DIR}\\{i.lower}.json", "w") as fp: 
            json.dump(v, fp)
            fp.close()

if __name__ == "__main__":
    if (useRawMode): nativeMode()
    else: dictMode()