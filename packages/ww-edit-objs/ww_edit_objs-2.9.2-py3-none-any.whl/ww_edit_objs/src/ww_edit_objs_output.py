from miautil import typemap as tm


class Output:
    """
    node out-ports that connect to other nodes' in-ports
    - use type annotation for all attributes
    - supported types:
        - py-types: bool, float, int, str; they are not portmap-able
        - proxy-types: tm.tProxyType; they are portmap-able
        - annotated collections: list[...], tuple[...]; they are portmap-able when the element type is proxy-type
    - ctor must contain only attribute definitions and their comments as user docs
    - example:
        def __init__(self):
            # doc for self.notMapped1
            self.notMapped1: str = ''
            # doc for self.notMapped2
            self.notMapped2: list[str] = []
            # doc for self.mapped1
            self.mapped1: tm.tFile = ''
            # doc for self.mapped2
            self.mapped2: list[tm.tFile] = ['']
    """
    def __init__(self):
        # 将输入 objects 原样输出
        self.passedObjList: tm.tWobjList = ''
        pass
