# 版本: v1.1
# 总结: Web 搜索技能逻辑 - 集成 DuckDuckGo 开源库。

def search(query):
    """
    执行网页搜索
    优先尝试使用 duckduckgo-search (开源无需Key)，如果未安装则降级为 Mock。
    """
    try:
        # 尝试引入开源搜索库
        from duckduckgo_search import DDGS
        print(f"🔍 [Skill] WebSearch: Using DuckDuckGo (Open Source) for '{query}'...")
        
        results = []
        with DDGS() as ddgs:
            # 获取前3条结果
            gen = ddgs.text(query, max_results=3)
            if gen:
                for r in gen:
                    results.append(f"- [{r.get('title')}]({r.get('href')}): {r.get('body')}")
        
        if not results:
            return "No results found."
        return "\n".join(results)
        
    except ImportError:
        print(f"⚠️ [Skill] WebSearch: 'duckduckgo-search' package not installed. Using Mock Mode.")
        print("   (Tip: pip install duckduckgo-search)")
        # Mock 逻辑
        return f"Mock Result for '{query}': Found relevant documentation on python.org and github.com."
    except Exception as e:
        print(f"❌ [Skill] Search Error: {e}")
        return f"Search failed: {e}"

def run_research_task(goal):
    """
    执行一个完整的研究任务
    """
    print(f"🕵️ [Skill] WebSearch: Researching '{goal}'...")
    results = search(goal)
    return results
