#
# Copyright (c) 2018-2021 T. {Benz,Kramer}.
#
# This file is part of verilog-parser 
# (see https://codeberg.org/tok/py-verilog-parser).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os.path


def verilog_netlist() -> str:
    """
    Get content of an example Verilog netlist.
    :return:
    """
    verilog_file = os.path.join(os.path.dirname(__file__), '../../test_data/simple_nl_ys.v')
    with open(verilog_file) as f:
        data = f.read()
    return data
