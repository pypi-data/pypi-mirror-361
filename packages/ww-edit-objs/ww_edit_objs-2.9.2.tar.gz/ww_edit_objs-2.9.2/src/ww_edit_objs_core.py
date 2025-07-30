import copy
import os.path as osp
from typing import Optional

# 3rd party
import dryable
import kkpyutil as util

# project
from miautil import service
from miautil import dryop
from miawwise.src import wwise as wu

_cm = util.init_repo(__file__, organization='_miatech')
_wobj_doc_url = 'https://www.audiokinetic.com/zh/library/?source=SDK&id=wobjects_index.html.'


def main(args):
    return service.run_core_session(args, _cm.ancestorDirs[1], validate_args, Worker)


def validate_args(args, logger=_cm.logger):
    fixed_args = copy.deepcopy(args)
    res = service.Result(logger=logger)

    fixed_args.inputObjList = util.lazy_load_listfile(args.inputObjList)

    if not args.allowCustomProperty:
        if not (property_data_type := wu.WWISE_PROPERTY_DATA_TYPE_MAP.get(args.property)):
            res.detail = f'非法的属性名: {args.property}'
            res.advice = f'检查输入的属性名. 参考文档: {_wobj_doc_url}'
            res.throw(KeyError)

        try:
            fixed_args.value = wu.convert_to_python_type(args.value, property_data_type)
        except ValueError as e:
            res.detail = f'对 `{args.property}` 传入非法的属性值: {args.value}'
            res.advice = 'Value 的格式与属性相关, 参考 Value 的 Tooltip'
            res.throw(ValueError)

    if args.enableRandomizer:
        if args.randomizerMinOffset > 0:
            res.detail = f'Randomizer min offset 应不大于0, 当前值: {args.randomizerMinOffset}'
            res.advice = '将 randomizer min offset 设置为不大于0的值'
            res.throw(ValueError)
        if args.randomizerMaxOffset < 0:
            res.detail = f'Randomizer max offset 应不小于0, 当前值: {args.randomizerMaxOffset}'
            res.advice = '将 randomizer max offset 设置为不小于0的值'
            res.throw(ValueError)

    return fixed_args


class Worker(service.WorkerBase):
    def __init__(self, session):
        super().__init__(session)
        self.nSteps = 3
        self.client: Optional[wu.WaapiClient] = None
        self.objectList: list[dict] = []
        self.propertyConflictedObjectList: list[dict] = []

    def main(self):
        with wu.WaapiClient() as self.client:
            self._query_objects()
            self._find_conflicts()
            self._resolve_property_conflict()

        self._save_object_list()

        self.res.succeeded = True

        self.res.detail = f'The following objects have property conflict, will {self.args.conflictResolution}\n'
        self.res.detail += '\n'.join(['- ' + obj['path'] for obj in self.propertyConflictedObjectList])
        self.res.detail += f'为 {len(self.objectList)} 个对象设置了属性:\n' + \
                           '\n'.join(['- ' + obj["path"] for obj in self.objectList])
        self.res.advice = '检查工程中这些对象的属性'
        return self.res, self.out

    def _query_objects(self):
        self.step_progress('querying objects')
        self.objectList = self.client.query_objects(self.args.inputObjList,
                                                    opt_props=[f'@{self.args.property}'])
        if self.args.inputObjList and not self.objectList:
            missing_obj = [obj for obj in self.args.inputObjList if not self.client.obj_exists(obj)]
            self.res.detail = '查询对象失败'
            self.res.advice = '无法查询到以下对象, 确保它们存在且格式无误: \n' + '\n'.join(missing_obj)
            self.res.throw(ValueError)

    def _find_conflicts(self):
        def update_object_overrider(_obj):
            """
            Find the overrider of the property and update the object with the overrider name and value.
            e.g. if the property is `@BelowThresholdBehavior`, the overrider is `@OverrideVirtualVoice`
            """
            property_info = self.client.query_object_property_info(_obj['id'], self.args.property)

            overrider = None
            for dep in property_info.get('dependencies') or []:
                if dep['type'] == 'override':
                    overrider = dep['property']
                    break

            overrider_value = False if overrider is None else \
                self.client.query_by_guid([_obj['id']], opt_props=[f'@{overrider}'])[0].get(f'@{overrider}')

            _obj['overrider'] = overrider
            _obj['overrider_enabled'] = overrider_value

        def property_conflicted(_obj):
            property_is_effective = (is_relative_property := _obj['overrider'] is None) or \
                                    _obj['overrider_enabled'] or \
                                    (is_top_level_obj := self.client.is_top_level_object(_obj['id']))
            return not property_is_effective

        for obj in self.objectList:
            update_object_overrider(obj)
            obj['propertyConflicted'] = property_conflicted(obj)
            if obj['propertyConflicted']:
                self.propertyConflictedObjectList.append(obj)

    def _resolve_property_conflict(self):
        def failAtOnce(_obj):
            self.res.detail = f'以下对象的属性与父级冲突:\n'
            self.res.detail += '\n'.join(['- ' + o['path'] for o in self.propertyConflictedObjectList])
            self.res.advice = '移动对象到顶层, 或启用 Override Parent, 或者选择其他的 conflict resolution'
            self.res.throw(ValueError)

        def acceptParent(_obj):
            # don't set property means accept parent.
            pass

        def overrideParent(_obj):
            self.client.set_property(_obj['id'], _obj['overrider'], True)
            self._set_property_for_obj(_obj)

        solution_map = {
            'failAtOnce': failAtOnce,
            'acceptParent': acceptParent,
            'overrideParent': overrideParent,
        }
        solution = solution_map[self.args.conflictResolution]

        for obj in self.objectList:
            if obj['propertyConflicted']:
                solution(obj)
            else:
                self._set_property_for_obj(obj)

    def _set_property_for_obj(self, obj):
        self.client.set_property(obj['id'], self.args.property, self.args.value)
        if self.args.enableRandomizer:
            self.client.set_randomizer(obj['id'], self.args.property,
                                       min_offset=self.args.randomizerMinOffset,
                                       max_offset=self.args.randomizerMaxOffset)

    def _save_object_list(self):
        self.out.passedObjList = osp.join(self.pathMan.paths.sessionDir, 'passed_object.list')
        dryop.save_lines(self.out.passedObjList, self.args.inputObjList, addlineend=True)
