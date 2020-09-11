# -*- coding: utf-8 -*-
import codecs


class Util():
    @staticmethod
    def read_stock(file):
        result = []
        try:
            f = open(file, 'r').readlines()
            for i in f:
                i = i.strip()
                if len(i) != 6:
                    continue
                result.append(i)
        except Exception as e:
            print(e)
            return None
        return result
