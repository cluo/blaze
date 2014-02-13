from __future__ import print_function, division, absolute_import

import unittest
from datashape import dshape

from blaze import add, multiply, eval, py2help
from blaze.io.sql import from_table, db
from blaze.io.sql.tests.testutils import create_sqlite_table

import numpy as np

class TestSQL(unittest.TestCase):

    def setUp(self):
        self.conn = create_sqlite_table()

        self.col_i = from_table('testtable', 'i',
                                dshape('a, int64'),
                                self.conn)
        self.col_msg = from_table('testtable', 'msg',
                                  dshape('a, string'),
                                  self.conn)
        self.col_price = from_table('testtable', 'price',
                                    dshape('a, float64'),
                                    self.conn)

    @py2help.skipIf(db is None, 'pyodbc is not installed')
    def test_query(self):
        expr = add(self.col_i, self.col_i)
        result = eval(expr)
        self.assertEqual([int(x) for x in result], [8, 16, 32])

    #@py2help.skipIf(db is None, 'pyodbc is not installed')
    #def test_query_exec(self):
    #    print("establishing connection...")
    #    conn = interface.SciDBShimInterface('http://192.168.56.101:8080/')
    #    print(conn)
    #
    #    a = zeros(ds, conn)
    #    b = ones(ds, conn)
    #
    #    expr = a + b
    #
    #    graph, ctx = expr.expr
    #    self.assertEqual(graph.dshape, dshape('10, 10, float64'))
    #
    #    result = eval(expr)
    #    print(result)


if __name__ == '__main__':
    unittest.main()
