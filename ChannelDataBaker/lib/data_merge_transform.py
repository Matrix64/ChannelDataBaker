import math

import bmesh
import bpy

from ChannelDataBaker.lib.cdb_utils import prepare_uv_channel


class DataMergeTransform(bpy.types.Operator):
    bl_idname = "object.data_merge_transform"
    bl_label = "Bake transform data"

    def execute(self, context):
        # 获取当前选中的所有物体
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            return {'CANCELLED'}

        props = context.scene.CDB_props
        # 获取当前模式
        mode = context.active_object.mode
        # 如果在编辑模式，切换到对象模式
        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for activeObj in selected_objects:
            if props.PosPackMode == 'Individual':
                for axis in ['X', 'Y', 'Z']:
                    transform = getattr(props, f"transform{axis}")
                    if transform.Mode == 'UV':
                        pack_to_uv_individual(transform, activeObj, activeObj, axis)
                    elif transform.Mode == 'vCol':
                        # 获取这些物体的x轴坐标的最大值
                        x_values = [obj.location.x for obj in selected_objects]
                        max_x = (max(x_values))
                        min_x = (min(x_values))

                        final_max_x = max(abs(max_x), abs(min_x))
                        context.scene.CDB_props.pivotXScale = final_max_x

                        pack_to_color_individual(transform, final_max_x, activeObj, axis)
            elif props.PosPackMode == 'AB Pack':
                transform = props.transformAB
                pack_to_uv_ab(transform, activeObj, activeObj)
            elif props.PosPackMode == 'XYZ Pack':
                transform = props.transformXYZ
                pack_to_uv_xyz(transform, activeObj, activeObj)
        # elif props.PosPackMode == 'AB Pack':
        #     return {'CANCELLED'}
        #         elif props.PosPackMode == 'XYZ Pack':

        # 执行完操作后，切换回原来的模式
        bpy.ops.object.mode_set(mode=mode)
        return {'FINISHED'}


def pack_to_uv_individual(transform, target_obj, active_obj, axis):
    if transform.channelToggle:
        uv_channel = prepare_uv_channel(transform, active_obj)
        # 遍历每个UV点
        for uv_loop in uv_channel.data:
            # 将UV点移动到指定的x和y坐标
            if transform.ChannelUV == 'U':
                uv_loop.uv.x = getattr(target_obj.location, axis.lower())
            else:
                uv_loop.uv.y = getattr(target_obj.location, axis.lower())


def pack_to_uv_ab(transform, target_obj, active_obj):
    if transform.channelToggle:
        uv_channel = prepare_uv_channel(transform, active_obj)
        # 遍历每个UV点
        for uv_loop in uv_channel.data:
            # 将UV点移动到指定的x和y坐标
            if transform.ChannelUV == 'U':
                if transform.axisPackGrp == 'XY':
                    uv_loop.uv.x = vec2_to_float([target_obj.location[0], target_obj.location[1]],
                                                 transform.scalePrecision)
                elif transform.axisPackGrp == 'XZ':
                    uv_loop.uv.x = vec2_to_float([target_obj.location[0], target_obj.location[2]],
                                                 transform.scalePrecision)
                else:  # 'YZ'
                    uv_loop.uv.x = vec2_to_float([target_obj.location[1], target_obj.location[2]],
                                                 transform.scalePrecision)
            else:
                if transform.axisPackGrp == 'XY':
                    uv_loop.uv.y = vec2_to_float([target_obj.location[0], target_obj.location[1]],
                                                 transform.scalePrecision)
                elif transform.axisPackGrp == 'XZ':
                    uv_loop.uv.y = vec2_to_float([target_obj.location[0], target_obj.location[2]],
                                                 transform.scalePrecision)
                else:  # 'YZ'
                    uv_loop.uv.y = vec2_to_float([target_obj.location[1], target_obj.location[1]],
                                                 transform.scalePrecision)


def pack_to_uv_xyz(transform, target_obj, active_obj):
    if transform.channelToggle:
        uv_channel = prepare_uv_channel(transform, active_obj)
        # 遍历每个UV点
        for uv_loop in uv_channel.data:
            # 将UV点移动到指定的x和y坐标
            if transform.ChannelUV == 'U':
                uv_loop.uv.x = vec3_to_float(target_obj.location)
            else:
                uv_loop.uv.y = vec3_to_float(target_obj.location)


