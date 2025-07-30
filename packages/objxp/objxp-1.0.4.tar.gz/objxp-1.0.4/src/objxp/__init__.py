import os
import json
import sys
import shutil
from typing import Literal, Optional, Union


def get_terminal_size_shutil():
    return shutil.get_terminal_size((80, 20))  # Default width and height

terminal_size = get_terminal_size_shutil()

initial_classes = {

    'func' : [
        "function",
        "module",
    ],
    
    'data' : [
        "int",
        "float",
        "bool",
        "str",
        "list",
        "dict",
        "set",
        "tuple",
    ],
    
    'builtin' : [
        "builtin_function_or_method",
    ],
    
    'other' : [
        "type",
        "method-wrapper",
        "nonetype"
    ]
}

    
resjson = {
    "objname":"",
    "objitms":[]
}


def safe_type(obj, attr):
    try:
        return str(type(getattr(obj, attr)))
    except Exception:
        return "unavailable"
    
def title_case(content: str, level: int = 1, outputType: str = "screen") -> str:
    """
    Convert the first letter of each word in the string to uppercase.
    """
    if level == 1:
        if outputType == "screen":
            return "\n\033[1;44m "+content+" \033[0m\n\n"
        else:
            # For markdown output
            return "\n## "+content+"\n\n"
    elif level == 2:
        # For level 2, we assume the content is a type name
        typename = content[8:-2].upper()  # Remove the "class " prefix and ">" suffix
        if outputType == "screen":
            return "\n"*2+" "*2+"\033[1;40;34m "+typename+" \033[0m\033[40;34mmembers: \033[0m\n"
        else:
            # For markdown output
            return "\n "+typename+" mmembers:\n"
        
