import bpy

class MTREE_PT_Sidebar(bpy.types.Panel):
    bl_label = "Mtree Troubleshooting"
    bl_idname = "MTREE_PT_sidebar"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Mtree'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'mt_MtreeNodeTree'

    def draw(self, context):
        layout = self.layout
        
        # Status Section
        col = layout.column(align=True)
        col.label(text="Native Module Status:")
        try:
            from .. import m_tree
            col.label(text="Connected", icon='CHECKMARK')
        except:
            col.label(text="Disconnected", icon='ERROR')
            box = col.box()
            box.label(text="Build required!", icon='INFO')
        
        layout.separator()
        
        # Tools Section
        col = layout.column(align=True)
        col.label(text="Tools:")
        col.operator("mtree.report_diagnostics", text="Run Diagnostics", icon='INFO')
        
        layout.separator()
        
        # Resources Section
        col = layout.column(align=True)
        col.label(text="Resources:")
        col.operator("wm.url_open", text="GitHub Repo", icon='URL').url = "https://github.com/MaximeHerpin/modular_tree"
        col.operator("wm.url_open", text="Documentation", icon='HELP').url = "https://github.com/MaximeHerpin/modular_tree#readme"

def register():
    bpy.utils.register_class(MTREE_PT_Sidebar)

def unregister():
    bpy.utils.unregister_class(MTREE_PT_Sidebar)
