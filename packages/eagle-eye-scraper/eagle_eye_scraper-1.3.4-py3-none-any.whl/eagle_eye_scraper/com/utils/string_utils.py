def removesuffix(s: str, suffix: str) -> str:
    """
    在 Python 3.8 及以下版本中实现 str.removesuffix 的功能。

    :param s: 原始字符串
    :param suffix: 需要移除的后缀
    :return: 移除后缀后的字符串
    """
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s