def ox(
        theobj: object="test", 
        ifprint = True, 
        savefile: str | None = 'both', 
        show_inner_members: str = 'none', # none show both, True show only inner members, False show only outer members
        show_onlyknown: bool = False, 
        bygroup: bool = True
        ):
    """
    function ox list members of theobj

    param theobj: what to explor
    param savefile: "md", "json", "both", None, if save the results to a file (md or json, or both of 2).
    param show_inner_members: '_'(内部方法,_开头), '__'(私有方法,__开头), 'both'(_,__), 'dunder'(首尾都是__, 特殊方法), 'none'(only outer members), other string, show all.
    param show_onlyknown: True ( 不包括非典型的自定义成员 ), False ( 包括非典成员 ), if only show known members of the object.
    param ifprint: True, False, if print the results on console.

    return: str results.

    """

    winww = terminal_size.columns-2
    # print(f'Width: {terminal_size.columns}, Height: {terminal_size.lines}')
    strBreakLine = "_"*winww+"\n"

    resjson["objname"]=str(theobj)
    
    result_content_text_screen = "\n"
    result_content_text_screen += strBreakLine
    result_content_text_screen += title_case("OBJ'S TYPE: ",1,"screen")
    result_content_text_screen += " "*4+str(type(theobj))+"\n"
    result_content_text_screen += strBreakLine
    result_content_text_screen += title_case("OBJ'S MEMBERS: ",1,"screen")
    print(result_content_text_screen) if ifprint else None

    result_content_text_md = ""
    result_content_text_md += strBreakLine
    result_content_text_md += title_case("OBJ'S TYPE: ",1,"md")
    result_content_text_md += " "*4+str(type(theobj))+"\n"
    result_content_text_md += strBreakLine
    result_content_text_md += title_case("OBJ'S MEMBERS: ",1,"md")

    lstSortedMembers = sorted(
        dir(theobj), 
        key=lambda x: safe_type(theobj,x)
        )

    previous_type_str = ""

    typesWithEachTypesMembers = []
    # typesWithEachTypesMembers: 
    # list of two elements: [typeName:str, members_of_this_type:list]

    atypeitm = []
    
    for objMember in lstSortedMembers:
        current_type_str = safe_type(theobj,objMember)

        if (previous_type_str != current_type_str):

            typesWithEachTypesMembers.append([current_type_str,[]])
            
            attrtype_all = initial_classes.get(current_type_str, ["other"])
            
            previous_type_str = current_type_str

        typesWithEachTypesMembers[-1][1].append(objMember)

    resjson["objitms"]=typesWithEachTypesMembers

    for aTypeWithThisTypesMembers in typesWithEachTypesMembers:
        
        typeName = aTypeWithThisTypesMembers[0]
        
        members = ""
        classified_members = {}
        for aMember in aTypeWithThisTypesMembers[1]:
                
            # 处理内部成员过滤
            is_dunder = aMember.startswith('__') and aMember.endswith('__')  # 特殊方法
            is_private = aMember.startswith('_') and not aMember.startswith('__')  # 单下划线
            is_very_private = aMember.startswith('__') and not aMember.endswith('__')  # 双下划线

            # 根据show_inner_members参数过滤
            if show_inner_members == 'none':
                # 不显示任何内部成员
                if aMember.startswith('_'):
                    continue
            elif show_inner_members == '_':
                # 只显示单下划线受保护的成员，不显示双下划线私有和首尾双下划线特殊方法
                if not is_private or is_dunder or is_very_private:
                    continue
            elif show_inner_members == '__':
                # 只显示双下划线成员，不显示单下划线和特殊方法
                if not is_very_private or is_dunder:
                    continue
            elif show_inner_members == 'dunder':
                # 只特殊方法
                if not is_dunder:
                    continue
            # 'both' 显示所有成员，不需要过滤
            
            # 处理名称修饰（name mangling）
            display_name = aMember
            if is_very_private and not isinstance(theobj, type):
                # 对于实例对象，需要处理名称修饰
                cls_name = theobj.__class__.__name__
                display_name = f"_{cls_name}{aMember}"
            
            # # 分类成员
            # category, subcategory, value = classify_member(theobj, aMember)
            
            # # 如果只显示已知类型且当前类型为'other'，则跳过
            # if show_onlyknown and category == 'other':
            #     continue
            
            # # 将成员添加到分类中
            # if category not in classified_members:
            #     classified_members[category] = []
            # classified_members[category].append({
            #     'name': display_name,
            #     'type': subcategory,
            #     'value': value
            # })

            members += display_name + ", "

        if members.endswith(", "):  
        
            result_content_text_md += title_case(typeName,2,"md")
            result_content_text_screen += title_case(typeName,2,"screen")

            members = members[:-2]  
            result_content_text_md += members
            result_content_text_screen += members

            print(result_content_text_screen)

    if savefile == "md" or savefile == "both":
        with open("objxp"+".md",'w', encoding="UTF-8") as ff:
            ff.write(result_content_text_md)

    if savefile == "json" or savefile == "both":
        with open("objxp"+".json",'w', encoding="UTF-8") as ff:
            ff.write(json.dumps(resjson))
    
    return result_content_text_md

# vars() is alternative to dirs(), or locals()

def what_is_vars():
    locals = vars().copy()
    for kk,vv in locals.items():
        print(kk,type())

    helpinfo = """
    vars() 是 Python 内置的一个函数，用于返回对象的 dict 属性，这是一个包含对象属性和它们值的字典。对于大多数 Python 对象，vars() 返回的是对象的命名空间。如果对象没有 dict 属性，比如内置类型或没有定义 dict 的自定义对象，vars() 将引发 TypeError。

    例如：
    ```python
    class MyClass:
        def __init__(self):
            self.a = 1
            self.b = 2

    obj = MyClass()
    print(vars(obj))  # 输出: {'a': 1, 'b': 2}
    ```
    在没有参数的情况下调用 vars()，它等价于 locals()，返回当前作用域中的局部符号表，也是一个字典。

    例如：
    ```python
    def my_function():
        x = 10
        y = 20
        print(vars())  # 输出: {'x': 10, 'y': 20}

    my_function()

    ```
    总结一下，vars() 主要用于获取对象的属性字典或当前作用域的局部符号表。


    """


def hlp(objtgt,mdff=""):
    mdff = "./tmp.md" if mdff == "" else mdff
    out = sys.stdout
    sys.stdout = open(mdff, 'w')
    help(objtgt)
    sys.stdout.close()
    sys.stdout = out

        
if __name__=="__main__":
    help(100)
