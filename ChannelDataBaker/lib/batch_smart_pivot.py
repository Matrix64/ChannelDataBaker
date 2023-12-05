import bpy


class BatchSmartPivot(bpy.types.Operator):
    bl_idname = "object.batch_smart_pivot"
    bl_label = "Batch Smart Pivot"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # 确保在编辑模式下
        if context.object.mode == 'EDIT':
            selected_objects = context.selected_objects
            for obj in selected_objects:
                # 取消选择所有物体
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')

                # 选择当前要处理的物体并设置为活动物体
                obj.select_set(True)
                context.view_layer.objects.active = obj

                # 切换回编辑模式
                bpy.ops.object.mode_set(mode='EDIT')

                # 检查物体是否有选定的元素
                if bpy.context.object.data.total_vert_sel > 0:
                    # 保存当前3D光标的位置
                    cursor_init_loc = context.scene.cursor.location.copy()

                    # 计算所选元素的中心并将3D光标移动到该位置
                    bpy.ops.view3d.snap_cursor_to_selected()

                    # 切换到对象模式并设置原点到3D光标的位置
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                    # 将3D光标恢复到初始位置并返回编辑模式
                    context.scene.cursor.location = cursor_init_loc
                    bpy.ops.object.mode_set(mode='EDIT')

            # 重新选择所有被执行的物体
            bpy.ops.object.mode_set(mode='OBJECT')
            for obj in selected_objects:
                obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')

        else:
            # 计算并设置原点到质心
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        return {'FINISHED'}