def linear_to_srgb(color):
    if color <= 0.0031308:
        return color * 12.92
    else:
        return 1.055 * (color ** (1 / 2.4)) - 0.055


def vec3_to_float(input_vec3):
    resized_vec3 = (math.ceil(((input_vec3[0] + 1) / 2) * 100), math.ceil(((input_vec3[1] + 1) / 2) * 100),
                    math.ceil(((input_vec3[2] + 1) / 2) * 100))
    return resized_vec3[0] * 10 + resized_vec3[1] * 0.1 + resized_vec3[2] * 0.001


def float_to_vec3(input_float):
    outputX = input_float * 0.001 * 2 - 1
    outputY = (input_float * 0.1 - math.floor(input_float * 0.1)) * 2 - 1
    outputZ = (input_float * 10 - math.floor(input_float * 10)) * 2 - 1

    return [outputX, outputY, outputZ]


def vec2_to_float(input_vec2, precision):
    # precision = 4096
    precisionminusone = precision - 1
    inputfloat1 = round((input_vec2[0] + 1) / 2 * precisionminusone)
    inputfloat2 = round((input_vec2[1] + 1) / 2 * precisionminusone)
    return (inputfloat1 * precision) + inputfloat2


# def float_to_vec2(input_float, precision):
#     precision = 4096
#
#     x = input_float // precision
#     y = input_float % precision
#     output = (x / (precision - 1) * 2 - 1, y / (precision - 1) * 2 - 1)
#     return output


def pack_to_color_individual(transform, max_x, target_obj, axis):
    if max_x == 0:
        return
    if transform.channelToggle:
        rawData = getattr(target_obj.location, axis.lower())
        target_data = ((rawData / max_x) + 1) / 2
        target_data_srgb = linear_to_srgb(target_data)
        bm = bmesh.new()
        bm.from_mesh(target_obj.data)
        color_layer = bm.loops.layers.color.get("cbd_vcolor")
        if not color_layer:
            color_layer = bm.loops.layers.color.new("cbd_vcolor")

        if transform.ChannelRGB == 'R':
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer][0] = target_data_srgb
        elif transform.ChannelRGB == 'G':
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer][1] = target_data_srgb
        elif transform.ChannelRGB == 'B':
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer][2] = target_data_srgb
        elif transform.ChannelRGB == 'A':
            for face in bm.faces:
                for loop in face.loops:
                    loop[color_layer][3] = target_data_srgb
        bm.to_mesh(target_obj.data)
        bm.free()


class DeletePosVColor(bpy.types.Operator):
    bl_idname = "object.delete_pos_vcolor"
    bl_label = "Delete vCol Attribute"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            return {'CANCELLED'}
        delete_pos_vcolor(selected_objects)
        return {'FINISHED'}


def delete_pos_vcolor(target_objs):
    for target_obj in target_objs:
        # 获取当前模式
        mode = target_obj.mode
        # 如果在编辑模式，切换到对象模式
        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(target_obj.data)
        color_layers = bm.loops.layers.color.keys()
        for color_layer in color_layers:
            if "cbd_vcolor" in color_layer:
                bm.loops.layers.color.remove(bm.loops.layers.color[color_layer])
        bm.to_mesh(target_obj.data)
        bm.free()

        # 执行完操作后，切换回原来的模式
        bpy.ops.object.mode_set(mode=mode)


class DeletePosUVMap(bpy.types.Operator):
    bl_idname = "object.delete_pos_uvmap"
    bl_label = "Delete UV Attribute"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            return {'CANCELLED'}
        delete_pos_uvmap(selected_objects)
        return {'FINISHED'}


def delete_pos_uvmap(target_objs):
    for target_obj in target_objs:
        uv_layers = target_obj.data.uv_layers
        for uv_layer in uv_layers:
            if "cdb_UVMap" in uv_layer.name:
                uv_layers.remove(uv_layer)


class GetPivotXScale(bpy.types.Operator):
    bl_idname = "object.get_pivot_x_scale"
    bl_label = "Get pivot x scale"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            return {'CANCELLED'}
        x_values = [obj.location.x for obj in selected_objects]

        max_x = (max(x_values))
        min_x = (min(x_values))

        final_max_x = max(abs(max_x), abs(min_x))

        context.scene.CDB_props.pivotXScale = final_max_x
        return {'FINISHED'}
