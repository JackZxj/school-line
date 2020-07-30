import requests
import sqlite3
import time
import json
import schoolLine as baseline


def requestSchoolSpecial(schoolid, provinceName, stype):
    provinceName = baseline.provinceName
    GprovinceID = baseline.GprovinceID
    provinceid = GprovinceID[provinceName]
    url = "https://static-data.eol.cn/www/school/%d/dic/specialscore.json" % (schoolid)
    headers = headers = {'Accept': 'text/plain, application/json, */*',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    result = requests.get(url, headers=headers)
    specialScore = json.loads(result.text)
    years = specialScore['year']
    
    for year in years:
        url = "https://static-data.eol.cn/www/2.0/schoolspecialindex/%d/%d/%d/%d/1.json" % (
            year, schoolid, provinceid, stype)
        result = requests.get(url, headers=headers)
        info = json.loads(result.text)
        if info['code'] != "0000":
            print('request school special list Error')
            return ""
        print('get schoolSpecialList 1')
        schoolSpecialList = info['data']['item']
        count = info['data']['numFound']
        if count > 10:
            for i in range(count // 10):
                time.sleep(5)
                url = "https://static-data.eol.cn/www/2.0/schoolspecialindex/%d/%d/%d/%d/%d.json" % (
                    year, schoolid, provinceid, stype, i + 2)
                result = requests.get(url, headers=headers)
                info = json.loads(result.text)
                if info['code'] != "0000":
                    print('request school special list Error')
                    return ""
                print('get schoolSpecialList %d' % (i + 2))
                schoolSpecialList = schoolSpecialList + info['data']['item']
        conn = sqlite3.connect('score.db')
        c = conn.cursor()
        for i in range(len(schoolSpecialList)):
            schoolSpecial = schoolSpecialList[i]
            specialId = schoolSpecial['special_id']
            specialName = schoolSpecial['spname']
            minScore = schoolSpecial['min']
            batch = schoolSpecial['local_batch_name']
            cursor = c.execute(
                "SELECT * from SCHOOLSPECIALLINE where \
                    SCHOOLID=%d AND PROVINCE='%s' AND STYPE=%d AND YEAR=%d AND MIN='%s' AND BATCH='%s'" % (
                        schoolid, provinceName, stype, year, minScore, batch))
            result = cursor.fetchall()
            if len(result) == 0:
                maxScore = averScore = None
                minSection = -1
                if schoolSpecial['max'] != '-':
                    maxScore = schoolSpecial['max']
                if schoolSpecial['average'] != '--':
                    averScore = schoolSpecial['max']
                if schoolSpecial['min_section']:
                    minSection = int(schoolSpecial['min_section'])
                if schoolSpecial['proscore'] != '-':
                    provinceScore = int(schoolSpecial['proscore'])
                c.execute(
                    "INSERT INTO SCHOOLLINEPLUS (SCHOOLID, PROVINCE, STYPE, YEAR, MAX, AVERAGE, MIN, MIN_SECTION, PRO_SCORE, TYPE, BATCH) \
                    VALUES (%d, '%s', %d, %d, '%s', '%s', '%s', %d, %d, '%s', '%s')"
                    % (schoolid, provinceName, int(stype), year, maxScore, averScore, minScore, minSection, provinceScore, zslx, batch))
                conn.commit()
            else:
                print(result)
                print(result[0][7])
        conn.close()
        print(len(schoolSpecialList))
        print()