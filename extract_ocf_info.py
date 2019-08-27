import sys
import json
import re
from lxml import etree


regex = re.compile(r'[\n\r\t]')


def get_attribute_value(element, xpath_pattern, default_value):
    part = element.xpath(xpath_pattern)
    if part:
        return part[0]
    else:
        return default_value

def get_element_value(element, xpath_pattern, default_value):
    part = element.xpath(xpath_pattern)
    if part:
        return part[0].text
    else:
        return default_value
    

def clean_string(text):
    return regex.sub(' ',text.strip())
    
def get_param_info_orig(param):
    result = {}
    result['name'] = get_attribute_value(param,"@name","").strip()
    result['title'] = clean_string(get_element_value(param, "shortdesc", ""))
    result['descripion'] = clean_string(get_element_value(param, "longdesc", ""))
    result['required'] = (get_attribute_value(param, "@required", False) == '1')
    result['unique'] = (get_attribute_value(param, "@unique", False) == '1')
    result['content_type'] = get_attribute_value(param, "content/@type",None) 
    result['default_value'] = get_attribute_value(param, "content/@default",None)
    return result

    
def get_actions(actions):
    result = []
    for action in actions:
        result.append(action)
    return result



def main(argv):
    print(str(argv))
    
    if len(argv) == 2:
        tree = etree.parse(argv[1])
    else:
        tree = etree.parse(sys.stdin)
        
    name = tree.xpath("/resource-agent/@name")[0].strip()
    longdesc = clean_string(tree.xpath("/resource-agent/longdesc")[0].text)
    shortdesc = clean_string(tree.xpath("/resource-agent/shortdesc")[0].text)

    params = []
    for param in tree.xpath("/resource-agent/parameters/parameter"):
        params.append(get_param_info_orig(param))

    actions = get_actions(tree.xpath("/resource-agent/actions/action/@name"))

    result = {}
    result['name'] = name
    result['resource'] = "ocf:heartbeat:"+name
    result['title'] = shortdesc
    result['description'] = longdesc 
    result['params'] = params
    result['actions'] =  actions

    print(json.dumps(result, sort_keys=False, indent=2))

    
if __name__ == "__main__":
    main(sys.argv)


