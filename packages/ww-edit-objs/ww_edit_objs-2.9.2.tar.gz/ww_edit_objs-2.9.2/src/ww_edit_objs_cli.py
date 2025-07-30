import os.path as osp

# 3rd party
import kkpyutil as util

# project
_cm = util.init_repo(__file__, organization='_miatech')
from miautil import service
from miautil import typemap as tm
_serv_name = osp.basename(_cm.ancestorDirs[1])
core = util.safe_import_module(f'{_serv_name}_core', _cm.srcDir)


def get_program_info():
    """
    Return program info as part of CLI help message.
    - description: what the program does in one sentence
    - examples: most-frequently-used commandline parameters and purposes
    - remarks: user cautions such as environment setup and known limitations
    """
    description = '为传入的 wwise object 按类型筛选后设置属性值'
    examples = """
# 将传入的对象 volume 设置为 -3
run.bat -i obj -p Volume -v -3
# 将传入的对象 SeekPercent 设为 0-100 随机
run.bat -i obj -p SeekPercent -v 0 -r --randomizer-min-offset 0 --randomizer-max-offset 100
"""
    remarks = """\
- Wwise 属性数据类型:
    - null, 无论 value 输入什么都将被认为是 null
    - string, 将 value 作为字符串原样输入
    - number, 将 value 转为 float 传入
    - boolean, value 可以使用 true/false
- Wwise 对象类型及属性参考: https://www.audiokinetic.com/zh/library/?source=SDK&id=wobjects_index.html.
"""
    return description, examples, remarks


def add_arguments(parser):
    """
    add service arguments here; all fields shown in examples are mandatory:
    - short switch: use single letter, except '-D', '-S', '-C', reserved for shared switches
    - long switch: use all-lowercase dash-delimited human-readable phrases, as this is the node editor UI caption
    - dest: must use camelCase; can use shorter words than long switch
    - type: use python type, or type-alias defined in typemap.py; bool needs no type if "action" is'store_true' or 'store_false'
    - help: explain the purposes of the argument in Chinese; will appear in Flow user doc
    - If "dest" is an in-port of the service's FBP node, then add it to inputArgs in your_service_schema.json
    parser.add_argument(
        '-n',
        '--name',
        action='store',
        dest='name',
        type=str,
        default='',
        required=True,
        help='用户名'
    )
    # boolean argument
    parser.add_argument(
        '-e',
        '--enabled',
        action='store_true',
        dest='enabled',
        default=False,
        required=False,
        help='启用的功能'
    )
    # list argument
    parser.add_argument(
        '-l',
        '--my-int-list',
        action='store',
        nargs='*',
        dest='mylist',
        type=int,
        default=[],
        required=False,
        help='整数列表'
    )
    # options
    parser.add_argument(
        '-s',
        '--single-option',
        action='store',
        choices=('en', 'zh', 'jp'),
        dest='singleOption',
        default='zh',
        type=str,
        required=False,
        help='单选参数须提供一列选项，用标量作为默认值'
    )
    parser.add_argument(
        '-m',
        '--multiple-options',
        action='store',
        nargs='+',
        choices=(1, 2, 3),
        type=int,
        dest='multiOptions',
        default=[1, 3],
        required=False,
        help='多选参数须提供一列选项，用 list 类型作为默认值'
    )
    parser.add_argument(
        '-f',
        '--typed-file',
        action='store',
        dest='typedFile',
        type=tm.tFile,
        default='',
        required=False,
        help='用自定义类型指定 type 字段用于自动映射节点端口'
    )
    """
    parser.add_argument(
        '-i',
        '--input-object-list',
        action='store',
        dest='inputObjList',
        type=tm.tWobjList,
        default='',
        required=True,
        help='要设置属性的 Object 表单, 可以是 guid 或 path（详见配置一节中对表单的说明）.'
    )
    parser.add_argument(
        '-c',
        '--allow-custom-property',
        action='store_true',
        dest='allowCustomProperty',
        default=False,
        required=False,
        help='要设置的属性是否为自定义属性, 若勾选, 则跳过属性类型检查.'
    )
    parser.add_argument(
        '-p',
        '--property',
        action='store',
        dest='property',
        type=str,
        default='',
        required=True,
        help='要设置属性的名, 不同类型的对象有不同的属性可以设置, 可以参考: https://www.audiokinetic.com/zh/library/?source=SDK&id=wobjects_index.html.'
    )
    parser.add_argument(
        '-v',
        '--value',
        action='store',
        dest='value',
        type=str,
        default='',
        required=True,
        help='''属性目标值, 格式规范受属性数据类型影响, 属性数据类型可以参考: https://www.audiokinetic.com/zh/library/?source=SDK&id=wobjects_index.html.:
- string, 将 value 作为字符串原样输入
- number, 将 value 转为 int/float 传入
- bool, value 可以使用 true/false'''
    )
    parser.add_argument(
        '-R',
        '--child-parent-property-conflict-resolution',
        action='store',
        choices=('failAtOnce', 'acceptParent', 'overrideParent'),
        dest='conflictResolution',
        type=str,
        default='failAtOnce',
        required=False,
        help='''当要设置的对象的属性与父级冲突时的解决方案：
- failAtOnce: 如果发现冲突则立即报错。
- acceptParent: 接受父级的属性, 不设置当前子级对象。
- overrideParent: 自动启用 Override Parent 并设置属性。'''
    )
    parser.add_argument(
        '-r',
        '--enable-randomizer',
        action='store_true',
        dest='enableRandomizer',
        default=False,
        required=False,
        help='为设置的属性启用 randomizer (仅 Wwise 2019 及以上).'
    )
    parser.add_argument(
        '--randomizer-min-offset',
        action='store',
        dest='randomizerMinOffset',
        type=int,
        default=0,
        required=False,
        help='Randomizer 的最小偏移值. 仅当勾选 Enable Randomizer 时生效.'
    )
    parser.add_argument(
        '--randomizer-max-offset',
        action='store',
        dest='randomizerMaxOffset',
        type=int,
        default=0,
        required=False,
        help='Randomizer 的最大偏移值. 仅当勾选 Enable Randomizer 时生效.'
    )


def main():
    desc, examples, remarks = get_program_info()
    parser = service.ArgParser(desc, examples, remarks, add_arguments)
    args = parser.main()
    core.main(args)


if __name__ == '__main__':
    main()
