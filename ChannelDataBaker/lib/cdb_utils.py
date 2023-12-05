def prepare_uv_channel(transform, active_obj):
    if transform.uvCh < len(active_obj.data.uv_layers):
        uv_layer = active_obj.data.uv_layers[transform.uvCh]
        # 如果UV通道已存在，则重命名为"pos_UVMap"
        if uv_layer.data:
            uv_layer.name = "cdb_UVMap"
        return uv_layer
    else:
        return active_obj.data.uv_layers.new(name="cdb_UVMap")
