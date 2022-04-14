class Error(Exception):
    pass


class NotSupportError(Error):
    """Not support c2c connection"""
    pass


class NotExistError(Error):
    """Already exsit error"""
    pass
