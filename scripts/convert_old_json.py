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

                    
def convert_data(data, first=False):
    
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = convert_data(data[i])
            
    elif isinstance(data, dict):
        if first:
            new = []
            for n, v in data.items():
                if isinstance(v, dict) and n != "items":
                    v.prepend('name', n)
                new.append(convert_data(v))
            data = new

        else:
            for n, v in data.items():
                if isinstance(v, dict) and n != "items":
                    v.prepend('name', n)

    return data
                
            
if __name__ == '__main__':
    import os
    # dir_path = r"A:\packages\perso\qargparser\dev\examples"
    # for n in os.listdir(dir_path):
    #     path = os.path.join(dir_path, n)
    #     if not path.endswith('.json'):
    #         continue
    #     print(path)
    #     dst_path = path
        
    #     with open(path, "r") as f:
    #         data = json.load(f, object_pairs_hook=OrderedDict)
            
    #     data = convert_data(data, first=True)
        
    #     with open(dst_path, "w") as f:
    #         json.dump(data, f, indent=4)

        