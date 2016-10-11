bl_info = {
    "name": "Select Adjacents",
    "author": "Mário Basto",
    "version": (1, 0),
    "description": "Selects the adjacent elements",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
    }

import bpy
import bmesh

from random import randint

# ----------- Class -----------
class SelectAdjacents(bpy.types.Operator):
    """Select Adjacents"""
    
    bl_idname = "mesh.select_adjacents"
    bl_label = "Select Adjacents"
    bl_options = {"REGISTER", "UNDO"}
  
    steps = bpy.props.IntProperty(name="Steps", default=1, min=1, max=20, options={"SKIP_SAVE"})
    face_step = bpy.props.BoolProperty(name="Face Step", default=True, options={"SKIP_SAVE"})
    random = bpy.props.BoolProperty(name="Random", default=False, options={"SKIP_SAVE"})
    random_perc = bpy.props.IntProperty(name="Percentage of Randomness", subtype="PERCENTAGE", default=50, min=1, max=99, options={"SKIP_SAVE"})       
     
    def updateSelection(self):
        # the actual selection list (that will become old)
        if self.select_mode[0]: # vertices
            old_sel = [el for el in self.bm.verts if el.select] 
        elif self.select_mode[1]: # edges
            old_sel = [el for el in self.bm.edges if el.select] 
        else: # faces
            old_sel = [el for el in self.bm.faces if el.select]
        
        # the new selection list    
        new_sel = list() 
        
        for element in old_sel:
            if self.select_mode[0]: # vertices
                if self.face_step:
                    elements = element.link_edges
                    new_sel.extend(element.link_edges)
                else:
                    elements = element.link_faces

            elif self.select_mode[1]: # edges
                if self.face_step:
                    elements = [edge for vert in element.verts for edge in vert.link_edges]
                else:
                    elements = [edge for vert in element.verts for edge in vert.link_faces]
                    
            else: # faces
                if self.face_step:
                    elements = [face for edge in element.edges for face in edge.link_faces]
                else:
                    elements = [face for vert in element.verts for face in vert.link_faces]
                    
            new_sel.extend(elements)
                
                              
        # select the new selection
        for sel in new_sel:
            # with self.random turn off it will be always True
            sel.select = not(self.random) or randint(0, 100) <= self.random_perc

        # unselect the old selection
        for sel in old_sel:
            # with self.random turn off it will be always False
            sel.select = self.random and randint(0, 100) <= self.random_perc
                    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        #mesh and bmesh
        self.mesh = bpy.context.edit_object.data
        self.bm = bmesh.from_edit_mesh(self.mesh)
    
        #get the type of select mode
        self.select_mode = bpy.context.scene.tool_settings.mesh_select_mode
              
        for i in range(self.steps):
            self.updateSelection()

        # update mesh
        bmesh.update_edit_mesh(self.mesh, False, False)
        
        return {'FINISHED'}   
 
# add the operator to Select -> Select Adjacents   
def add_select_adjacents_operator(self, context):
    self.layout.operator(  
        SelectAdjacents.bl_idname,  
        text=SelectAdjacents.bl_label) 

addon_kmaps = []

def register():
    bpy.utils.register_class(SelectAdjacents)
    bpy.types.VIEW3D_MT_select_edit_mesh.append(add_select_adjacents_operator)
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
    # change the shortcut here..
    kmi = km.keymap_items.new(SelectAdjacents.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl=True)
    addon_kmaps.append(km)

def unregister():
    bpy.utils.unregister_class(SelectAdjacents)
    bpy.types.VIEW3D_MT_select_edit_mesh.remove(add_select_adjacents_operator)
    
    wm = bpy.context.window_manager
    for km in addon_kmaps:
        wm.keyconfigs.addon.kmaps.remove(km)
    del addon_kmaps[:]

    
if __name__ == "__main__":
    register()
    bpy.ops.mesh.select_adjacents()
