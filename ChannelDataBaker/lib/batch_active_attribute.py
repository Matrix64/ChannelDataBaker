import bmesh
import bpy

class BatchActiveAttribute(bpy.types.Operator):
    bl_idname = "object.batch_active_attribute"
    bl_label = "Batch Active Attribute"

    def execute(self, context):
        props = context.scene.CDB_props
        attribute_name = props.previewAttribute

        for obj in bpy.context.selected_objects:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            color_layer = bm.loops.layers.color.get(attribute_name)
            if color_layer is not None:
                obj.data.vertex_colors.active_index = bm.loops.layers.color.keys().index(attribute_name)
            bm.to_mesh(obj.data)
            bm.free()
        return {'FINISHED'}
