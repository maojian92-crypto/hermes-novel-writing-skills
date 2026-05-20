#!/usr/bin/env python3
"""
novel-config.yaml 读取工具
所有写作技能统一使用此工具读取项目配置
"""

import yaml
import os
import re
from pathlib import Path


def find_config(start_path="."):
    """
    从起始路径向上查找 novel-config.yaml
    返回找到的目录路径，找不到返回 None
    """
    current = Path(start_path).resolve()
    while current != current.parent:
        config_file = current / "novel-config.yaml"
        if config_file.exists():
            return str(current)
        current = current.parent
    return None


def load_config(project_path=None):
    """
    加载 novel-config.yaml
    
    Args:
        project_path: 项目路径，None 时自动查找
    
    Returns:
        dict: 配置字典
    """
    if project_path is None:
        project_path = find_config()
        if project_path is None:
            raise FileNotFoundError("未找到 novel-config.yaml，请确认在项目目录内或提供项目路径")
    
    config_path = Path(project_path) / "novel-config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 解析变量
    config = resolve_variables(config, config)
    
    # 展开路径
    config = expand_paths(config, project_path)
    
    # 清理被错误展开为路径的纯字符串值
    config = strip_path_prefix(config)
    
    return config


def resolve_string(s, root_config):
    """解析配置中的变量引用，如 {project.id}"""
    if not isinstance(s, str):
        return s
    
    # 匹配 {path.to.value} 或 {path.to.value:format}
    pattern = r'\{([\w.]+)(?::([^}]+))?\}'
    
    def replacer(match):
        key_path = match.group(1)
        fmt = match.group(2) or ""
        
        # 从 root_config 中获取值
        keys = key_path.split('.')
        value = root_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return match.group(0)  # 找不到，保持原样
        
        if fmt:
            try:
                return format(value, fmt)
            except:
                return str(value)
        return str(value)
    
    return re.sub(pattern, replacer, s)


