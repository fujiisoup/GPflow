# Copyright 2016 James Hensman, alexggmatthews, PabloLeon, Valentine Svensson
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import tensorflow as tf
import numpy as np
from .param import Param, Parameterized


class MeanFunction(Parameterized):
    """
    The base mean function class.
    To implement a mean function, write the __call__ method. This takes a
    tensor X and returns a tensor m(X). In accordance with the GPflow
    standard, each row of X represents one datum, and each row of Y is computed
    independently for each row of X.

    MeanFunction classes can have parameters, see the Linear class for an
    example.
    """
    def __call__(self, X):
        raise NotImplementedError("Implement the __call__\
                                  method for this mean function")

    def __add__(self, other):
        return Additive(self, other)

    def __mul__(self, other):
        return Product(self, other)


class Zero(MeanFunction):
    def __call__(self, X):
        return tf.zeros(tf.pack([tf.shape(X)[0], 1]), dtype='float64')


class Linear(MeanFunction):
    """
    y_i = A x_i + b
    """
    def __init__(self, A=np.ones((1, 1)), b=np.zeros(1)):
        """
        A is a matrix which maps each element of X to Y, b is an additive
        constant.

        If X has N rows and D columns, and Y is intended to have Q columns,
        then A must be D x Q, b must be a vector of length Q.
        """
        MeanFunction.__init__(self)
        self.A = Param(np.atleast_2d(A))
        self.b = Param(b)

    def __call__(self, X):
        return tf.matmul(X, self.A) + self.b


class Constant(MeanFunction):
    """
    y_i = c,,
    """
    def __init__(self, c=np.zeros(1)):
        MeanFunction.__init__(self)
        self.c = Param(c)

    def __call__(self, X):
        shape = tf.pack([tf.shape(X)[0], 1])
        return tf.tile(tf.reshape(self.c, (1, -1)), shape)


class Additive(MeanFunction):
    def __init__(self, first_part, second_part):
        MeanFunction.__init__(self)
        self.add_1 = first_part
        self.add_2 = second_part

    def __call__(self, X):
        return tf.add(self.add_1(X), self.add_2(X))


class Product(MeanFunction):
    def __init__(self, first_part, second_part):
        MeanFunction.__init__(self)

        self.prod_1 = first_part
        self.prod_2 = second_part

    def __call__(self, X):
        return tf.mul(self.prod_1(X), self.prod_2(X))
