# ctypes-glpk - A ctypes-based Python wrapper for GLPK

# Copyright (c) 2008, Minh-Tri Pham
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# For further inquiries, please contact Minh-Tri Pham(pmtri80@gmail.com) for more information.
# ---------------------------------------------------------------------
#!/usr/bin/env python
"""ctypes-glpk - A ctypes-based Python wrapper for GLPK

ctypes-glpk is a Python wrapper for GNU Linear Programming Kit (GLPK) based on ctypes.

:Author: Minh-Tri Pham <pmtri80@gmail.com>
:Version: 0.1.0 (devel)
:Released: September 2008 (devel)

Requirement
===========

The only requirement is that you have GLPK installed on your platform. ctypes-glpk detects the existence of GLPK by calling 'glpsol -v'. It uses the corresponding shared library of GLPK to provide the interface.

Installation
============

Just include this 'glpk.py' in your <Python>\lib\site-packages folder, or add a path to the file in your PYTHONPATH variable.

Support
-------

- Platforms: Win32, Linux, and Mac OS
- GLPK: 4.9 to 4.31

How to use
==========

See the 'sample.c' file for an example of using GLPK in C, and the 'sample.py' file for the corresponding code in Python. You will find that they are almost identical.


Change Log
==========

To be updated.

"""

#=============================================================================
# Importation
#=============================================================================
from ctypes import *
import os, sys

# Common declarations
c_int_p = POINTER(c_int)
c_float_p = POINTER(c_float)
c_double_p = POINTER(c_double)
size_t = c_uint


#=============================================================================
# Detect GLPK and load it
#=============================================================================
def _load_glpk():
    # Attempt to automatically detect which version of GLPK we are using.
    try:
        fi, fo = os.popen4('glpsol -v')
        fi.close()
        tokens = fo.read().split()
        # Version GLPK detected!!
        version_string = tokens[tokens.index('Version')+1]
        version = version_string.split('.')
        version = tuple([int(i) for i in version[:2]])
        
    except Exception, e:
        raise ImportError("Failed to run 'glpsol' to extract version number. GLPK may not be properly installed.")

    # Attempt to load the DLL
    if os.name == 'posix' and sys.platform.startswith('linux'):
        dllname = 'libglpk.so'
    elif os.name == 'posix' and sys.platform.startswith('darwin'):
        dllname = 'libglpk.dylib'
    elif os.name == 'nt':
        dllname = 'glpk'+str(version[0])+str(version[1])+'.dll'
    else:
        raise ImportError('Platform '+str(os.name)+' is currently not supported.')

    try:
        glpk_lib = cdll.LoadLibrary(dllname)
    except:
        raise ImportError("Cannot import GLPK's shared library (" + dllname + "). Make sure its path is included in your system's PATH variable.")
        
    return version, glpk_lib
    
_version, _glpk_lib = _load_glpk()

# return the current GLPK version
if _version >= (4, 9):
    def lpx_version():
        return str(_version[0])+'.'+str(_version[1])

#=============================================================================
# make function prototypes a bit easier to declare
#=============================================================================
def cfunc(name, result, *args):
    '''build and apply a ctypes prototype complete with parameter flags
    e.g.
cvMinMaxLoc = cfunc('cvMinMaxLoc', None,
                    ('image', POINTER(IplImage), 1),
                    ('min_val', POINTER(double), 2),
                    ('max_val', POINTER(double), 2),
                    ('min_loc', POINTER(CvPoint), 2),
                    ('max_loc', POINTER(CvPoint), 2),
                    ('mask', POINTER(IplImage), 1, None))
means locate cvMinMaxLoc in dll _glpk_lib, it returns nothing.
The first argument is an input image. The next 4 arguments are output, and the last argument is
input with an optional value. A typical call might look like:

min_val,max_val,min_loc,max_loc = cvMinMaxLoc(img)
    '''
    atypes = []
    aflags = []
    for arg in args:
        atypes.append(arg[1])
        aflags.append((arg[2], arg[0]) + arg[3:])
    return CFUNCTYPE(result, *atypes)((name, _glpk_lib), tuple(aflags))

    
#=============================================================================
# Identifiers
#=============================================================================

if _version >= (4, 9) and _version <= (4, 15):
    _lpx = 'glp_lpx_'
elif _version >= (4, 16):
    _lpx = '_glp_lpx_'
    _glp = 'glp_'

    
#=============================================================================
# Problem Object
#=============================================================================

if _version >= (4, 9):
    def LPX_FIELDS():
        return [] # to be expanded in the future

    class LPX(Structure):
        _fields_ = LPX_FIELDS()

