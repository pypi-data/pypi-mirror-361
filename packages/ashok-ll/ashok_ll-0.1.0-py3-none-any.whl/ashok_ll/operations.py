from .node import ListNode 

def reverseLL(head : ListNode) -> ListNode :
    prev = None 
    temp = head 
    while temp :
        front = temp.next
        temp.next = prev 
        prev = temp 
        temp = front
    return prev

def printLL(head : ListNode) -> None :
    temp = head 
    while temp :
        print(temp.val , end=" -> ")
    print("NULL")

def deleteHead(head : ListNode) -> ListNode :
    if head == None or head.next:
        return None
    return head.next