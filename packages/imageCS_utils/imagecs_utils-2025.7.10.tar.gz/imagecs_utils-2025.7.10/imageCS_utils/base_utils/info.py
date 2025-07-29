"""My Info class"""
# pylint: disable=invalid-name

class Info:
    """My Info Class"""
    @staticmethod
    def info(s, **kwargs):
        """info"""
        print(f"[Info] {s}", **kwargs)
    
    @staticmethod
    def warn(s, **kwargs):
        """warn with yellow font"""
        print(f"\033[93m[Warn] {s}\033[0m", **kwargs)
    
    @staticmethod
    def WARN(s, **kwargs):
        """warn with yellow back"""
        print(f"\033[103m[WARN] {s}\033[0m", **kwargs)
    
    @staticmethod
    def error(s, **kwargs):
        """print error with red font"""
        print(f"\033[91m[ERROR] {s}\033[0m", **kwargs)
