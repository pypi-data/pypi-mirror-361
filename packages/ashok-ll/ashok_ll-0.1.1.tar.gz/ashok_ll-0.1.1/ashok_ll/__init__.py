from .node import ListNode
from .operations import reverseLL , deleteHead , printLL

if __name__ == '__main__' :
    head = ListNode(10 , ListNode(20 , ListNode(30)))
    printLL(head)
        