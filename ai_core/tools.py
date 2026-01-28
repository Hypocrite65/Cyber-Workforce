# 版本: v1.1
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: 增加路径安全检查，防止 AI 修改框架核心代码。

import os
import re
import subprocess
from datetime import datetime

def is_safe_path(base_dir, target_path):
    """
    检查目标路径是否在基础目录内 (防止路径遍历攻击)
    """
    abs_base = os.path.abspath(base_dir)
    abs_target = os.path.abspath(os.path.join(base_dir, target_path))
    return abs_target.startswith(abs_base)

def init_workspace(work_dir):
    """
    初始化工作区：创建目录，初始化Git
    """
    os.makedirs(os.path.join(work_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(work_dir, "src"), exist_ok=True)
    
    git_dir = os.path.join(work_dir, ".git")
    if not os.path.exists(git_dir):
        try:
            subprocess.run(["git", "init"], cwd=work_dir, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "AI-Collab"], cwd=work_dir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "ai@example.com"], cwd=work_dir, capture_output=True)
        except Exception as e:
            print(f"Warning: Git init failed: {e}")

def save_log(work_dir, agent_name, content):
    """保存对话日志"""
    log_dir = os.path.join(work_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    version = len([f for f in os.listdir(log_dir) if agent_name.lower() in f.lower()]) + 1
    path = os.path.join(log_dir, f"{agent_name}_v{version}.md")
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {agent_name} - Version {version}\n\n")
            f.write(f"**Time**: {datetime.now().isoformat()}\n\n")
            f.write(content)
        print(f"📝 Log saved: {path}")
    except Exception as e:
        print(f"❌ Failed to save log: {e}")

def save_code_to_file(work_dir, rel_path, content):
    """
    将内容保存到指定文件 (安全模式)
    """
    if not is_safe_path(work_dir, rel_path):
        return False, f"⛔ Security Violation: Cannot write to '{rel_path}' (Outside workspace)"

    full_path = os.path.join(work_dir, rel_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Saved: {rel_path}")
        
        # Git commit
        subprocess.run(["git", "add", "."], cwd=work_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Auto-save: {rel_path}"], cwd=work_dir, capture_output=True)
        
        return True, f"Successfully saved to {rel_path}"
    except Exception as e:
        return False, str(e)

def read_workspace_file(work_dir, filepath):
    """安全读取工作区文件"""
    if not is_safe_path(work_dir, filepath):
        return "❌ Error: Access denied (Outside workspace)"
        
    safe_path = os.path.abspath(os.path.join(work_dir, filepath))
    if os.path.exists(safe_path):
        try:
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"❌ Error reading file: {e}"
    return "❌ Error: File not found"

def extract_and_save_code(work_dir, content):
    """
    从对话内容中提取代码块并保存
    支持格式: #### path/to/file \n ```python ... ```
    """
    lines = content.split('\n')
    saved_files = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        path_match = re.match(r'^#{1,4}\s+`?(.+?)`?\s*$', line)
        if path_match:
            path = path_match.group(1).strip()
            # 过滤掉普通标题，只处理看起来像文件路径的
            # 简单的启发式：包含 '.' 或者 '/'
            if not ('.' in path or '/' in path or '\\' in path):
                i += 1
                continue
                
            j = i + 1
            code_lines = []
            found_block = False
            
            while j < len(lines):
                if lines[j].strip().startswith("```"):
                    if not found_block: found_block = True
                    else: break
                elif found_block:
                    code_lines.append(lines[j])
                j += 1
            
            if found_block and code_lines:
                clean_path = path.replace('workspace/', '').replace('workspace\\', '')
                success, msg = save_code_to_file(work_dir, clean_path, "\n".join(code_lines))
                if success:
                    saved_files.append(clean_path)
                else:
                    print(f"   (Skipped invalid path: {clean_path})")
            i = j
        else:
            i += 1
    return saved_files
