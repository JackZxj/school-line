import sqlite3

typeList = []
def main():
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    cursor = c.execute(
        "SELECT TYPE, count(TYPE) from SCHOOLLINEPLUS group by TYPE order by count(TYPE) desc")
    result = cursor.fetchall()
    # print(result)
    for i in result:
        typeList.append(i[0])
    print(typeList)


if __name__ == "__main__":
    main()