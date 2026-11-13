import bpy,json
data={}
for n in ['19_GearLift_Ground','20_GearLift_Scenery','23_GearLift_Moving','13_Extended_Floors']:
 c=bpy.data.collections.get(n)
 if c:
  data[n]=[{'name':o.name,'pos':[round(v,2) for v in o.location],'dim':[round(v,2) for v in o.dimensions]} for o in c.all_objects if o.type=='MESH' and 70<o.location.x<100]
print('LIFT_DATA',json.dumps(data))