if _version >= (4, 16):
    glp_prob = LPX


#=============================================================================
# Karush-Kuhn-Tucker
#=============================================================================

if _version >= (4, 9):
    def LPXKKT_FIELDS():
        return [
            ('pe_ae_max', c_double), # largest absolute error
            ('pe_ae_row', c_int), # number of row with largest absolute error
            ('pe_re_max', c_double), # largest relative error
            ('pe_re_row', c_int), # number of row with largest relative error
            ('pe_quality', c_int), # quality of primal solution

            ('pb_ae_max', c_double), # largest absolute error
            ('pb_ae_ind', c_int), # number of variable with largest absolute error
            ('pb_re_max', c_double), # largest relative error
            ('pb_re_ind', c_int), # number of variable with largest relative error
            ('pb_quality', c_int), # quality of primal feasibility

            ('de_ae_max', c_double), # largest absolute error
            ('de_ae_col', c_int), # number of column with largest absolute error
            ('de_re_max', c_double), # largest relative error
            ('de_re_col', c_int), # number of column with largest relative error
            ('de_quality', c_int), # quality of dual solution

            ('db_ae_max', c_double), # largest absolute error
            ('db_ae_ind', c_int), # number of variable with largest absolute error
            ('db_re_max', c_double), # largest relative error
            ('db_re_ind', c_int), # number of variable with largest relative error
            ('db_quality', c_int), # quality of dual feasibility

            ('cs_ae_max', c_double), # largest absolute error
            ('cs_ae_ind', c_int), # number of variable with largest absolute error
            ('cs_re_max', c_double), # largest relative error
            ('cs_re_ind', c_int), # number of variable with largest relative error
            ('cs_quality', c_int), # quality of complementary slackness
        ]

    class LPXKKT(Structure):
        _fields_ = LPXKKT_FIELDS()
    
    
#=============================================================================
# Problem creating and modifying routines
#=============================================================================

