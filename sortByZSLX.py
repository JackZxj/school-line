import os
import schoolLine as baseline
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

provinceLine = [410, 352, 333, 378, 393]
baseyear = [2015, 2016, 2017, 2018, 2019]
higherThenBase = 10


def main():
    stype = baseline.GtypeID[baseline.typeName]
    conn = sqlite3.connect('score.db')
    yearLine = {k: v for k, v in zip(baseyear, provinceLine)}
    for batch in baseline.batchList:
        if not os.path.exists('./%s省%s录取情况/高于省线%d' % (baseline.provinceName, batch, higherThenBase)):
            os.makedirs('./%s省%s录取情况/高于省线%d' %
                        (baseline.provinceName, batch, higherThenBase))

        result = []
        for zslx in baseline.zslxList:
            # 打印省线
            plt.figure(figsize=(20, 15))
            plt.plot(baseyear, provinceLine, 'o', label='%s省本科线' %
                     (baseline.provinceName), linestyle='-', color='black')
            plt.fill_between(baseyear, (np.array(provinceLine) + 10).tolist(),
                             (np.array(provinceLine) - 10).tolist(), color='black', alpha=.2)
            plt.fill_between(baseyear, (np.array(provinceLine) + 20).tolist(),
                             (np.array(provinceLine) - 20).tolist(), color='black', alpha=.1)
            saveImg = False
            schoolSet = set()

            # 获取数据
            c = conn.cursor()
            cursor = c.execute(
                "SELECT * from SCHOOLLINEPLUS where PROVINCE='%s' AND STYPE='%s' \
                    AND TYPE='%s' AND BATCH='%s'" % (
                    baseline.provinceName, stype, zslx, batch))
            result = cursor.fetchall()
            # print(result, '\n')
            sortBySchool = {}
            for t in result:
                cursor = c.execute(
                    "SELECT name from SCHOOLID where schoolid=%d" % (t[1]))
                res = cursor.fetchall()
                kname = res[0][0]
                sortBySchool.setdefault(kname, []).append(t)
            # print(sortBySchool)

            for k, v in sortBySchool.items():
                score = []
                year = []
                isPlt = False
                for i in v:
                    try:
                        score.append(float(i[7]))
                        year.append(i[4])
                        if yearLine[i[4]] + higherThenBase > int(float(i[7])):
                            isPlt = True
                    except Exception as e:
                        print(e)
                        print()
                if len(score) > 0 and isPlt:
                    plt.plot(year, score, 'o', label=k, linestyle='-')
                    schoolSet.add(k)
                    saveImg = True
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.legend(bbox_to_anchor=[1, 1])
            plt.grid()
            plt.ylim((325, 500))
            plt.subplots_adjust(left=0.05, bottom=0.05, right=0.75, top=0.95)
            if saveImg:
                plt.savefig('./%s省%s录取情况/高于省线%d/%s.png' %
                            (baseline.provinceName, batch, higherThenBase, zslx))
                file = './%s省%s录取情况/高于省线%d/%s-%d个.txt' % (
                    baseline.provinceName, batch, higherThenBase, zslx, len(schoolSet))
                school = ', '.join(schoolSet)
                with open(file, 'w') as file_object:
                    file_object.write(school)
            plt.cla()
            plt.close()
    conn.close()


if __name__ == "__main__":
    main()
