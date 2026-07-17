import sys
import copy

# Python 3.14 compatibility patch for Django Template Context copy
try:
    from django.template.context import BaseContext

    def _patched_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _patched_copy
except Exception:
    pass
