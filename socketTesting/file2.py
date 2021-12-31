import file1 as var
import multiprocessing
from multiprocessing import Process, Manager
from queue import Queue


class Broadcaster(multiprocessing.Process):
    def __init__(self, id, lis=0,broad=0):
        super(Broadcaster, self).__init__()
        
class A(multiprocessing.Process):
    def __init__(self, man, leaderID, leader, lst,lst2):
        super(A, self).__init__()
        self.groupview = man
        self.leaderID = leaderID
        self.leader = leader
        self.lst = lst
        self.lst2 = lst2
        
    def run(self):
        print(self.groupview)
        data = self.groupview['groupView']
        data.update({"2":"3"})
        data.update({"3":"3"})
        self.leader.value = 1
        self.leaderID.value = 1022
        self.groupview['groupView'] = data
        self.lst.append(23)
        self.lst.pop()
        self.lst.append({"check":123})
        self.lst.append({"check":124})
        self.lst2['response_queu'].put({"key":1})
        self.lst2['response_queu'].put({"key":2})
        self.lst2['response_queu'].put({"key":3})

        print(self.groupview)


        return
   
        
class B:
    def __init__(self) -> None:
        pass
    def test(self):
        print(var.foo)
        var.foo = 16
    def test2(self):
        print(var.foo)


def f(d):
    d[1] += '1'
    d['2'] += 2

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()
    leaderID = manager.Value('i',123)
    leader = manager.Value('i',0)
    lst = manager.list([])
    lst2 = manager.dict({"response_queu":Queue(maxsize=0)})
    d["groupView"] = {"0":"1"}
    a = A(d, leaderID, leader,lst, lst2)
    a.start()
    a.join()
    '''
    p1 = Process(target=f, args=(d,))
    p2 = Process(target=f, args=(d,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    '''
    print (d)
    print(leaderID.value)
    print(leader)
    print(lst)
    print(lst2['response_queu'])
    