import time
import simplejson
import hashlib
import uuid
from flask import Flask
from flask import request
from flask import jsonify



class InfoBlockChain(object):

    def __init__(self):
        self.accounts = set()
        self.current_trade_list = []
        self.infoBlockChain = []
        # Param land_owner_info can be load by a function for the real data
        self.new_block(success_trade=[], reject_trade=[], contract_id="", previous_hash='1',
                       land_owner_info={'land1': 10000, 'land2': 33333, 'land3': 12345})


    def register_account(self, identifier):
        """
        THIS IS DUMMY RULE NOW!!!
        Add a new account to the list of accounts
        :param identifier: Identifier of node. Eg. '1234567890'
        """

        if isinstance(identifier, int) and 10000 < identifier < 99999:

            self.accounts.add(identifier)

        else:
            raise ValueError('Invalid ID')

    def new_block(self, success_trade, reject_trade, contract_id, previous_hash, land_owner_info):
        """
        Create a new Block in the InfoBlockChain
        :param success_trade: success_trade
        :param reject_trade: reject trade list
        :param contract_id: The evidence of the land trade eg. contract number
        :param previous_hash: Hash of previous Block
        :param land_owner_info the land owner information
        :return: New Block
        """

        block = {
            'index': len(self.infoBlockChain) + 1,
            'timestamp': 'UTC ' + time.asctime(time.gmtime()),
            'success_trade': success_trade,
            'contract_id': contract_id,
            'reject_trade' : reject_trade,
            'previous_hash': previous_hash or self.hash(self.infoBlockChain[-1]),
            'land_owner_info' : land_owner_info
        }

        # Reset the current list of transactions
        self.current_trade_list = []

        self.infoBlockChain.append(block)
        return block

    @property
    def last_block(self):
        return self.infoBlockChain[-1]



    def new_trade(self, trade_id, sender, recipient, land_id, pay) :
        """
        Creates a new transaction to go into the next mined Block
        :param trade_id: trade id
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param land_id: land_id
        :param pay: payment
        :return: The index of the Block that will hold this transaction
        """
        self.current_trade_list.append({
            'trade_id' : trade_id,
            'sender': sender,
            'recipient': recipient,
            'land_id': land_id,
            'pay' : pay,
            'request_timestamp' : 'UTC ' + time.asctime(time.gmtime())
        })



    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = simplejson.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    def proof_of_trade(self, last_block):
        pass



app = Flask(__name__)

global_trade_id = str(uuid.uuid4()).replace('-', '')


infoblockchain = InfoBlockChain()


@app.route('/account/register', methods=['POST'])
def register_account():
    values = request.get_json()


    # Allow to create multiple accounts for testing only
    accounts = values.get('accounts')

    if accounts is None:
        return "Please supply a valid account list", 400

    for account in accounts:
        infoblockchain.register_account(account)

    response = {
        'message' : "accounts have been added",
        'account_list' : list(infoblockchain.accounts)
    }

    print(response)
    return jsonify(response), 201


@app.route('/tradelist/account=<int:account>', methods=['GET'])
def get_trade_list(account):

    """
    account = request.headers.get('account')
    """

    print(type(account))

    if infoblockchain.current_trade_list is None:
        return "No Trade now", 201

    response = {'tradelist': infoblockchain.current_trade_list}

    for trade_list in infoblockchain.current_trade_list:
        if account == trade_list['recipient']:
            response['You have a trade request'] = trade_list['sender']
            return jsonify(response), 201

    return jsonify(response), 201


@app.route('/newtrade', methods=['POST'])
def new_trade():
    values = request.get_json()
    print(values)
    required_keys = ['sender', 'recipient', 'land_id', 'pay']
    if not all(key in values for key in required_keys):
        return 'Missing Value', 400

    if values['sender'] not in infoblockchain.accounts:
        return 'Sender account not valid', 400

    if values['recipient'] not in infoblockchain.accounts or \
            values['recipient'] != infoblockchain.last_block()['land_owner_info'][values['land_id']]:
        return 'Recipient account not valid', 400

    if infoblockchain.infoBlockChain.__len__() > 1:
        if values['land_id'] not in infoblockchain.last_block()['land_owner_info'].keys():
            return 'Land ID not valid', 400


    # Create a new trade
    infoblockchain.new_trade(global_trade_id, values['sender'], values['recipient'],
                             values['land_id'], values['pay'])

    response = {'message' : f'New Trade Request Created, Trade ID:{new_block_index}'}
    return jsonify(response), 201


@app.route('/makedeal', methods=['POST'])
def make_deal():

    """
    sample json:
    {
        'success' : [{'trade_id' : 1234, 'sender' : 33333, 'recipient' : 12345, 'land_id' : 'land1'， ‘contract_id' : 123456}],
        'reject' :  [{'trade_id' : 1234, 'sender' : 33333, 'recipient' : 12345, 'land_id' : 'land1'},
                    {'trade_id' : 1234, 'sender' : 33333, 'recipient' : 12345, 'land_id' : 'land1'},
                    {'trade_id' : 1234, 'sender' : 33333, 'recipient' : 12345, 'land_id' : 'land1'}
                    ]
    }


    """
    trade_list = request.get_json()
    success_values = ['trade_id', 'sender', 'recipient', 'land_id', 'contract_id']
    reject_values = ['trade_id', 'sender', 'recipient', 'land_id']

    if not all(key in trade_list['success'] for key in success_values and trade_list['success'].__len__() > 1):
        return 'Information Incomplete, need valid success trade info', 400

    if not all(key in trade_list['reject'] for key in reject_values):
        return 'Information Incomplete, need reject trade info', 400



    # Unsolved Condition : contract_id needs to be validated
    contract_id = trade_list['success']['contract_id']
    success_trade = ''
    reject_trade = []
    # Unsolved Condition : the trade list is continuously increasing
    for trade in infoblockchain.current_trade_list:

        if trade['trade_id'] == trade_list['success']['trade_id']:
            success_trade = trade_list['success']
            continue
        for reject in trade_list['reject']:
            if reject['trade_id'] == trade['trade_id']:
                reject_trade.append(reject)


    # Create a TradeBlock!!!!









    # Add a new Block
    last_block = InfoBlockChain.last_block()
    previous_hash = InfoBlockChain.hash(last_block)
    previous_land_owner_info = last_block['land_owner_info']
    land_id = trade_list['success']['land_id']
    previous_land_owner_info[land_id] = trade_list['success']['sender']
    new_land_owner_info = previous_land_owner_info

    block = infoblockchain.new_block(success_trade, reject_trade, contract_id=contract_id,
                                     previous_hash=previous_hash, new_land_owner_info=new_land_owner_info)

    return "Make Deal! It's added to a new block. Block ID = "+block['index'], 201

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5666)



