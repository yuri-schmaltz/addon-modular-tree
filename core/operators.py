import sys
from .resources.node_groups import distribute_leaves
from .logger import get_logger, get_log_file

logger = get_logger()


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
    bl_label = "Add leaves"
    bl_description = "Adds a Geometry Nodes modifier to the tree for leaf distribution"
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


class MTREE_OT_ReportDiagnostics(bpy.types.Operator):
    bl_idname = "mtree.report_diagnostics"
    bl_label = "Mtree Diagnostics"
    bl_description = "Generate a diagnostic report for troubleshooting"
    bl_options = {'REGISTER'}

    def execute(self, context):
        log_file = get_log_file()
        report = []
        report.append("--- MTREE DIAGNOSTIC REPORT ---")
        report.append(f"Blender Version: {bpy.app.version_string}")
        report.append(f"Python Version: {sys.version}")
        report.append(f"Platform: {platform.platform()}")
        report.append(f"Addon Version: {bpy.context.preferences.addons.get('modular_tree', {}).get('version', 'Unknown')}")
        
        # Check native module
        try:
            from .. import m_tree
            report.append(f"Native Module Status: LOADED ({m_tree.__file__})")
        except Exception as e:
            report.append(f"Native Module Status: FAILED ({e})")

        report.append(f"Log File Location: {log_file}")
        
        # Print to console and show message
        print("\n".join(report))
        
        # Add logs to the report if file exists
        if log_file.exists():
            with open(log_file, 'r') as f:
                report.append("\n--- LATEST LOGS ---")
                report.extend(f.readlines()[-20:]) # last 20 lines

        self.report({'INFO'}, f"Diagnostics sent to console. Log: {log_file}")
        
        # Copy to clipboard if possible
        try:
            bpy.context.window_manager.clipboard = "\n".join(report)
            self.report({'INFO'}, "Report copied to clipboard!")
        except:
            pass
            
        return {'FINISHED'}


CLASSES = [
    ExecuteNodeFunction,
    AddLeavesModifier,
    MTREE_OT_ReportDiagnostics
]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
