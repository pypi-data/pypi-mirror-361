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
        temp = temp.next
    print("NULL")

def deleteHead(head : ListNode) -> ListNode :
    if head == None or head.next == None:
        return None
    return head.next


# pypi-AgEIcHlwaS5vcmcCJGFmZWMyNzBhLTg1NDUtNGQxYy05MGFhLWRlNjgyNTgwMTI2NwACKlszLCI1Yzc0MGM5OS05YWI4LTQ0MTYtYWE3My1hNzg4NWQwOTg0NzIiXQAABiCqeVEPaWx4DhYlQq260_HTIlpeOGAI7UG7fADVeks2SA