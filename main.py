import sys
from multiprocessing import Process

sys.path.append('../')
from schedule.refresh_proxy import run as refresh_proxy
from schedule.check_proxy import check_proxy

def main():
    p = Process(target=refresh_proxy, name='RefreshProxy')
    p2 = Process(target=check_proxy, name='CheckProxy')

    p.start()
    p2.start()

    p.join()
    p2.join()


if __name__ == '__main__':
    main()
