import pytest

from netorchestr.envir.psimplemodule import PSimpleModule
from netorchestr.envir.psimplelink import PSimpleLink
from netorchestr.envir.psimplemessage import PSimpleMessage
from netorchestr.envir.psimplegate import PSimpleGate
from netorchestr.envir.psimplenet import PSimpleNet

class Txc(PSimpleModule):
    def __init__(self, name:str):
        super().__init__(name)

    def initialize(self):
        if self.name == 'tic':
            msg = PSimpleMessage(0, 'tic', 'toc', 'tictocMsg', '0')
            self.send_msg(msg, 'out')

    def recv_msg(self, msg:PSimpleMessage, gate:PSimpleGate):
        self.send_msg(msg, 'out')

def test_tictac():
    net = PSimpleNet('Tictoc')
    tic = Txc('tic')
    toc = Txc('toc')
    
    gate_tic = PSimpleGate('out', tic)
    gate_toc = PSimpleGate('out', toc)
    
    tic.gates[gate_tic] = (PSimpleLink('tic-toc', 20.0), gate_toc)
    toc.gates[gate_toc] = (PSimpleLink('tic-toc', 100.0), gate_tic)
    
    net.add_module(tic)
    net.add_module(toc)
    
    net.run(1000)

if __name__ == '__main__':
    pytest.main()
