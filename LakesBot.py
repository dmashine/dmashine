#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import gvr, OSMAPI


if __name__=="__main__":
    gvrlist = gvr.GVRList(bo="1", rb="67", hep="591",subb="86", wot="11")
    for o in gvrlist:
        name=o.get_data()[u"Название"]
        print name
        OSMAPI.search(name)
