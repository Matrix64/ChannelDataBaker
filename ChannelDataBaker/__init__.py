import importlib
import inspect
import sys

import bpy

bl_info = {
    "name": "Channel Data Baker",
    "version": (1, 0, 0),
    "author": "matrix64",
    "blender": (3, 50, 0),
    "location": "3D Viewport > Sidebar > Tool",
    "description": "",
    "category": "Tool",
}

module_names = ["panel",
                "cdb_utils",
                "data_merge_transform",
                "batch_smart_pivot",
                "batch_active_attribute",
                "data_merge_linear_mask"]


class CDBPanelContext(bpy.types.PropertyGroup):
    items = [
        ("TRANSFORM", "Transform", "Transform", "EMPTY_ARROWS", 0),
        ("LINEAR_MASK", "Linear mask", "Linear mask", "MOD_MASK", 1),
        ("UTILS", "Utils", "Utils", "SHADERFX", 2),
    ]
    panel_enums: bpy.props.EnumProperty(
        items=(items),
        name="Addon Panels",
    )


class TransformProperty(bpy.types.PropertyGroup):
    channelToggle: bpy.props.BoolProperty(name="Pass Transform",
                                          description="",
                                          default=True)
    Mode: bpy.props.EnumProperty(name="Mode",
                                 description="",
                                 items=[('UV', "UV", ""),
                                        ('vCol', "vCol", "")])
    uvCh: bpy.props.IntProperty(name="UV Map",
                                default=0,
                                min=0,
                                max=7,
                                step=1,
                                description="Set the index of UV Map")
    scalePrecision: bpy.props.IntProperty(name="Scale Precision",
                                          default=4096,
                                          min=1,
                                          max=8192,
                                          step=1,
                                          description="Set the scale of pack number")
    axisPackGrp: bpy.props.EnumProperty(name="Pack Axis",
                                        description="",
                                        items=[('XY', "XY", ""),
                                               ('XZ', "XZ", ""),
                                               ('YZ', "YZ", "")])
    ChannelUV: bpy.props.EnumProperty(name="ChannelUV",
                                      description="",
                                      items=[('U', "U", ""),
                                             ('V', "V", "")])
    ChannelRGB: bpy.props.EnumProperty(name="ChannelRGB",
                                       description="",
                                       items=[('R', "R", ""),
                                              ('G', "G", ""),
                                              ('B', "B", ""),
                                              ('A', "A", "")])
    TransformOrientation: bpy.props.EnumProperty(name="ChannelUV",
                                      description="",
                                      items=[('Global', "Global", ""),
                                             ('Local', "Local", "")])


class CDBPropertyGroup(bpy.types.PropertyGroup):
    PosPackMode: bpy.props.EnumProperty(name="PackMode",
                                        description="",
                                        items=[('Individual', "Individual", ""),
                                               ('AB Pack', "AB Pack", ""),
                                               ('XYZ Pack', "XYZ Pack", "")])
    transformX: bpy.props.PointerProperty(type=TransformProperty)
    transformY: bpy.props.PointerProperty(type=TransformProperty)
    transformZ: bpy.props.PointerProperty(type=TransformProperty)
    linearMaskX: bpy.props.PointerProperty(type=TransformProperty)
    linearMaskY: bpy.props.PointerProperty(type=TransformProperty)
    linearMaskZ: bpy.props.PointerProperty(type=TransformProperty)
    transformAB: bpy.props.PointerProperty(type=TransformProperty)
    transformXYZ: bpy.props.PointerProperty(type=TransformProperty)
    pivotXScale: bpy.props.FloatProperty(name="Pivot X Scale")
    previewAttribute: bpy.props.StringProperty(name="Active Preview Attribute")


classes = [TransformProperty, CDBPropertyGroup, CDBPanelContext]


def register():
    namespace = {}
    for name in module_names:
        fullname = '{}.{}.{}'.format(__package__, "lib", name)
        if fullname in sys.modules:
            namespace[name] = importlib.reload(sys.modules[fullname])
        else:
            namespace[name] = importlib.import_module(fullname)

    for module in module_names:
        for module_class in [obj for name, obj in inspect.getmembers(namespace[module]) if inspect.isclass(obj)]:
            if module_class not in classes:
                classes.append(module_class)

    for cls in classes:
        if not hasattr(bpy.types, cls.__name__):
            bpy.utils.register_class(cls)
        # print("### register module ### " + cls.__name__)

    bpy.types.Scene.CDB_props = bpy.props.PointerProperty(type=CDBPropertyGroup)
    bpy.types.Scene.CDB_panel = bpy.props.PointerProperty(type=CDBPanelContext)

    print("### Channel Data Baker ### register success")


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
        #     print("### unregister module ### " + cls.__name__)
        # else:
        #     print("### class not registered ### " + cls.__name__)

    if hasattr(bpy.types.Scene, 'CDB_props'):
        del bpy.types.Scene.CDB_props
    if hasattr(bpy.types.Scene, 'CDB_panel'):
        del bpy.types.Scene.CDB_panel
    classes.clear()

    print("### Channel Data Baker ### unregister success")


if __name__ == "__main__":
    register()
