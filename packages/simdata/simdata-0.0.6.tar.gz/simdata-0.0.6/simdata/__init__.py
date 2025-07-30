#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024  darryl mcculley

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pydantic import BaseModel, ConfigDict
from polars import DataFrame

from .sim import simd_func, int as sim_int, float as sim_float, choice as sim_choice, literal as sim_literal

class simd (BaseModel):
    model_config = ConfigDict(extra="allow")

    def __init__(self, **data):
        super().__init__(**data)
        simd_funcs = {f.__name__:f for f in simd_func.__subclasses__()}
        for field, value in self.__pydantic_extra__.items():
            if isinstance(value, dict) and "func" in value:
                func_type = value["func"]
                func_class = simd_funcs.get(func_type)
                if func_class: 
                    setattr(self, field, func_class(**value))

    def simulate(self, n:int=1):
        sim_data = [{ 
            field: getattr(self, field).simulate()
            for field in sorted(self.model_fields_set)
        } for _ in range(n)]
        if n == 1: return sim_data[0]
        else: return sim_data

def build(data: DataFrame):
    sim_fields = {}
    for col in data.columns:
        values = data[col].to_list()
        dtype = data[col].dtype
        dtype_str = str(dtype)
        if dtype_str.startswith("Int"):
            sim_fields[col] = sim_int.create(values=values)
        elif dtype_str.startswith("Float"):
            sim_fields[col] = sim_float.create(values=values)
        elif dtype_str == "Utf8":
            sim_fields[col] = sim_choice.create(values=values)
        elif dtype_str == "Boolean":
            sim_fields[col] = sim_choice.create(values=[str(v) for v in values])
        else:
            if all(v == values[0] for v in values):
                sim_fields[col] = sim_literal.create(value=values[0])
            else:
                sim_fields[col] = sim_choice.create(values=[str(v) for v in values])
    return simd(**sim_fields)
