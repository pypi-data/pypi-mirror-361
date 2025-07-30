# ashok-ll

A lightweight Python module for performing various singly linked list operations like reversing, deleting head/tail, etc.

## Example

```python
from ashok_ll import ListNode, reverseLL, printList

head = ListNode(1, ListNode(2, ListNode(3)))
printList(head)

head = reverseLL(head)
printList(head)
