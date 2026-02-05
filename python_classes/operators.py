from bpy.utils import register_class, unregister_class
import bpy

from .resources.node_groups import distribute_leaves


class ExecuteNodeFunction(bpy.types.Operator):
    bl_idname = "mtree.node_function"
    bl_label = "Node Function callback"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    function_name : bpy.props.StringProperty()

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if node_group is None:
            self.report({'ERROR'}, f"Node group '{self.node_tree_name}' not found.")
            return {'CANCELLED'}

        node = node_group.nodes.get(self.node_name)
        if node is None:
            self.report({'ERROR'}, f"Node '{self.node_name}' not found.")
            return {'CANCELLED'}

        function = getattr(node, self.function_name, None)
        if function is None:
            self.report({'ERROR'}, f"Action '{self.function_name}' is unavailable.")
            return {'CANCELLED'}

        try:
            function()
        except Exception as exc:
            self.report({'ERROR'}, f"Failed to execute action: {exc}")
            return {'CANCELLED'}
        return {'FINISHED'}


class AddLeavesModifier(bpy.types.Operator):
    bl_idname = "mtree.add_leaves"
    bl_label = "Add leaves distribution modifier to tree"
    bl_options = {'REGISTER', 'UNDO'}

    object_id: bpy.props.StringProperty()

    def execute(self, context):
        ob = bpy.data.objects.get(self.object_id)
        if ob is None:
            self.report({'ERROR'}, f"Object '{self.object_id}' not found.")
            return {'CANCELLED'}

        try:
            distribute_leaves(ob)
        except Exception as exc:
            self.report({'ERROR'}, f"Failed to add leaves: {exc}")
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    register_class(ExecuteNodeFunction)
    register_class(AddLeavesModifier)

def unregister():
    unregister_class(ExecuteNodeFunction)
    unregister_class(AddLeavesModifier)
