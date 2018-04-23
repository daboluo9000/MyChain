block = {'index': 1,
            'timestamp': 'UTC ',
            'trade_list': 123,
            'proof': 123,
            'previous_hash': 123213,
            'land_owner_info': {'a' : 'land1', 'b' : 'land2', 'c' : 'land3'}}

block2 = {'index': 2,
            'timestamp': 'UTC ',
            'trade_list': 3333,
            'proof': 3333323,
            'previous_hash': 123213,
            'land_owner_info': {'a' : 'land1', 'b' : 'land2', 'c' : 'land3'}}



list = []

list.append(block)
list.append(block2)


print(list.__len__())


