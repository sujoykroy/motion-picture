"""This module provides the entry point for Windows executable"""
import os

import img2vid

THIS_DIR=os.path.abspath(os.path.dirname(__file__))
os.environ['VCRUNTIME']=os.path.join(THIS_DIR, 'vcruntime140.dll')
os.environ['TCL_LIBRARY']=os.path.join(THIS_DIR, 'ActiveTcl\\lib\\tcl8.6')
os.environ['TK_LIBRARY']=os.path.join(THIS_DIR, 'ActiveTcl\\lib\\tkl8.6')

img2vid.main()