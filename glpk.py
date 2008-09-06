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
- GLPK: 4.9 to 4.30

How to use
----------
See the example below.


Changes
-------
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
def lpx_get_version(): 
    return _version

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
# Problem Object
#=============================================================================

def LPX_FIELDS():
    return [] # to be expanded in the future

class LPX(Structure):
    _fields_ = LPX_FIELDS()


#=============================================================================
# Karush-Kuhn-Tucker
#=============================================================================

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
    lpx_create_prob = cfunc('glp_lpx_create_prob', POINTER(LPX))

    # assign (change) problem name
    lpx_set_prob_name = cfunc('glp_lpx_set_prob_name', None,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # assign (change) objective function name
    lpx_set_obj_name = cfunc('glp_lpx_set_obj_name', None,
        ('lp', POINTER(LPX), 1),
        ('name', c_char_p, 1),
    )

    # set (change) optimization direction flag
    lpx_set_obj_dir = cfunc('glp_lpx_set_obj_dir', None,
        ('lp', POINTER(LPX), 1),
        ('dir', c_int, 1),
    )
    LPX_MIN = 120 # minimization
    LPX_MAX = 121 # maximization

    # add new rows to problem object
    lpx_add_rows = cfunc('glp_lpx_add_rows', c_int,
        ('lp', POINTER(LPX), 1),
        ('nrs', c_int, 1),
    )

    # add new columns to problem object
    lpx_add_cols = cfunc('glp_lpx_add_cols', c_int,
        ('lp', POINTER(LPX), 1),
        ('ncs', c_int, 1),
    )

    # assign (change) row name
    lpx_set_row_name = cfunc('glp_lpx_set_row_name', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('name', c_char_p, 1),
    )

    # assign (change) column name
    lpx_set_col_name = cfunc('glp_lpx_set_col_name', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('name', c_char_p, 1),
    )

    # set (change) row bounds
    lpx_set_row_bnds = cfunc('glp_lpx_set_row_bnds', None,
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
    lpx_set_col_bnds = cfunc('glp_lpx_set_col_bnds', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('type', c_int, 1),
        ('lb', c_double, 1),
        ('ub', c_double, 1),
    )

    # set (change) objective coefficient or constant term
    lpx_set_obj_coef = cfunc('glp_lpx_set_obj_coef', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('coef', c_double, 1),
    )

    # set (replace) row of the constraint matrix
    lpx_set_mat_row = cfunc('glp_lpx_set_mat_row', None,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # set (replace) column of the constraint matrix
    lpx_set_mat_col = cfunc('glp_lpx_set_mat_col', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # load (replace) the whole constraint matrix
    lpx_load_matrix = cfunc('glp_lpx_load_matrix', None,
        ('lp', POINTER(LPX), 1),
        ('ne', c_int, 1),
        ('ia', c_int_p, 1),
        ('ja', c_int_p, 1),
        ('ar', c_double_p, 1),
    )

    # delete rows from problem object
    lpx_del_rows = cfunc('glp_lpx_del_rows', None,
        ('lp', POINTER(LPX), 1),
        ('nrs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete columns from problem object
    lpx_del_cols = cfunc('glp_lpx_del_cols', None,
        ('lp', POINTER(LPX), 1),
        ('ncs', c_int, 1),
        ('num', c_int_p, 1),
    )

    # delete problem object
    lpx_delete_prob = cfunc('glp_lpx_delete_prob', None,
        ('lp', POINTER(LPX), 1),
    )

    
#=============================================================================
# Problem retrieving routines
#=============================================================================

if _version >= (4, 9):
    # retrieve problem name
    lpx_get_prob_name = cfunc('glp_lpx_get_prob_name', c_char_p,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve objective function name
    lpx_get_obj_name = cfunc('glp_lpx_get_obj_name', c_char_p,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve optimization direction flag
    lpx_get_obj_dir = cfunc('glp_lpx_get_obj_dir', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of rows
    lpx_get_num_rows = cfunc('glp_lpx_get_num_rows', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of columns
    lpx_get_num_cols = cfunc('glp_lpx_get_num_cols', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row name
    lpx_get_row_name = cfunc('glp_lpx_get_row_name', c_char_p,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column name
    lpx_get_col_name = cfunc('glp_lpx_get_col_name', c_char_p,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve row type
    lpx_get_row_type = cfunc('glp_lpx_get_row_type', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row lower bound
    lpx_get_row_lb = cfunc('glp_lpx_get_row_lb', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row upper bound
    lpx_get_row_ub = cfunc('glp_lpx_get_row_ub', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column type
    lpx_get_col_type = cfunc('glp_lpx_get_col_type', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column lower bound
    lpx_get_col_lb = cfunc('glp_lpx_get_col_lb', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column upper bound
    lpx_get_col_ub = cfunc('glp_lpx_get_col_ub', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve objective coefficient or constant term
    lpx_get_obj_coef = cfunc('glp_lpx_get_obj_coef', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve number of constraint coefficients
    lpx_get_num_nz = cfunc('glp_lpx_get_num_nz', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row of the constraint matrix
    lpx_get_mat_row = cfunc('glp_lpx_get_mat_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # retrieve column of the constraint matrix
    lpx_get_mat_col = cfunc('glp_lpx_get_mat_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )


#=============================================================================
# Problem scaling routines
#=============================================================================

if _version >= (4, 9):
    # scale problem data
    lpx_scale_prob = cfunc('glp_lpx_scale_prob', None,
        ('lp', POINTER(LPX), 1),
    )

    # unscale problem data
    lpx_unscale_prob = cfunc('glp_lpx_unscale_prob', None,
        ('lp', POINTER(LPX), 1),
    )


#=============================================================================
# LP basis constructing routines
#=============================================================================

if _version >= (4, 9):
    # construct standard initial LP basis
    lpx_std_basis = cfunc('glp_lpx_std_basis', None,
        ('lp', POINTER(LPX), 1),
    )

    # construct advanced initial LP basis
    lpx_adv_basis = cfunc('glp_lpx_adv_basis', None,
        ('lp', POINTER(LPX), 1),
    )

    # set (change) row status
    lpx_set_row_stat = cfunc('glp_lpx_set_row_stat', None,
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
    lpx_set_col_stat = cfunc('glp_lpx_set_col_stat', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('stat', c_int, 1),
    )
    

#=============================================================================
# Simplex method routine
#=============================================================================

if _version >= (4, 9):
    # solve LP problem using the simplex method
    lpx_simplex = cfunc('glp_lpx_simplex', c_int,
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


#=============================================================================
# Basic solution retrieving routines
#=============================================================================

if _version >= (4, 9):
    # retrieve generic status of basic solution
    lpx_get_status = cfunc('glp_lpx_get_status', c_int,
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
    lpx_get_prim_stat = cfunc('glp_lpx_get_prim_stat', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # status of primal basic solution:
    LPX_P_UNDEF = 132 # primal solution is undefined
    LPX_P_FEAS = 133 # solution is primal feasible
    LPX_P_INFEAS = 134 # solution is primal infeasible
    LPX_P_NOFEAS = 135 # no primal feasible solution exists
    
    # retrieve dual status of basic solution
    lpx_get_dual_stat = cfunc('glp_lpx_get_dual_stat', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # status of dual basic solution:
    LPX_D_UNDEF = 136 # dual solution is undefined
    LPX_D_FEAS = 137 # solution is dual feasible
    LPX_D_INFEAS = 138 # solution is dual infeasible
    LPX_D_NOFEAS = 139 # no dual feasible solution exists

    # retrieve objective value
    lpx_get_obj_val = cfunc('glp_lpx_get_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row status
    lpx_get_row_stat = cfunc('glp_lpx_get_row_stat', c_int,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row primal value
    lpx_get_row_prim = cfunc('glp_lpx_get_row_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    lpx_get_row_dual = cfunc('glp_lpx_get_row_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column status
    lpx_get_col_stat = cfunc('glp_lpx_get_col_stat', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve col primal value
    lpx_get_col_prim = cfunc('glp_lpx_get_col_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    lpx_get_col_dual = cfunc('glp_lpx_get_col_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve non-basic variable which causes unboundness
    lpx_get_ray_info = cfunc('glp_lpx_get_ray_info', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # check Karush-Kuhn-Tucker conditions
    lpx_check_kkt = cfunc('glp_lpx_check_kkt', None,
        ('lp', POINTER(LPX), 1),
        ('scaled', c_int, 1),
        ('kkt', POINTER(LPXKKT), 1),
    )

    
#=============================================================================
# LP basis and simplex table routines
#=============================================================================

if _version >= (4, 9):
    # "warm up" LP basis
    lpx_warm_up = cfunc('glp_lpx_warm_up', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # compute row of the simplex table
    lpx_eval_tab_row = cfunc('glp_lpx_eval_tab_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('k', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # compute column of the simplex table
    lpx_eval_tab_col = cfunc('glp_lpx_eval_tab_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('k', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # transform explicitly specified row
    lpx_transform_row = cfunc('glp_lpx_transform_row', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # transform explicitly specified column
    lpx_transform_col = cfunc('glp_lpx_transform_col', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
    )

    # perform primal ratio test
    lpx_prim_ratio_test = cfunc('glp_lpx_prim_ratio_test', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
        ('how', c_int, 1),
        ('tol', c_double, 1),
    )

    # perform dual ratio test
    lpx_dual_ratio_test = cfunc('glp_lpx_dual_ratio_test', c_int,
        ('lp', POINTER(LPX), 1),
        ('len', c_int, 1),
        ('ind', c_int_p, 1),
        ('val', c_double_p, 1),
        ('how', c_int, 1),
        ('tol', c_double, 1),
    )


#=============================================================================
# Interior-point method routines
#=============================================================================

if _version >= (4, 9):
    # solve LP problem using the primal-dual interiorpoint method
    lpx_interior = cfunc('glp_lpx_interior', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve status of interior-point solution
    lpx_ipt_status = cfunc('glp_lpx_ipt_status', c_int,
        ('lp', POINTER(LPX), 1),
    )
    LPX_T_UNDEF = 150 # interior solution is undefined
    LPX_T_OPT = 151 # interior solution is optimal

    # retrieve objective value
    lpx_ipt_obj_val = cfunc('glp_lpx_ipt_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row primal value
    lpx_ipt_row_prim = cfunc('glp_lpx_ipt_row_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve row dual value
    lpx_ipt_row_dual = cfunc('glp_lpx_ipt_row_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column primal value
    lpx_ipt_col_prim = cfunc('glp_lpx_ipt_col_prim', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve column dual value
    lpx_ipt_col_dual = cfunc('glp_lpx_ipt_col_dual', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )


#=============================================================================
# MIP routines
#=============================================================================

if _version >= (4, 9):
    # set (change) problem class
    lpx_set_class = cfunc('glp_lpx_set_class', None,
        ('lp', POINTER(LPX), 1),
        ('klass', c_int, 1),
    )
    LPX_LP = 100 # linear programming (LP)
    LPX_MIP = 101 # mixed integer programming (MIP)
    
    # retrieve problem class
    lpx_get_class = cfunc('glp_lpx_get_class', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # set (change) column kind
    lpx_set_col_kind = cfunc('glp_lpx_set_col_kind', None,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
        ('kind', c_int, 1),
    )
    LPX_CV = 160 # continuous variable
    LPX_IV = 161 # integer variable

    # retrieve column kind
    lpx_get_col_kind = cfunc('glp_lpx_get_col_kind', c_int,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )

    # retrieve number of integer columns
    lpx_get_num_int = cfunc('glp_lpx_get_num_int', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve number of binary columns
    lpx_get_num_bin = cfunc('glp_lpx_get_num_bin', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # solve MIP problem using the branch-and-bound method
    lpx_integer = cfunc('glp_lpx_integer', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # solve MIP problem using the branch-and-bound method
    lpx_intopt = cfunc('glp_lpx_intopt', c_int,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve status of MIP solution
    lpx_mip_status = cfunc('glp_lpx_mip_status', c_int,
        ('lp', POINTER(LPX), 1),
    )
    LPX_I_UNDEF = 170 # integer solution is undefined
    LPX_I_OPT = 171 # integer solution is optimal
    LPX_I_FEAS = 172 # integer solution is feasible
    LPX_I_NOFEAS = 173 # no integer solution exists

    # retrieve objective value
    lpx_mip_obj_val = cfunc('glp_lpx_mip_obj_val', c_double,
        ('lp', POINTER(LPX), 1),
    )

    # retrieve row value
    lpx_mip_row_val = cfunc('glp_lpx_mip_row_val', c_double,
        ('lp', POINTER(LPX), 1),
        ('i', c_int, 1),
    )

    # retrieve column value
    lpx_mip_col_val = cfunc('glp_lpx_mip_col_val', c_double,
        ('lp', POINTER(LPX), 1),
        ('j', c_int, 1),
    )


#=============================================================================
# Control parameters and statistics routines
#=============================================================================

if _version >= (4, 9):
    # reset control parameters to default values
    lpx_reset_parms = cfunc('glp_lpx_reset_parms', None,
        ('lp', POINTER(LPX), 1),
    )
    
    # set (change) integer control parameter
    lpx_set_int_parms = cfunc('glp_lpx_set_int_parms', None,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
        ('val', c_int, 1),
    )
    
    # query integer control parameter
    lpx_set_int_parms = cfunc('glp_lpx_set_int_parms', c_int,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
    )
    
    # set (change) real control parameter
    lpx_set_real_parms = cfunc('glp_lpx_set_real_parms', None,
        ('lp', POINTER(LPX), 1),
        ('parm', c_int, 1),
        ('val', c_double, 1),
    )
    
    # query real control parameter
    lpx_set_real_parms = cfunc('glp_lpx_set_real_parms', c_double,
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


#=============================================================================
# Utility routines
#=============================================================================

if _version >= (4, 9):
    # read problem data in fixed MPS format
    lpx_read_mps = cfunc('glp_lpx_read_mps', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in fixed MPS format
    lpx_write_mps = cfunc('glp_lpx_write_mps', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read LP basis in fixed MPS format
    lpx_read_bas = cfunc('glp_lpx_read_bas', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write LP basis in fixed MPS format
    lpx_write_bas = cfunc('glp_lpx_write_bas', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read problem data in free MPS format
    lpx_read_freemps = cfunc('glp_lpx_read_freemps', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in free MPS format
    lpx_write_freemps = cfunc('glp_lpx_write_freemps', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read problem data in CLPEX LP format
    lpx_read_cpxlp = cfunc('glp_lpx_read_cpxlp', POINTER(LPX),
        ('fname', c_char_p, 1),
    )
    
    # write problem data in CLPEX LP format
    lpx_write_cpxlp = cfunc('glp_lpx_write_cpxlp', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # read model written in GNU MathProg modeling language
    lpx_read_model = cfunc('glp_lpx_read_model', POINTER(LPX),
        ('model', c_char_p, 1),
        ('data', c_char_p, 1),
        ('output', c_char_p, 1),
    )
    
    # write problem data in plain text format
    lpx_print_prob = cfunc('glp_lpx_print_prob', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write basic solution in printable format
    lpx_print_sol = cfunc('glp_lpx_print_sol', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write bounds sensitivity information
    lpx_print_sens_bnds = cfunc('glp_lpx_print_sens_bnds', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write interior point solution in printable format
    lpx_print_ips = cfunc('glp_lpx_print_ips', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    
    # write MIP solution in printable format
    lpx_print_mip = cfunc('glp_lpx_print_mip', c_int,
        ('lp', POINTER(LPX), 1),
        ('fname', c_char_p, 1),
    )
    

#=============================================================================
# Wrap up all the functions and constants into __all__
#=============================================================================
__all__ = [x for x in locals().keys() if x.startswith('lpx_') or x.startswith('LPX')]

if __name__ == "__main__":
    print "Welcome. You are using ctypes-glpk, a Python wrapper for GLPK written by Minh-Tri Pham."
