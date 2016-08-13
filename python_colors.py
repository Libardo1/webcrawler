#! /usr/bin/env python



def COL(string, color):
    
    if color=='blue':
        pref = '\033[94m'
        
    if color=='header':
        pref = '\033[95m'
        
    if color=='green':
        pref = '\033[92m'

    if color=='warning':
        pref = '\033[93m'
        
    if color=='fail':
        pref = '\033[91m'
                
    suff = '\033[0m'
    return pref + string + suff



    
