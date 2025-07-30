# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import importlib
import json


class dt_json:
    @staticmethod
    def dumps(obj):
        d = obj.__dict__ if hasattr(obj, "__dict__") else obj
        d["__class__"] = obj.__class__.__name__
        return json.dumps(d)

    @classmethod
    def loads(cls, json_str):
        d = json.loads(json_str)
        class_name = d.get("__class__")
        module = importlib.import_module("datatailr")
        if class_name and hasattr(module, class_name):
            target_class = getattr(module, class_name)
            obj = target_class.__new__(target_class)
            if hasattr(obj, "from_json"):
                obj.from_json(d)
                return obj
            # fallback: set attributes directly
            for k, v in d.items():
                if k != "__class__":
                    setattr(obj, k, v)
            return obj
        return d  # fallback to dict if not registered

    @classmethod
    def load(cls, json_file):
        return json.load(json_file)
