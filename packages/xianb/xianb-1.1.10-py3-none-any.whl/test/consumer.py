from xianbao.core.BlockDeque import SQLiteProcessQueue


queue = SQLiteProcessQueue("../rpa_ztdb.db", "queue")
for i in range(10):
    print(queue.get())
