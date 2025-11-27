# -*- coding: utf-8 -*-
"""Mapping dictionaries from legacy Student OS CSV headers to new Notion property schema."""

# (header_in_csv): (new_property_name, new_property_type)
# new_property_type one of: title, select, multi_select, date, number, relation, rich_text, url

KNOWLEDGE_MAPPING = {
    "标题": ("名称", "title"),
    "关键知识点": ("说明摘要", "rich_text"),
    "日期": ("最近更新日期", "date"),
    "笔记类型": ("类别", "select"),
    "课程": ("标签", "multi_select"),
    "重要程度": ("重要程度", "select"),
}

TASKS_MAPPING = {
    "任务标题": ("任务名称", "title"),
    "优先级": ("优先级", "select"),
    "关联课程": ("关联知识点", "relation"),
    "截止日期": ("截止日期", "date"),
    "状态": ("状态", "select"),
    "预计用时": ("预计用时", "number"),
}

RESOURCES_MAPPING = {
    "名称": ("名称", "title"),
    "描述": ("摘要", "rich_text"),
    "标签": ("标签", "multi_select"),
    "添加日期": ("添加日期", "date"),
    "状态": ("使用状态", "select"),
    "类型": ("类型", "select"),
    "编程语言": ("编程语言", "multi_select"),
    "重要程度": ("重要程度", "select"),
    "难度等级": ("难度等级", "select"),
    "链接": ("URL", "url"),
    "课堂笔记": ("关联知识点", "relation"),
}

COURSE_MAPPING = {
    "课程名称": ("课程名称", "title"),
    "上课地点": ("上课地点", "rich_text"),
    "上课时间": ("上课时间", "rich_text"),
    "任课教师": ("任课教师", "rich_text"),
    "学分": ("学分", "number"),
    "开课学期": ("开课学期", "select"),
    "教材信息": ("教材信息", "rich_text"),
}

ASSIGNMENT_MAPPING = {
    "作业标题": ("任务名称", "title"),
    "优先级": ("优先级", "select"),
    "作业要求": ("说明摘要", "rich_text"),
    "备注": ("备注", "rich_text"),
    "完成状态": ("状态", "select"),
    "截止日期": ("截止日期", "date"),
    "所属课程": ("关联知识点", "relation"),
    "预计用时": ("预计用时", "number"),
}

# Unified registry for dynamic selection
MAPPING_REGISTRY = {
    "knowledge": KNOWLEDGE_MAPPING,
    "tasks": TASKS_MAPPING,
    "resources": RESOURCES_MAPPING,
    "courses": COURSE_MAPPING,
    "assignments": ASSIGNMENT_MAPPING,
}

def get_mapping(kind: str):
    return MAPPING_REGISTRY.get(kind, {})
