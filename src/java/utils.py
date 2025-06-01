"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Utility functions for Java code analysis.
"""
from java.models import  JavaClass, JavaMethod

def is_valid_method( method: JavaMethod) -> bool:
    if get_class_name_from_qualified_name(method.src.class_name) == method.src.method_name:
        # constructor
        return False
    invalid_method_names = ["equals", "hashCode", "toString", "clone", "finalize", "wait", "notify", "notifyAll"]
    if method.src.method_name in invalid_method_names:
        return False
    return True

def is_valid_class( clazz: JavaClass) -> bool:
    if  clazz.class_name.endswith("Test"):
        # constructor
        return False
    return True


def get_class_name_from_qualified_name( qualified_name: str) -> str:
    """Extract class name from fully qualified name."""
    return qualified_name.split('.')[-1]