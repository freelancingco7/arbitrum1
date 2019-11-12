# Copyright 2019, Offchain Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import arbitrum as arb

count = 0


def runBinaryOp(vm, arg1, arg2, op):
    global count
    vm.push(arg2)
    vm.push(arg1)
    op()


def binaryOp(vm, arg1, arg2, res, op):
    runBinaryOp(vm, arg1, arg2, op)
    cmpEqual(vm, res)


def cmpEqual(vm, res):
    global count
    vm.push(res)
    vm.eq()
    vm.push(arb.ast.AVMLabel("next" + str(count)))
    vm.cjump()
    vm.error()
    vm.set_label(arb.ast.AVMLabel("next" + str(count)))
    count += 1


def cmpNotEqual(vm, res):
    global count
    vm.push(res)
    vm.eq()
    vm.iszero()
    vm.push(arb.ast.AVMLabel("next" + str(count)))
    vm.cjump()
    vm.error()
    vm.set_label(arb.ast.AVMLabel("next" + str(count)))
    count += 1


def test(vm):
    # ADD
    binaryOp(vm, 4, 3, 7, vm.add)
    #    binaryOp(vm,4,3,6,vm.add)
    binaryOp(vm, 0, 0, 0, vm.add)
    binaryOp(vm, 2 ** 256 - 1, 4, 3, vm.add)
    binaryOp(vm, 2 ** 256 - 2, 1, 2 ** 256 - 1, vm.add)
    # MUL
    binaryOp(vm, 4, 3, 12, vm.mul)
    binaryOp(vm, 3, 0, 0, vm.mul)
    binaryOp(vm, 2 ** 256 - 1, 1, 2 ** 256 - 1, vm.mul)
    binaryOp(vm, 2 ** 256 - 2, 1, 2 ** 256 - 2, vm.mul)
    # SUB
    binaryOp(vm, 4, 3, 1, vm.sub)
    binaryOp(vm, 3, 4, 2 ** 256 - 1, vm.sub)
    # DIV
    binaryOp(vm, 12, 3, 4, vm.div)
    runBinaryOp(vm, 2 ** 256 - 6, 3, vm.div)
    cmpNotEqual(vm, 4)
    # divide by 0
    vm.push(arb.ast.AVMLabel("DIV_divide_by_0_expected"))
    vm.errset()
    runBinaryOp(vm, 12, 0, vm.div)
    vm.error()
    vm.set_label(arb.ast.AVMLabel("DIV_divide_by_0_expected"))
    # SDIV
    binaryOp(vm, 12, 3, 4, vm.sdiv)
    binaryOp(vm, 12, 2 ** 256 - 3, 2 ** 256 - 4, vm.sdiv)
    binaryOp(vm, 2 ** 256 - 12, 3, 2 ** 256 - 4, vm.sdiv)
    binaryOp(vm, 2 ** 256 - 12, 2 ** 256 - 3, 4, vm.sdiv)
    # sdivide by 0
    vm.push(arb.ast.AVMLabel("SDIV_divide_by_0_expected"))
    vm.errset()
    runBinaryOp(vm, 12, 0, vm.sdiv)
    vm.error()
    vm.set_label(arb.ast.AVMLabel("SDIV_divide_by_0_expected"))
    #
    vm.halt()


code = arb.compile_block(test)
vm = arb.compile_program(arb.ast.BlockStatement([]), code)
# print(vm.code)
with open("../arb-validator/test/opcodetest.ao", "wb") as f:
    arb.marshall.marshall_vm(vm, f)
