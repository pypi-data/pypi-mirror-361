// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_SDF_SUB_LAYER_LIST_EDITOR_H
#define PXR_SDF_SUB_LAYER_LIST_EDITOR_H

/// \file sdf/subLayerListEditor.h

#include "./vectorListEditor.h"
#include "./declareHandles.h"
#include "./proxyPolicies.h"

namespace pxr {

SDF_DECLARE_HANDLES(SdfLayer);

/// \class Sdf_SubLayerListEditor
///
/// List editor implementation for sublayer path lists.
///
class Sdf_SubLayerListEditor 
    : public Sdf_VectorListEditor<SdfSubLayerTypePolicy>
{
public:
    Sdf_SubLayerListEditor(const SdfLayerHandle& owner);

    virtual ~Sdf_SubLayerListEditor();

private:
    typedef Sdf_VectorListEditor<SdfSubLayerTypePolicy> Parent;

    virtual void _OnEdit(
        SdfListOpType op,
        const std::vector<std::string>& oldValues,
        const std::vector<std::string>& newValues) const;
};

}  // namespace pxr

#endif // PXR_SDF_SUB_LAYER_LIST_EDITOR_H
