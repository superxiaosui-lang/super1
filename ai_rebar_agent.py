import os
import openai
from github import Github

# 1. 解析 OpenSees/Tcl 脚本，提取钢筋参数
def parse_tcl_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    params = []
    for line in lines:
        if 'uniaxialMaterial' in line or 'section' in line:
            params.append(line.strip())
    return '\n'.join(params)

# 2. 调用大模型生成结构安全性分析报告
def generate_report(tcl_params, model="gpt-4"):
    prompt = f"""你是一名结构工程专家，请根据以下钢筋仿真参数，分析其屈曲安全性，并生成一份详细的结构安全性分析报告（含建议与结论，要求中英文双语）：\n{tcl_params}\n"""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024
    )
    return response['choices'][0]['message']['content']

# 3. 自动推送分析报告到 GitHub 仓库（新建 PR）
def push_report_to_github(report, repo_name, branch="auto-report", token=None):
    g = Github(token or os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    base = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base.commit.sha)
    file_path = "reports/auto_report.md"
    repo.create_file(file_path, "Add auto-generated report", report, branch=branch)
    pr = repo.create_pull(
        title="自动生成结构安全性分析报告",
        body="本 PR 由 AI Agent 自动生成，包含最新仿真分析结果。",
        head=branch,
        base="main"
    )
    return pr.html_url

if __name__ == "__main__":
    # 示例流程
    tcl_file = "16@100unequal tension and compression_final.tcl"
    tcl_params = parse_tcl_file(tcl_file)
    report = generate_report(tcl_params)
    pr_url = push_report_to_github(
        report,
        repo_name="your_github_username/your_repo",
        token="your_github_token"
    )
    print("自动分析报告 PR 已创建，访问链接：", pr_url)
