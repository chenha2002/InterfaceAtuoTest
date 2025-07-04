import multiprocessing

a = 1

def demo1():
    global a
    a += 1

def demo2():
    print(a)

def main():
    t1 = multiprocessing.Process(target=demo1)
    t2 = multiprocessing.Process(target=demo2)
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()