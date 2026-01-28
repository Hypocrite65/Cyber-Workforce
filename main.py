# 版本: v1.4
# 作者: wei-Aug2024
# 邮箱: wei_qiao@tigerte.com
# 日期: 2026-01-28
# 总结: 增加 Windows 路径自动兼容处理，确保在 Docker (Linux) 中能正确读取文件。

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core.runner import run_project, run_company
from ai_core.skills.team_builder import assess_and_build_team
from ai_core.skills.ui_designer import generate_design_system

def main():
    parser = argparse.ArgumentParser(description="Multi-AI Collaboration Runner")
    
    # 模式选择
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--type", choices=["web", "embedded"], help="Legacy: Quick project type")
    group.add_argument("--company", help="Path to company config JSON")
    group.add_argument("--auto-team", action="store_true", help="Skill: Analyze task and build custom team automatically")
    group.add_argument("--design", action="store_true", help="Skill: Generate UI design system")
    
    # 任务参数
    parser.add_argument("--task", required=True, help="Path to task description file (.md)")
    parser.add_argument("--name", help="Project name (subfolder in output/), default is task filename")
    
    args = parser.parse_args()
    
    # 【Fix】路径兼容性处理：将 Windows 的 \ 转换为 Linux 的 /
    # 因为 Docker 容器是 Linux 环境
    task_path = args.task.replace("\\", "/")
    
    # 确定项目名称
    project_name = args.name
    if not project_name:
        base_name = os.path.basename(task_path)
        project_name = os.path.splitext(base_name)[0]
    
    # 关键路径定义
    # ROOT/output/project_name/workspace
    root_dir = os.getcwd()
    output_base = os.path.join(root_dir, "output")
    project_dir = os.path.join(output_base, project_name)
    workspace_dir = os.path.join(project_dir, "workspace")
    
    if not os.path.exists(task_path):
        print(f"❌ Task file not found: {task_path}")
        # 调试信息：列出当前文件，帮助用户排查挂载问题
        print(f"   (Current Dir: {os.getcwd()})")
        print(f"   (Available: {os.listdir(os.getcwd())})")
        return
        
    with open(task_path, 'r', encoding='utf-8') as f:
        task_content = f.read()

    print(f"📋 Project: {project_name}")
    print(f"💾 Output:  {workspace_dir}")
    print("--------------------------------------------------")
    
    # 执行逻辑
    if args.design:
        print("🎨 Mode:    UI Design System Generation")
        design_output = os.path.join(project_dir, "design_system.md")
        success = generate_design_system(task_content, design_output)
        if success:
            print(f"✅ Design system generated: {design_output}")
        else:
            print("❌ Design generation failed.")
            
    elif args.auto_team:
        print("🧠 Mode:    Auto-Team Building (AI Skill)")
        # 自动生成的配置也保存在 output 目录下，保持 source 干净
        config_path = os.path.join(project_dir, "company_config.json")
        
        success = assess_and_build_team(task_content, config_path)
        if success:
            print(f"🏢 Team Assembled! Config saved to: {config_path}")
            run_company(config_path, task_content, workspace_dir)
        else:
            print("❌ Team building failed.")
            
    elif args.company:
        print(f"🏢 Mode:    Manual Company Config ({args.company})")
        # 同样处理 company config 路径
        company_path = args.company.replace("\\", "/")
        if not os.path.exists(company_path):
             print(f"❌ Company config not found: {company_path}")
             return
        run_company(company_path, task_content, workspace_dir)
        
    else:
        print(f"📂 Mode:    Legacy Type ({args.type})")
        run_project(args.type, task_content, workspace_dir)

if __name__ == "__main__":
    main()
