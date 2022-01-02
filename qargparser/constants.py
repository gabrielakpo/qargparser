#Icons
import os
_root = os.path.dirname(__file__)
RELOAD_ICON = os.path.join(_root, "icons", "reload.png")

NAMES_ORDER = [
    "name", 
    "type", 
    "description", 
    "min", 
    "max", 
    "step",
    "slider",
    "buttonLabel",
    "searchMessage",
    "enums",
    "enumsDescriptions",
    "default",
    "items"]

DEFAULT_DATA = {
    "array":{
        "default" : [],
        "min" : 0,
        "max" : 10000,
        "buttonLabel" : "Add Item",
        "items" : {},
    },
        "arrayobject":{
        "default" : [],
        "min" : 0,
        "max" : 10000,
        "buttonLabel" : "Add Item",
        "items" : [],
    },
    "integer":{
        "default" : 0,
        "step" : 1,
        "min" : -10000,
        "max" : 10000,
        "slider" : False
    },
    "float":{
        "default" : 0.0,
        "step" : 0.1,
        "min" : -10000.0,
        "max" : 10000.0,
        "slider" : False
    },
    "path":{
        "default" : "",
        "buttonLabel" : "...",
        "searchMessage" : "Choose path"
    },
    "enum":{
        "default" : "",
        "enums" : [],
        "enumsDescriptions" : []
    },
    "text": {
        "default" : ""
    },
    "doc": {
        "default" : ""
    },
    "code": {
        "default" : ""
    },
    "python": {
        "default" : "#Python"
    },
    "mel": {
        "default" : "//Mel"
    },
    "boolean":{
        "default" : False
    },
    "item":{
        "default" : None,
        "template" : {}
    },
    "string":{
        "default" : ""
    }
}