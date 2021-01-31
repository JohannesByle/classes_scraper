from xml.etree import ElementTree
import os
import json


def print_recursive(node, tab=0):
    if isinstance(node, tuple):
        indent = "".join(["\t"] * tab)
        if isinstance(node[1], list):
            print(indent + str(node[0]))
            [print_recursive(n, tab + 1) for n in node[1]]
        else:
            print(indent + str(node))
    else:
        [print_recursive(n, tab + 1) for n in node]


def parse_rule(rule):
    children = [n.tag for n in rule]
    label = rule.attrib["Label"]
    if rule.attrib["RuleType"] == "IfStmt":
        is_else = "IfElsePart" in children and rule[children.index("IfElsePart")].text == "ElsePart"
        boolean = rule[children.index("BooleanEvaluation")].text == "True"
        requirement_children = rule.find("Requirement")
        requirement_children_tags = [n.tag for n in requirement_children]
        name = "ElsePart" if (is_else or not boolean) and "ElsePart" in requirement_children_tags else "IfPart"
        return parse_xml(requirement_children[requirement_children_tags.index(name)])
    elif rule.attrib["RuleType"] == "Course":
        if len(rule.findall("Requirement")) > 1:
            raise Exception("More than one requirement")
        return label, parse_req(rule.find("Requirement"))
    elif rule.attrib["RuleType"] == "Group":
        return (label, rule.find("Requirement").attrib["NumGroups"]), parse_xml(rule)
    else:
        return label, parse_xml(rule)


def parse_req(req):
    if req.attrib["Class_cred_op"] != "OR":
        raise Exception("Not or exception")
    return [(n.attrib["Disc"], n.attrib["Num"]) for n in req.findall("Course")]


def parse_xml(node):
    if node.tag == "Block" and node.attrib["Req_type"] == "DEGREE":
        return
    return [n for n in [parse_rule(n) if n.tag == "Rule" else parse_xml(n) for n in node] if n]


def convert_xml():
    requirements_json = {}
    reqs_dir = "data/requirements"
    for file in os.listdir(reqs_dir):
        requirements_json[file.replace(".xml", "")] = parse_xml(ElementTree.parse(reqs_dir + "/" + file).getroot())
    with open("data/requirements.json", "w") as f:
        json.dump(requirements_json, f)