def resolve_variables(config, root_config):
    """解析配置中的变量引用"""
    def traverse(obj):
        if isinstance(obj, dict):
            return {k: traverse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [traverse(item) for item in obj]
        elif isinstance(obj, str):
            return resolve_string(obj, root_config)
        return obj
    
    return traverse(config)


def expand_paths(config, project_path):
    """展开 ~ 等路径变量，但保留纯字符串值不变"""
    def expand(obj):
        if isinstance(obj, dict):
            return {k: expand(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [expand(item) for item in obj]
        elif isinstance(obj, str):
            # 只展开 ~ 为家目录
            expanded = os.path.expanduser(obj)
            # 如果是相对路径，才拼接项目路径
            if not os.path.isabs(expanded):
                # 检查是否是纯名称（不含路径分隔符）
                if os.path.sep not in obj and '/' not in obj:
                    # 纯文件名或目录名，拼接项目路径
                    expanded = os.path.join(project_path, expanded)
                else:
                    # 包含路径分隔符，保持原样（相对路径）
                    pass
            return os.path.normpath(expanded)
        return obj
    
    return expand(config)


def strip_path_prefix(config):
    """
    清理配置中因 expand_paths 而被错误添加路径前缀的纯字符串值。
    例如：project.name 被展开成了绝对路径，需要恢复为纯字符串。
    """
    def strip_value(obj, is_path_field=False):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # 标记哪些字段是纯字符串，不应该有路径前缀
                pure_string_fields = {
                    'project': ['name', 'id', 'status'],
                    'narrative': ['pov', 'label', 'description', 'ratio'],
                    'characters': ['name', 'id', 'reason', 'description', 'type', 'limb'],
                    'word_count': ['min', 'pass', 'target_min', 'target_max', 'excellent'],
                    'anti_ai': ['adverb_threshold', 'emotion_label_threshold', 
                               'explain_threshold', 'template_repeat_limit'],
                    'terminology': ['allowed_english', 'allowed_traditional', 'character_names'],
                }
                
                # 检查当前字段是否应该保持纯字符串
                should_be_pure = False
                for section, fields in pure_string_fields.items():
                    if k in fields:
                        should_be_pure = True
                        break
                
                result[k] = strip_value(v, is_path_field=should_be_pure)
            return result
        elif isinstance(obj, list):
            return [strip_value(item) for item in obj]
        elif isinstance(obj, str) and is_path_field:
            # 如果是纯字符串字段，但包含了路径分隔符，提取最后一部分
            if os.path.sep in obj:
                return os.path.basename(obj)
            return obj
        return obj
    
    return strip_value(config)


def get_file_path(config, file_type, key=None):
    """
    获取文件路径
    
    Args:
        config: 配置字典
        file_type: 文件类型 (outline, truth_file, chapter, etc.)
        key: 子键（如 truth_file 的 core/team/quest 等）
    
    Returns:
        str: 文件路径（已展开为绝对路径）
    """
    files = config.get('files', {})
    
    if file_type == 'outline':
        outlines = files.get('outlines', [])
        return outlines[0] if outlines else None
    
    elif file_type == 'truth_file':
        truth_files = files.get('truth_files', {})
        if key and key in truth_files:
            return truth_files[key]
        return None
    
    elif file_type == 'chapters_dir':
        return files.get('chapters_dir', 'chapters')
    
    elif file_type == 'references_dir':
        return files.get('references_dir', 'references')
    
    elif file_type == 'progress':
        return files.get('progress_file', '创作进度.md')
    
    elif file_type == 'synopsis':
        return files.get('synopsis', 'synopsis.md')
    
    return None


def get_project_name(config):
    """获取项目名称（纯字符串，不带路径）"""
    name = config.get('project', {}).get('name', '')
    if os.path.sep in str(name):
        return os.path.basename(name)
    return name


def get_protagonist_name(config):
    """获取主角名称（纯字符串，不带路径）"""
    name = config.get('characters', {}).get('protagonist', {}).get('name', '')
    if os.path.sep in str(name):
        return os.path.basename(name)
    return name


def get_chapter_path(config, chapter_num, chapter_title=""):
    """
    生成章节文件路径
    
    Args:
        config: 配置字典
        chapter_num: 章节号
        chapter_title: 章节标题（可选）
    
    Returns:
        str: 章节文件完整路径
    """
    pattern = config.get('naming', {}).get('chapter_pattern', '第{chapter_num:03d}章-{chapter_title}.md')
    chapters_dir = get_file_path(config, 'chapters_dir')
    
    filename = pattern.format(chapter_num=chapter_num, chapter_title=chapter_title)
    return os.path.join(chapters_dir, filename)


def get_character_names(config):
    """获取所有角色名列表（返回纯名称，不带路径）"""
    chars = config.get('characters', {})
    names = []
    
    protagonist = chars.get('protagonist', {})
    if protagonist and 'name' in protagonist:
        name = protagonist['name']
        # 如果 name 是路径（被 expand_paths 处理过），提取最后一部分
        if os.path.sep in str(name):
            name = os.path.basename(name)
        names.append(name)
    
    for member in chars.get('team', []):
        if 'name' in member:
            name = member['name']
            if os.path.sep in str(name):
                name = os.path.basename(name)
            names.append(name)
    
    for antagonist in chars.get('antagonists', []):
        if 'name' in antagonist:
            name = antagonist['name']
            if os.path.sep in str(name):
                name = os.path.basename(name)
            names.append(name)
    
    for absent in chars.get('absent', []):
        if 'name' in absent:
            name = absent['name']
            if os.path.sep in str(name):
                name = os.path.basename(name)
            names.append(name)
    
    return names


def get_absent_characters(config):
    """获取已死亡/离开的角色列表"""
    return config.get('characters', {}).get('absent', [])


def get_character_checks(config, character_name):
    """获取角色的检查规则"""
    chars = config.get('characters', {})
    
    # 检查主角
    protagonist = chars.get('protagonist', {})
    if protagonist.get('name') == character_name:
        return protagonist.get('checks', [])
    
    # 检查团队成员
    for member in chars.get('team', []):
        if member.get('name') == character_name:
            return member.get('checks', [])
    
    return []


# 测试代码
if __name__ == "__main__":
    import sys
    
    # 测试万界求生
    wanjie_path = os.path.expanduser("~/.hermes/workspace/novels/万界求生")
    if os.path.exists(wanjie_path):
        print("=== 万界求生 ===")
        config = load_config(wanjie_path)
        print(f"项目名: {get_project_name(config)}")
        print(f"主角: {get_protagonist_name(config)}")
        print(f"大纲: {get_file_path(config, 'outline')}")
        print(f"章节目录: {get_file_path(config, 'chapters_dir')}")
        names = get_character_names(config)
        print(f"角色列表: {names}")
        print(f"角色数: {len(names)}")
        print()
    
    # 测试无尽进化
    endless_path = os.path.expanduser("~/writing/novels/endless-evolution")
    if os.path.exists(endless_path):
        print("=== 无尽进化 ===")
        config = load_config(endless_path)
        print(f"项目名: {get_project_name(config)}")
        print(f"主角: {get_protagonist_name(config)}")
        print(f"大纲: {get_file_path(config, 'outline')}")
        print(f"章节目录: {get_file_path(config, 'chapters_dir')}")
        names = get_character_names(config)
        print(f"角色列表: {names}")
        print(f"角色数: {len(names)}")
        print()
    
    print("配置读取工具测试完成")
