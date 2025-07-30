// Copyright 2025 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/sdf/pathExpression.h>
#include <pxr/vt/array.h>
#include <pxr/vt/wrapArray.h>
#include <pxr/vt/valueFromPython.h>

namespace pxr {

namespace Vt_WrapArray {
    template <>
    std::string GetVtArrayName< VtArray<SdfPathExpression> >() {
        return "PathExpressionArray";
    }
}

template<>
SdfPathExpression VtZero() {
    return SdfPathExpression();
}

}  // namespace pxr

using namespace pxr;

void wrapArrayPathExpression() {
    VtWrapArray<VtArray<SdfPathExpression> >();
    VtValueFromPythonLValue<VtArray<SdfPathExpression> >();
}
