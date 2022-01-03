from collections import OrderedDict as Od
import json 

class OrderedDict(Od):
    def prepend(self, key, value, dict_setitem=dict.__setitem__):
        root = self._OrderedDict__root
        first = root[1]

        if key in self:
            link = self._OrderedDict__map[key]
            link_prev, link_next, _ = link
            link_prev[1] = link_next
            link_next[0] = link_prev
            link[0] = root
            link[1] = first
            root[1] = first[0] = link
        else:
            root[1] = first[0] = self._OrderedDict__map[key] = [root, first, key]
            dict_setitem(self, key, value)

    def to_dict(self):
        return json.loads(json.dumps(self))

                    
def convert_structure(data, first=True):
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = convert_structure(data[i], first=False)
            
    elif isinstance(data, dict):
        new = []
        for n, v in data.items():
            if isinstance(v, dict) and n not in ["items", "template"]:
                v = OrderedDict(v)
                v.prepend('name', n)
            new.append(convert_structure(v, first=False))

        if first:
            data = new

    return data

def convert_stringEnum_to_enum(data):
    for d in data:
        if d["type"] == "string" and "enum" in d:
            d["type"] = "enum"
            d["enums"] = d["enum"]
            d.pop("enum")
        
        if "items" in d and isinstance(d["items"], list):
            d["items"] = convert_stringEnum_to_enum(d["items"])

    return data

def convert_array(data):
    if isinstance(data, list):
        for d in data:
            convert_array(d)
    else:
        if (data["type"] == "array" 
            and "items" in data 
            and isinstance(data["items"], dict) 
            and data["items"]["type"] == "item"):
                if "template" in data["items"]:
                    #Array
                    if isinstance(data["items"]["template"], list):
                        data["items"] = data["items"]["template"][0]
                        data["default"] = [v[0] for v in data["default"]]
                    #Array item
                    elif isinstance(data["items"]["template"], dict):
                        data["items"]["type"] = "object"
                        data["items"]["items"] = convert_structure(data["items"]["template"])
                        data["items"].pop("template")

        if "items" in data:
            data["items"] = convert_array(data["items"])

    return data
                
if __name__ == '__main__':
    import os
    # dir_path = r"A:\packages\perso\qargparser\dev\examples"
    # paths = [os.path.join(dir_path, name) for name in os.listdir(dir_path)]
    paths = []
    for path in paths:
        if not path.endswith('.json'):
            continue
        print("convert: %s..."%path)
        dst_path = path
        
        with open(path, "r") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)
            
        try:
            print("\tconvert structure...")
            data = convert_structure(data)
            print("\tconvert stringEnum to enum...")
            data = convert_stringEnum_to_enum(data)
            print("\tconvert array...")
            data = convert_array(data)

            with open(dst_path, "w") as f:
                json.dump(data, f, indent=4)

        except:
            import traceback
            traceback.print_exc()

            
        

        