if _version >= (4, 9):
    # create problem object
    lpx_create_prob = cfunc(_lpx+'create_prob', POINTER(LPX))

    # assign (change) problem name
    lpx_set_prob_name = cfunc(_lpx+'set_prob_name', None,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # assign (change) objective function name
    lpx_set_obj_name = cfunc(_lpx+'set_obj_name', None,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # set (change) optimization direction flag
    lpx_set_obj_dir = cfunc(_lpx+'set_obj_dir', None,
        ('lp', POINTER(LPX), 1),
        ('dir', c_int, 1),
    )
    LPX_MIN = 120 # minimization
    LPX_MAX = 121 # maximization

    # add new rows to problem object
    lpx_add_rows = cfunc(_lpx+'add_rows', c_int,
        ('lp', POINTER(LPX), 1),
        ('nrs', c_int, 1),
    )

    # add new columns to problem object
    lpx_add_cols = cfunc(_lpx+'add_cols', c_int,
        ('lp', POINTER(LPX), 1),
        ('ncs', c_int, 1),
    )

    # assign (change) row name
    lpx_set_row_name = cfunc(_lpx+'set_row_name', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('name', c_char_p, 1),
    )

    # assign (change) column name
    lpx_set_col_name = cfunc(_lpx+'set_col_name', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('name', c_char_p, 1),
    )

    # set (change) row bounds
    lpx_set_row_bnds = cfunc(_lpx+'set_row_bnds', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('type', c_int, 1),
        ('lb', c_double, 1),
        ('ub', c_double, 1),
    )
    LPX_FR = 110 #free variable
    LPX_LO = 111 # variable with lower bound
    LPX_UP = 112 # variable with upper bound
    LPX_DB = 113 # double-bounded variable
    LPX_FX = 114 # fixed variable

    # set (change) column bounds
    lpx_set_col_bnds = cfunc(_lpx+'set_col_bnds', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('type', c_int, 1),
        ('lb', c_double, 1),
        ('ub', c_double, 1),
    )

    # set (change) objective coefficient or constant term
    lpx_set_obj_coef = cfunc(_lpx+'set_obj_coef', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('coef', c_double, 1),
    )

    # set (replace) row of the constraint matrix
    lpx_set_mat_row = cfunc(_lpx+'set_mat_row', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # set (replace) column of the constraint matrix
    lpx_set_mat_col = cfunc(_lpx+'set_mat_col', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # load (replace) the whole constraint matrix
    lpx_load_matrix = cfunc(_lpx+'load_matrix', None,
        ('lp', POINTER(LPX), 1),
        ('ne', c_int, 1),
        ('ia', c_int_p, 1),
        ('ja', c_int_p, 1),
        ('ar', c_double_p, 1),
    )

    # delete rows from problem object
    lpx_del_rows = cfunc(_lpx+'del_rows', None,
        ('lp', POINTER(LPX), 1),
        ('nrs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete columns from problem object
    lpx_del_cols = cfunc(_lpx+'del_cols', None,
        ('lp', POINTER(LPX), 1),
        ('ncs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete problem object
    lpx_delete_prob = cfunc(_lpx+'delete_prob', None,
        ('lp', POINTER(LPX), 1),
    )
    
if _version >= (4, 16):
    # create problem object
    glp_create_prob = cfunc(_glp+'create_prob', POINTER(glp_prob))

    # assign (change) problem name
    glp_set_prob_name = cfunc(_glp+'set_prob_name', None,
        ('lp', POINTER(glp_prob), 1),
        ('name', c_char_p, 1),
    )

    # assign (change) objective function name
    glp_set_obj_name = cfunc(_glp+'set_obj_name', None,
        ('lp', POINTER(glp_prob), 1),
        ('name', c_char_p, 1),
    )

    # set (change) optimization direction flag
    glp_set_obj_dir = cfunc(_glp+'set_obj_dir', None,
        ('lp', POINTER(glp_prob), 1),
        ('dir', c_int, 1),
    )
    GLP_MIN   = 1  # minimization
    GLP_MAX   = 2  # maximization

    # add new rows to problem object
    glp_add_rows = cfunc(_glp+'add_rows', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('nrs', c_int, 1),
    )

    # add new columns to problem object
    glp_add_cols = cfunc(_glp+'add_cols', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('ncs', c_int, 1),
    )

    # assign (change) row name
    glp_set_row_name = cfunc(_glp+'set_row_name', None,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
        ('name', c_char_p, 1),
    )

    # assign (change) column name
    glp_set_col_name = cfunc(_glp+'set_col_name', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('name', c_char_p, 1),
    )

    # set (change) row bounds
    glp_set_row_bnds = cfunc(_glp+'set_row_bnds', None,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
        ('type', c_int, 1),
        ('lb', c_double, 1),
        ('ub', c_double, 1),
    )
    GLP_FR = 1 #free variable
    GLP_LO = 2 # variable with lower bound
    GLP_UP = 3 # variable with upper bound
    GLP_DB = 4 # double-bounded variable
    GLP_FX = 5 # fixed variable

    # set (change) column bounds
    glp_set_col_bnds = cfunc(_glp+'set_col_bnds', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('type', c_int, 1),
        ('lb', c_double, 1),
        ('ub', c_double, 1),
    )

    # set (change) objective coefficient or constant term
    glp_set_obj_coef = cfunc(_glp+'set_obj_coef', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('coef', c_double, 1),
    )

    # set (replace) row of the constraint matrix
    glp_set_mat_row = cfunc(_glp+'set_mat_row', None,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # set (replace) column of the constraint matrix
    glp_set_mat_col = cfunc(_glp+'set_mat_col', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # load (replace) the whole constraint matrix
    glp_load_matrix = cfunc(_glp+'load_matrix', None,
        ('lp', POINTER(glp_prob), 1),
        ('ne', c_int, 1),
        ('ia', c_int_p, 1),
        ('ja', c_int_p, 1),
        ('ar', c_double_p, 1),
    )

    # delete rows from problem object
    glp_del_rows = cfunc(_glp+'del_rows', None,
        ('lp', POINTER(glp_prob), 1),
        ('nrs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete columns from problem object
    glp_del_cols = cfunc(_glp+'del_cols', None,
        ('lp', POINTER(glp_prob), 1),
        ('ncs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete problem object
    glp_delete_prob = cfunc(_glp+'delete_prob', None,
        ('lp', POINTER(glp_prob), 1),
    )

    
#=============================================================================
# Problem retrieving routines
#=============================================================================

if _version >= (4, 9):
    # retrieve problem name
    lpx_get_prob_name = cfunc(_lpx+'get_prob_name', c_char_p,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve objective function name
    lpx_get_obj_name = cfunc(_lpx+'get_obj_name', c_char_p,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve optimization direction flag
    lpx_get_obj_dir = cfunc(_lpx+'get_obj_dir', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of rows
    lpx_get_num_rows = cfunc(_lpx+'get_num_rows', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of columns
    lpx_get_num_cols = cfunc(_lpx+'get_num_cols', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row name
    lpx_get_row_name = cfunc(_lpx+'get_row_name', c_char_p,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column name
    lpx_get_col_name = cfunc(_lpx+'get_col_name', c_char_p,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve row type
    lpx_get_row_type = cfunc(_lpx+'get_row_type', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row lower bound
    lpx_get_row_lb = cfunc(_lpx+'get_row_lb', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row upper bound
    lpx_get_row_ub = cfunc(_lpx+'get_row_ub', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column type
    lpx_get_col_type = cfunc(_lpx+'get_col_type', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column lower bound
    lpx_get_col_lb = cfunc(_lpx+'get_col_lb', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column upper bound
    lpx_get_col_ub = cfunc(_lpx+'get_col_ub', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve objective coefficient or constant term
    lpx_get_obj_coef = cfunc(_lpx+'get_obj_coef', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve number of constraint coefficients
    lpx_get_num_nz = cfunc(_lpx+'get_num_nz', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row of the constraint matrix
    lpx_get_mat_row = cfunc(_lpx+'get_mat_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # retrieve column of the constraint matrix
    lpx_get_mat_col = cfunc(_lpx+'get_mat_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

if _version >= (4, 16):
    # retrieve problem name
    glp_get_prob_name = cfunc(_glp+'get_prob_name', c_char_p,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve objective function name
    glp_get_obj_name = cfunc(_glp+'get_obj_name', c_char_p,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve optimization direction flag
    glp_get_obj_dir = cfunc(_glp+'get_obj_dir', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve number of rows
    glp_get_num_rows = cfunc(_glp+'get_num_rows', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve number of columns
    glp_get_num_cols = cfunc(_glp+'get_num_cols', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve row name
    glp_get_row_name = cfunc(_glp+'get_row_name', c_char_p,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve column name
    glp_get_col_name = cfunc(_glp+'get_col_name', c_char_p,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve row type
    glp_get_row_type = cfunc(_glp+'get_row_type', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve row lower bound
    glp_get_row_lb = cfunc(_glp+'get_row_lb', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve row upper bound
    glp_get_row_ub = cfunc(_glp+'get_row_ub', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve column type
    glp_get_col_type = cfunc(_glp+'get_col_type', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve column lower bound
    glp_get_col_lb = cfunc(_glp+'get_col_lb', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve column upper bound
    glp_get_col_ub = cfunc(_glp+'get_col_ub', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve objective coefficient or constant term
    glp_get_obj_coef = cfunc(_glp+'get_obj_coef', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve number of constraint coefficients
    glp_get_num_nz = cfunc(_glp+'get_num_nz', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve row of the constraint matrix
    glp_get_mat_row = cfunc(_glp+'get_mat_row', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # retrieve column of the constraint matrix
    glp_get_mat_col = cfunc(_glp+'get_mat_col', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    
#=============================================================================
# Row and column searching routines
#=============================================================================

if _version >= (4, 15):
    # Create the name index
    lpx_create_index = cfunc(_lpx+'create_index', None,
        ('lp', POINTER(LPX), 1),
    )

    # Find row by its name
    lpx_find_row = cfunc(_lpx+'find_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # Find column by its name
    lpx_find_col = cfunc(_lpx+'find_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # Delete the name index
    lpx_delete_index = cfunc(_lpx+'delete_index', None,
        ('lp', POINTER(LPX), 1),
    )

if _version >= (4, 16):
    # Create the name index
    glp_create_index = cfunc(_glp+'create_index', None,
        ('lp', POINTER(glp_prob), 1),
    )

    # Find row by its name
    glp_find_row = cfunc(_glp+'find_row', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('name', c_char_p, 1),
    )

    # Find column by its name
    glp_find_col = cfunc(_glp+'find_col', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('name', c_char_p, 1),
    )

    # Delete the name index
    glp_delete_index = cfunc(_glp+'delete_index', None,
        ('lp', POINTER(glp_prob), 1),
    )


#=============================================================================
# Problem scaling routines
#=============================================================================

if _version >= (4, 9):
    # scale problem data
    lpx_scale_prob = cfunc(_lpx+'scale_prob', None,
        ('lp', POINTER(LPX), 1),
    )

    # unscale problem data
    lpx_unscale_prob = cfunc(_lpx+'unscale_prob', None,
        ('lp', POINTER(LPX), 1),
    )


#=============================================================================
# LP basis constructing routines
#=============================================================================

if _version >= (4, 9):
    # construct standard initial LP basis
    lpx_std_basis = cfunc(_lpx+'std_basis', None,
        ('lp', POINTER(LPX), 1),
    )

    # construct advanced initial LP basis
    lpx_adv_basis = cfunc(_lpx+'adv_basis', None,
        ('lp', POINTER(LPX), 1),
    )

if _version >= (4, 10):
    # construct advanced initial LP basis
    lpx_cpx_basis = cfunc(_lpx+'cpx_basis', None,
        ('lp', POINTER(LPX), 1),
    )

if _version >= (4, 9):
    # set (change) row status
    lpx_set_row_stat = cfunc(_lpx+'set_row_stat', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('stat', c_int, 1),
    )
    LPX_BS = 140 # basic variable
    LPX_NL = 141 # non-basic variable on lower bound
    LPX_NU = 142 # non-basic variable on upper bound
    LPX_NF = 143 # non-basic free variable
    LPX_NS = 144 # non-basic fixed variable

    # set (change) column status
    lpx_set_col_stat = cfunc(_lpx+'set_col_stat', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('stat', c_int, 1),
    )
    
if _version >= (4, 16):
    # set (change) row status
    glp_set_row_stat = cfunc(_glp+'set_row_stat', None,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
        ('stat', c_int, 1),
    )
    GLP_BS = 1 # basic variable
    GLP_NL = 2 # non-basic variable on lower bound
    GLP_NU = 3 # non-basic variable on upper bound
    GLP_NF = 4 # non-basic free variable
    GLP_NS = 5 # non-basic fixed variable

    # set (change) column status
    glp_set_col_stat = cfunc(_glp+'set_col_stat', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('stat', c_int, 1),
    )
    

#=============================================================================
# Simplex method routine
#=============================================================================

if _version >= (4, 9):
    # solve LP problem using the simplex method
    lpx_simplex = cfunc(_lpx+'simplex', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # exit codes returned by solver routines:
    LPX_E_OK = 200 # success
    LPX_E_EMPTY = 201 # empty problem
    LPX_E_BADB = 202 # invalid initial basis
    LPX_E_INFEAS = 203 # infeasible initial solution
    LPX_E_FAULT = 204 # unable to start the search
    LPX_E_OBJLL = 205 # objective lower limit reached
    LPX_E_OBJUL = 206 # objective upper limit reached
    LPX_E_ITLIM = 207 # iterations limit exhausted
    LPX_E_TMLIM = 208 # time limit exhausted
    LPX_E_NOFEAS = 209 # no feasible solution
    LPX_E_INSTAB = 210 # numerical instability
    LPX_E_SING = 211 # problems with basis matrix
    LPX_E_NOCONV = 212 # no convergence (interior)
    LPX_E_NOPFS = 213 # no primal feas. sol. (LP presolver)
    LPX_E_NODFS = 214 # no dual feas. sol. (LP presolver)

if _version >= (4, 13):
    # solve LP problem using the primal two-phase simplex method based on exact (rational) arithmetic
    lpx_exact = cfunc(_lpx+'exact', c_int,
        ('lp', POINTER(LPX), 1),
    )


#=============================================================================
# Basic solution retrieving routines
#=============================================================================

if _version >= (4, 9):
    # retrieve generic status of basic solution
    lpx_get_status = cfunc(_lpx+'get_status', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # status codes reported by the routine lpx_get_status:
    LPX_OPT = 180 # optimal
    LPX_FEAS = 181 # feasible
    LPX_INFEAS = 182 # infeasible
    LPX_NOFEAS = 183 # no feasible
    LPX_UNBND = 184 # unbounded
    LPX_UNDEF = 185 # undefined

    # retrieve primal status of basic solution
    lpx_get_prim_stat = cfunc(_lpx+'get_prim_stat', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # status of primal basic solution:
    LPX_P_UNDEF = 132 # primal solution is undefined
    LPX_P_FEAS = 133 # solution is primal feasible
    LPX_P_INFEAS = 134 # solution is primal infeasible
    LPX_P_NOFEAS = 135 # no primal feasible solution exists
    
    # retrieve dual status of basic solution
    lpx_get_dual_stat = cfunc(_lpx+'get_dual_stat', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # status of dual basic solution:
    LPX_D_UNDEF = 136 # dual solution is undefined
    LPX_D_FEAS = 137 # solution is dual feasible
    LPX_D_INFEAS = 138 # solution is dual infeasible
    LPX_D_NOFEAS = 139 # no dual feasible solution exists

if _version >= (4, 9):
    # retrieve objective value
    lpx_get_obj_val = cfunc(_lpx+'get_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row status
    lpx_get_row_stat = cfunc(_lpx+'get_row_stat', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row primal value
    lpx_get_row_prim = cfunc(_lpx+'get_row_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    lpx_get_row_dual = cfunc(_lpx+'get_row_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column status
    lpx_get_col_stat = cfunc(_lpx+'get_col_stat', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve col primal value
    lpx_get_col_prim = cfunc(_lpx+'get_col_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    lpx_get_col_dual = cfunc(_lpx+'get_col_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

if _version >= (4, 16):
    # retrieve objective value
    glp_get_obj_val = cfunc(_glp+'get_obj_val', c_double,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve row status
    glp_get_row_stat = cfunc(_glp+'get_row_stat', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve row primal value
    glp_get_row_prim = cfunc(_glp+'get_row_prim', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    glp_get_row_dual = cfunc(_glp+'get_row_dual', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve column status
    glp_get_col_stat = cfunc(_glp+'get_col_stat', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve col primal value
    glp_get_col_prim = cfunc(_glp+'get_col_prim', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    glp_get_col_dual = cfunc(_glp+'get_col_dual', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

if _version >= (4, 9):
    # retrieve non-basic variable which causes unboundness
    lpx_get_ray_info = cfunc(_lpx+'get_ray_info', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # check Karush-Kuhn-Tucker conditions
    lpx_check_kkt = cfunc(_lpx+'check_kkt', None,
        ('lp', POINTER(LPX), 1),
        ('scaled', c_int, 1),
        ('kkt', POINTER(LPXKKT), 1),
    )

    
#=============================================================================
# Interior-point method routines
#=============================================================================

if _version >= (4, 9):
    # solve LP problem using the primal-dual interiorpoint method
    lpx_interior = cfunc(_lpx+'interior', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve status of interior-point solution
    lpx_ipt_status = cfunc(_lpx+'ipt_status', c_int,
        ('lp', POINTER(LPX), 1),
    )
    LPX_T_UNDEF = 150 # interior solution is undefined
    LPX_T_OPT = 151 # interior solution is optimal

if _version >= (4, 9):
    # retrieve objective value
    lpx_ipt_obj_val = cfunc(_lpx+'ipt_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row primal value
    lpx_ipt_row_prim = cfunc(_lpx+'ipt_row_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    lpx_ipt_row_dual = cfunc(_lpx+'ipt_row_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column primal value
    lpx_ipt_col_prim = cfunc(_lpx+'ipt_col_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    lpx_ipt_col_dual = cfunc(_lpx+'ipt_col_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

if _version >= (4, 16):
    # retrieve objective value
    glp_ipt_obj_val = cfunc(_glp+'ipt_obj_val', c_double,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve row primal value
    glp_ipt_row_prim = cfunc(_glp+'ipt_row_prim', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    glp_ipt_row_dual = cfunc(_glp+'ipt_row_dual', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve column primal value
    glp_ipt_col_prim = cfunc(_glp+'ipt_col_prim', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    glp_ipt_col_dual = cfunc(_glp+'ipt_col_dual', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )


#=============================================================================
# MIP routines
#=============================================================================

if _version >= (4, 9):
    # set (change) problem class
    lpx_set_class = cfunc(_lpx+'set_class', None,
        ('lp', POINTER(LPX), 1),
        ('klass', c_int, 1),
    )
    LPX_LP = 100 # linear programming (LP)
    LPX_MIP = 101 # mixed integer programming (MIP)
    
    # retrieve problem class
    lpx_get_class = cfunc(_lpx+'get_class', c_int,
        ('lp', POINTER(LPX), 1),
    )

if _version >= (4, 9):
    # set (change) column kind
    lpx_set_col_kind = cfunc(_lpx+'set_col_kind', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('kind', c_int, 1),
    )
    LPX_CV = 160 # continuous variable
    LPX_IV = 161 # integer variable

    # retrieve column kind
    lpx_get_col_kind = cfunc(_lpx+'get_col_kind', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve number of integer columns
    lpx_get_num_int = cfunc(_lpx+'get_num_int', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of binary columns
    lpx_get_num_bin = cfunc(_lpx+'get_num_bin', c_int,
        ('lp', POINTER(LPX), 1),
    )

if _version >= (4, 16):
    # set (change) column kind
    glp_set_col_kind = cfunc(_glp+'set_col_kind', None,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
        ('kind', c_int, 1),
    )
    GLP_CV   = 1 # continuous variable
    GLP_IV   = 2 # integer variable
    LP_BV    = 3  # binary variable

    # retrieve column kind
    glp_get_col_kind = cfunc(_glp+'get_col_kind', c_int,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )

    # retrieve number of integer columns
    glp_get_num_int = cfunc(_glp+'get_num_int', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve number of binary columns
    glp_get_num_bin = cfunc(_glp+'get_num_bin', c_int,
        ('lp', POINTER(glp_prob), 1),
    )

if _version >= (4, 9):
    # solve MIP problem using the branch-and-bound method
    lpx_integer = cfunc(_lpx+'integer', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # solve MIP problem using the branch-and-bound method
    lpx_intopt = cfunc(_lpx+'intopt', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve status of MIP solution
    lpx_mip_status = cfunc(_lpx+'mip_status', c_int,
        ('lp', POINTER(LPX), 1),
    )
    LPX_I_UNDEF = 170 # integer solution is undefined
    LPX_I_OPT = 171 # integer solution is optimal
    LPX_I_FEAS = 172 # integer solution is feasible
    LPX_I_NOFEAS = 173 # no integer solution exists

if _version >= (4, 9):
    # retrieve objective value
    lpx_mip_obj_val = cfunc(_lpx+'mip_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row value
    lpx_mip_row_val = cfunc(_lpx+'mip_row_val', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column value
    lpx_mip_col_val = cfunc(_lpx+'mip_col_val', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

if _version >= (4, 16):
    # retrieve objective value
    glp_mip_obj_val = cfunc(_glp+'mip_obj_val', c_double,
        ('lp', POINTER(glp_prob), 1),
    )

    # retrieve row value
    glp_mip_row_val = cfunc(_glp+'mip_row_val', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('i', c_int, 1),
    )

    # retrieve column value
    glp_mip_col_val = cfunc(_glp+'mip_col_val', c_double,
        ('lp', POINTER(glp_prob), 1),
        ('j', c_int, 1),
    )


#=============================================================================
# Utility routines
#=============================================================================

if _version >= (4, 9):
    # read problem data in fixed MPS format
    lpx_read_mps = cfunc(_lpx+'read_mps', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in fixed MPS format
    lpx_write_mps = cfunc(_lpx+'write_mps', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read LP basis in fixed MPS format
    lpx_read_bas = cfunc(_lpx+'read_bas', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write LP basis in fixed MPS format
    lpx_write_bas = cfunc(_lpx+'write_bas', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read problem data in free MPS format
    lpx_read_freemps = cfunc(_lpx+'read_freemps', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in free MPS format
    lpx_write_freemps = cfunc(_lpx+'write_freemps', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read problem data in CLPEX LP format
    lpx_read_cpxlp = cfunc(_lpx+'read_cpxlp', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in CLPEX LP format
    lpx_write_cpxlp = cfunc(_lpx+'write_cpxlp', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read model written in GNU MathProg modeling language
    lpx_read_model = cfunc(_lpx+'read_model', POINTER(LPX),
        ('model', c_char_p, 1),
        ('data', c_char_p, 1),
        ('output', c_char_p, 1),
    )
    
    # write problem data in plain text format
    lpx_print_prob = cfunc(_lpx+'print_prob', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write basic solution in printable format
    lpx_print_sol = cfunc(_lpx+'print_sol', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write bounds sensitivity information
    lpx_print_sens_bnds = cfunc(_lpx+'print_sens_bnds', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write interior point solution in printable format
    lpx_print_ips = cfunc(_lpx+'print_ips', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write MIP solution in printable format
    lpx_print_mip = cfunc(_lpx+'print_mip', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    

#=============================================================================
# Control parameters and statistics routines
#=============================================================================

if _version >= (4, 9):
    # reset control parameters to default values
    lpx_reset_parms = cfunc(_lpx+'reset_parms', None,
        ('lp', POINTER(LPX), 1),
    )
    
    # set (change) integer control parameter
    lpx_set_int_parm = cfunc(_lpx+'set_int_parm', None,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
        ('val', c_int, 1),
    )
    
    # query integer control parameter
    lpx_set_int_parm = cfunc(_lpx+'set_int_parm', c_int,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
    )
    
    # set (change) real control parameter
    lpx_set_real_parm = cfunc(_lpx+'set_real_parm', None,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
        ('val', c_double, 1),
    )
    
    # query real control parameter
    lpx_set_real_parm = cfunc(_lpx+'set_real_parm', c_double,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
    )
    
    # control parameter identifiers:
    LPX_K_MSGLEV    = 300   # lp->msg_lev
    LPX_K_SCALE     = 301   # lp->scale
    LPX_K_DUAL      = 302   # lp->dual
    LPX_K_PRICE     = 303   # lp->price
    LPX_K_RELAX     = 304   # lp->relax
    LPX_K_TOLBND    = 305   # lp->tol_bnd
    LPX_K_TOLDJ     = 306   # lp->tol_dj
    LPX_K_TOLPIV    = 307   # lp->tol_piv
    LPX_K_ROUND     = 308   # lp->round
    LPX_K_OBJLL     = 309   # lp->obj_ll
    LPX_K_OBJUL     = 310   # lp->obj_ul
    LPX_K_ITLIM     = 311   # lp->it_lim
    LPX_K_ITCNT     = 312   # lp->it_cnt
    LPX_K_TMLIM     = 313   # lp->tm_lim
    LPX_K_OUTFRQ    = 314   # lp->out_frq
    LPX_K_OUTDLY    = 315   # lp->out_dly
    LPX_K_BRANCH    = 316   # lp->branch
    LPX_K_BTRACK    = 317   # lp->btrack
    LPX_K_TOLINT    = 318   # lp->tol_int
    LPX_K_TOLOBJ    = 319   # lp->tol_obj
    LPX_K_MPSINFO   = 320   # lp->mps_info
    LPX_K_MPSOBJ    = 321   # lp->mps_obj
    LPX_K_MPSORIG   = 322   # lp->mps_orig
    LPX_K_MPSWIDE   = 323   # lp->mps_wide
    LPX_K_MPSFREE   = 324   # lp->mps_free
    LPX_K_MPSSKIP   = 325   # lp->mps_skip
    LPX_K_LPTORIG   = 326   # lp->lpt_orig
    LPX_K_PRESOL    = 327   # lp->presol
    LPX_K_BINARIZE  = 328   # lp->binarize
    LPX_K_USECUTS   = 329   # lp->use_cuts

if _version >= (4, 10):
    # control parameter identifiers:
    LPX_C_COVER     = 0x01  # mixed cover cuts
    LPX_C_CLIQUE    = 0x02  # clique cuts
    LPX_C_GOMORY    = 0x04  # Gomory's mixed integer cuts
    LPX_C_ALL       = 0xFF  # all cuts


#=============================================================================
# LP basis and simplex table routines
#=============================================================================

if _version >= (4, 9):
    # "warm up" LP basis
    lpx_warm_up = cfunc(_lpx+'warm_up', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # compute row of the simplex table
    lpx_eval_tab_row = cfunc(_lpx+'eval_tab_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('k', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # compute column of the simplex table
    lpx_eval_tab_col = cfunc(_lpx+'eval_tab_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('k', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # transform explicitly specified row
    lpx_transform_row = cfunc(_lpx+'transform_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # transform explicitly specified column
    lpx_transform_col = cfunc(_lpx+'transform_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # perform primal ratio test
    lpx_prim_ratio_test = cfunc(_lpx+'prim_ratio_test', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
        ('how', c_int, 1),
        ('tol', c_double, 1),
    )

    # perform dual ratio test
    lpx_dual_ratio_test = cfunc(_lpx+'dual_ratio_test', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
        ('how', c_int, 1),
        ('tol', c_double, 1),
    )


#=============================================================================
# Library environment routines
#=============================================================================

if _version >= (4, 9) and _version <= (4, 15):
    glp_version = lpx_version

if _version >= (4, 16):
    class glp_ulong(Structure):
        _fields_ = [
            ('lo', c_uint),
            ('hi', c_uint),
        ]

    # Determine library version
    glp_version = cfunc(_glp+'version', c_char_p,
    )
    
    # Terminal hook function
    glp_term_hook_func = CFUNCTYPE(c_int, c_void_p, c_char_p)

    # Determine library version
    glp_term_hook = cfunc(_glp+'term_hook', None,
        ('func', glp_term_hook_func, 1),
        ('info', c_void_p, 1),
    )
    
    # Get memory usage information
    glp_mem_usage = cfunc(_glp+'mem_usage', None,
        ('count', c_int_p, 1),
        ('cpeak', c_int_p, 1),
        ('total', POINTER(glp_ulong), 1),
        ('tpeak', POINTER(glp_ulong), 1),
    )
    
        
#=============================================================================
# Wrap up all the functions and constants into __all__
#=============================================================================
__all__ = [x for x in locals().keys() \
    if  x.startswith('lpx_') or \
        x.startswith('LPX') or \
        x.startswith('glp') or \
        x.startswith('GLP')]

if __name__ == "__main__":
    print "Welcome. You are using ctypes-glpk, a Python wrapper for GLPK written by Minh-Tri Pham."
