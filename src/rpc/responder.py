from PyQt4 import QtCore, QtGui
from rpc.common import Request, Operation, OpType
from utils.utils import Utils

class RPCresponder:
    """ Handles the processing of RPC requests"""
    def __init__(self, state):
        # make all of the string functions available through
        # string.func_name
        import string
        self.string = string
        self.state = state

    def _listMethods(self):
        # implement this method so that system.listMethods
        # knows to advertise the strings methods
        return list_public_methods(self) + \
                ['string.' + method for method in list_public_methods(self.string)]

    # RPC methods
    def enq(self,rqData):
        """ Unmarshalls the request and add it to the queue"""

        rq = Request(**rqData)

        print 'Responder, rq:', rq
        appended = self.state.appendToQueue(rq)
        if !appended:
            return True
        self.state.executeOperations()
        return True
