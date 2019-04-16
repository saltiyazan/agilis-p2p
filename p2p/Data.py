import time

class Data:
    """
    Egyseges adatformatumot megvalosito osztaly.
    Az elkuldendo adatokat idobelyeggel latja el.
    """
    def __init__(self, data):
        # timestamp + adat tarolasa
        self.data = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            data
        )

    def __str__(self):
        return f'Data[{self.data}]'

    def __repr__(self):
        return f'Data[{self.data}]'