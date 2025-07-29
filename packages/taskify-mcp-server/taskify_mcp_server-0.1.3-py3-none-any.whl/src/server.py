"""Taskify MCP Server - 智能化编程思维导师"""

import re
import json
from typing import Dict, List
from enum import Enum
from dataclasses import dataclass, asdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("taskify")


class TaskType(Enum):
    """任务类型枚举"""
    NEW_FEATURE = "new_feature"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """复杂度级别枚举"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class TaskAnalysis:
    """任务分析结果"""
    task_type: TaskType
    complexity_level: ComplexityLevel
    core_objective: str
    key_requirements: List[str]
    constraints: List[str]
    risk_factors: List[str]
    success_criteria: List[str]
    context_needs: List[str]


@dataclass
class ThinkingFramework:
    """思考框架"""
    phase: str
    guiding_questions: List[str]
    key_considerations: List[str]
    output_format: str
    examples: List[str]


def analyze_task_type(user_request: str) -> TaskType:
    """基于用户请求分析任务类型"""
    request_lower = user_request.lower()
    
    # 关键词匹配规则
    type_keywords = {
        TaskType.NEW_FEATURE: ["add", "implement", "create", "build", "develop", "新增", "添加", "实现", "构建"],
        TaskType.BUG_FIX: ["fix", "bug", "error", "issue", "problem", "修复", "错误", "问题", "故障"],
        TaskType.REFACTOR: ["refactor", "restructure", "reorganize", "clean", "重构", "重组", "清理"],
        TaskType.PERFORMANCE: ["optimize", "performance", "speed", "memory", "efficient", "优化", "性能", "效率"],
        TaskType.TESTING: ["test", "testing", "unit test", "coverage", "测试", "单元测试"],
        TaskType.DOCUMENTATION: ["document", "doc", "readme", "comment", "文档", "注释"],
        TaskType.MAINTENANCE: ["update", "upgrade", "maintain", "dependency", "更新", "升级", "维护"]
    }
    
    for task_type, keywords in type_keywords.items():
        if any(keyword in request_lower for keyword in keywords):
            return task_type
    
    return TaskType.UNKNOWN


def estimate_complexity(user_request: str, task_type: TaskType) -> ComplexityLevel:
    """评估任务复杂度"""
    request_lower = user_request.lower()
    
    # 复杂度指标
    complexity_indicators = {
        "high": ["architecture", "system", "multiple", "integrate", "database", "api", "架构", "系统", "多个", "集成"],
        "medium": ["module", "class", "function", "component", "模块", "组件", "类", "函数"],
        "low": ["variable", "config", "simple", "single", "变量", "配置", "简单", "单个"]
    }
    
    # 计算复杂度分数
    high_score = sum(1 for keyword in complexity_indicators["high"] if keyword in request_lower)
    medium_score = sum(1 for keyword in complexity_indicators["medium"] if keyword in request_lower)
    low_score = sum(1 for keyword in complexity_indicators["low"] if keyword in request_lower)
    
    # 考虑任务类型的基础复杂度
    base_complexity = {
        TaskType.NEW_FEATURE: 2,
        TaskType.REFACTOR: 2,
        TaskType.PERFORMANCE: 2,
        TaskType.BUG_FIX: 1,
        TaskType.TESTING: 1,
        TaskType.DOCUMENTATION: 1,
        TaskType.MAINTENANCE: 1,
        TaskType.UNKNOWN: 1
    }
    
    total_score = high_score * 3 + medium_score * 2 + low_score * 1 + base_complexity[task_type]
    
    if total_score >= 5:
        return ComplexityLevel.COMPLEX
    elif total_score >= 3:
        return ComplexityLevel.MEDIUM
    else:
        return ComplexityLevel.SIMPLE


def generate_thinking_framework(task_analysis: TaskAnalysis) -> Dict[str, ThinkingFramework]:
    """根据任务分析生成定制化思考框架"""
    
    frameworks = {}
    
    # 第一阶段：理解阶段
    frameworks["understanding"] = ThinkingFramework(
        phase="深度理解",
        guiding_questions=generate_understanding_questions(task_analysis),
        key_considerations=generate_understanding_considerations(task_analysis),
        output_format="问题本质、用户意图、隐含需求",
        examples=generate_understanding_examples(task_analysis)
    )
    
    # 第二阶段：规划阶段
    frameworks["planning"] = ThinkingFramework(
        phase="策略规划",
        guiding_questions=generate_planning_questions(task_analysis),
        key_considerations=generate_planning_considerations(task_analysis),
        output_format="实现路径、技术选型、风险评估",
        examples=generate_planning_examples(task_analysis)
    )
    
    # 第三阶段：实现阶段
    frameworks["implementation"] = ThinkingFramework(
        phase="精准实现",
        guiding_questions=generate_implementation_questions(task_analysis),
        key_considerations=generate_implementation_considerations(task_analysis),
        output_format="具体步骤、代码结构、接口设计",
        examples=generate_implementation_examples(task_analysis)
    )
    
    # 第四阶段：验证阶段
    frameworks["validation"] = ThinkingFramework(
        phase="质量验证",
        guiding_questions=generate_validation_questions(task_analysis),
        key_considerations=generate_validation_considerations(task_analysis),
        output_format="测试策略、验收标准、性能指标",
        examples=generate_validation_examples(task_analysis)
    )
    
    return frameworks


def generate_understanding_questions(task_analysis: TaskAnalysis) -> List[str]:
    """生成理解阶段的指导问题"""
    base_questions = [
        "用户真正想要解决什么核心问题？",
        "这个需求背后的业务价值是什么？",
        "有哪些隐含的约束和期望？"
    ]
    
    type_specific_questions = {
        TaskType.NEW_FEATURE: [
            "这个功能如何融入现有系统？",
            "预期的用户使用场景是什么？",
            "功能边界在哪里？"
        ],
        TaskType.BUG_FIX: [
            "问题的根本原因是什么？",
            "影响范围有多大？",
            "如何避免类似问题再次出现？"
        ],
        TaskType.REFACTOR: [
            "当前设计的痛点是什么？",
            "重构的最终目标是什么？",
            "如何确保重构后的向后兼容性？"
        ],
        TaskType.PERFORMANCE: [
            "性能瓶颈在哪里？",
            "目标性能指标是什么？",
            "优化的权衡取舍是什么？"
        ]
    }
    
    return base_questions + type_specific_questions.get(task_analysis.task_type, [])


def generate_understanding_considerations(task_analysis: TaskAnalysis) -> List[str]:
    """生成理解阶段的关键考虑点"""
    base_considerations = [
        "区分显性需求和隐性需求",
        "识别技术约束和业务约束",
        "评估变更的影响范围"
    ]
    
    complexity_considerations = {
        ComplexityLevel.SIMPLE: ["确保理解准确，避免过度设计"],
        ComplexityLevel.MEDIUM: ["平衡功能完整性和实现复杂度"],
        ComplexityLevel.COMPLEX: ["系统性思考，考虑架构影响", "分阶段实现策略"]
    }
    
    return base_considerations + complexity_considerations[task_analysis.complexity_level]


def generate_understanding_examples(task_analysis: TaskAnalysis) -> List[str]:
    """生成理解阶段的示例"""
    examples = {
        TaskType.NEW_FEATURE: ["用户说'添加搜索功能' → 理解为：需要什么类型的搜索？实时搜索还是批量搜索？搜索范围是什么？"],
        TaskType.BUG_FIX: ["用户说'登录有问题' → 理解为：什么情况下出错？错误现象是什么？影响所有用户还是特定用户？"],
        TaskType.REFACTOR: ["用户说'代码太乱了' → 理解为：具体哪些部分需要重构？重构的优先级是什么？"],
        TaskType.PERFORMANCE: ["用户说'太慢了' → 理解为：哪个环节慢？可接受的响应时间是多少？"]
    }
    
    return examples.get(task_analysis.task_type, ["深入理解用户真实需求，而非表面描述"])


def generate_planning_questions(task_analysis: TaskAnalysis) -> List[str]:
    """生成规划阶段的指导问题"""
    return [
        "最佳的实现路径是什么？",
        "需要哪些技术栈和工具？",
        "如何分解任务以降低风险？",
        "有哪些可能的技术陷阱？",
        "如何确保代码质量和可维护性？"
    ]


def generate_planning_considerations(task_analysis: TaskAnalysis) -> List[str]:
    """生成规划阶段的关键考虑点"""
    base_considerations = [
        "选择合适的技术方案",
        "评估开发成本和时间",
        "考虑未来扩展性"
    ]
    
    if task_analysis.complexity_level == ComplexityLevel.COMPLEX:
        base_considerations.extend([
            "设计系统架构",
            "定义模块接口",
            "制定迭代计划"
        ])
    
    return base_considerations


def generate_planning_examples(task_analysis: TaskAnalysis) -> List[str]:
    """生成规划阶段的示例"""
    return [
        "技术选型：React vs Vue → 考虑团队技能、项目需求、生态系统",
        "架构设计：单体 vs 微服务 → 考虑项目规模、团队能力、维护成本"
    ]


def generate_implementation_questions(task_analysis: TaskAnalysis) -> List[str]:
    """生成实现阶段的指导问题"""
    return [
        "如何组织代码结构？",
        "接口设计是否清晰合理？",
        "错误处理策略是什么？",
        "如何确保代码的可测试性？",
        "是否遵循了项目的编码规范？"
    ]


def generate_implementation_considerations(task_analysis: TaskAnalysis) -> List[str]:
    """生成实现阶段的关键考虑点"""
    return [
        "保持代码简洁和可读性",
        "遵循设计模式和最佳实践",
        "考虑异常情况的处理",
        "确保接口的向后兼容性",
        "添加必要的日志和监控"
    ]


def generate_implementation_examples(task_analysis: TaskAnalysis) -> List[str]:
    """生成实现阶段的示例"""
    return [
        "函数设计：单一职责、清晰命名、适当抽象",
        "错误处理：预期异常 vs 意外异常的不同处理策略"
    ]


def generate_validation_questions(task_analysis: TaskAnalysis) -> List[str]:
    """生成验证阶段的指导问题"""
    return [
        "如何验证功能的正确性？",
        "性能是否满足要求？",
        "是否考虑了边界情况？",
        "用户体验是否良好？",
        "是否有充分的测试覆盖？"
    ]


def generate_validation_considerations(task_analysis: TaskAnalysis) -> List[str]:
    """生成验证阶段的关键考虑点"""
    return [
        "功能测试和集成测试",
        "性能基准测试",
        "用户体验验证",
        "代码质量检查",
        "文档完整性确认"
    ]


def generate_validation_examples(task_analysis: TaskAnalysis) -> List[str]:
    """生成验证阶段的示例"""
    return [
        "API测试：正常情况、异常情况、边界情况",
        "性能测试：响应时间、并发处理、内存使用"
    ]


@mcp.tool()
def analyze_programming_context(
    user_request: str,
    project_context: str = "",
    complexity_hint: str = "auto"
) -> str:
    """
    🧠 智能编程任务分析器 - 启发式思维的起点
    
    这个工具是编程思维导师系统的核心，它能够：
    • 自动识别任务类型（新功能、Bug修复、性能优化、重构等）
    • 智能评估复杂度级别（简单/中等/复杂）
    • 提供场景化的4阶段思考框架（理解→规划→实现→验证）
    • 生成定制化的指导问题和关键考虑点
    
    使用场景：
    - 面对新的编程任务时，不确定从何思考
    - 需要系统化的思考框架来指导任务分析
    - 希望根据任务特点获得针对性的思考指导
    - 想要确保考虑到所有重要的技术和业务因素
    
    Args:
        user_request: 用户的编程请求描述
        project_context: 项目背景信息（技术栈、架构约束等）
        complexity_hint: 复杂度提示 ("simple"/"medium"/"complex"/"auto")
    
    Returns:
        JSON格式的完整分析结果，包含：
        {
            "task_analysis": {
                "task_type": "任务类型",
                "complexity_level": "复杂度级别", 
                "core_objective": "核心目标",
                "key_requirements": ["关键需求"],
                "constraints": ["约束条件"],
                "risk_factors": ["风险因素"],
                "success_criteria": ["成功标准"],
                "context_needs": ["上下文需求"]
            },
            "thinking_frameworks": {
                "understanding": "理解阶段框架",
                "planning": "规划阶段框架",
                "implementation": "实现阶段框架", 
                "validation": "验证阶段框架"
            },
            "recommended_approach": "推荐的实现方法",
            "quality_checklist": ["质量检查清单"]
        }
    """
    
    # 分析任务类型
    task_type = analyze_task_type(user_request)
    
    # 估算复杂度
    if complexity_hint == "auto":
        complexity_level = estimate_complexity(user_request, task_type)
    else:
        complexity_level = ComplexityLevel(complexity_hint)
    
    # 生成任务分析
    task_analysis = TaskAnalysis(
        task_type=task_type,
        complexity_level=complexity_level,
        core_objective=extract_core_objective(user_request),
        key_requirements=extract_requirements(user_request),
        constraints=extract_constraints(user_request, project_context),
        risk_factors=identify_risk_factors(user_request, task_type),
        success_criteria=define_success_criteria(user_request, task_type),
        context_needs=identify_context_needs(user_request, project_context)
    )
    
    # 生成思考框架
    frameworks = generate_thinking_framework(task_analysis)
    
    # 构建结果
    result = {
        "task_analysis": {
            "task_type": task_analysis.task_type.value,
            "complexity_level": task_analysis.complexity_level.value,
            "core_objective": task_analysis.core_objective,
            "key_requirements": task_analysis.key_requirements,
            "constraints": task_analysis.constraints,
            "risk_factors": task_analysis.risk_factors,
            "success_criteria": task_analysis.success_criteria,
            "context_needs": task_analysis.context_needs
        },
        "thinking_frameworks": {k: asdict(v) for k, v in frameworks.items()},
        "recommended_approach": generate_approach_recommendation(task_analysis),
        "quality_checklist": generate_quality_checklist(task_analysis)
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def extract_core_objective(user_request: str) -> str:
    """提取核心目标"""
    # 简单的目标提取逻辑
    if "implement" in user_request.lower() or "实现" in user_request:
        return "实现新功能"
    elif "fix" in user_request.lower() or "修复" in user_request:
        return "修复问题"
    elif "optimize" in user_request.lower() or "优化" in user_request:
        return "优化性能"
    elif "refactor" in user_request.lower() or "重构" in user_request:
        return "重构代码"
    else:
        return "完成编程任务"


def extract_requirements(user_request: str) -> List[str]:
    """提取关键需求"""
    # 简化的需求提取
    requirements = []
    if "test" in user_request.lower() or "测试" in user_request:
        requirements.append("包含测试用例")
    if "document" in user_request.lower() or "文档" in user_request:
        requirements.append("提供文档说明")
    if "performance" in user_request.lower() or "性能" in user_request:
        requirements.append("考虑性能优化")
    
    return requirements if requirements else ["满足基本功能需求"]


def extract_constraints(user_request: str, project_context: str) -> List[str]:
    """提取约束条件"""
    constraints = []
    if "backward compatible" in user_request.lower() or "向后兼容" in user_request:
        constraints.append("保持向后兼容性")
    if project_context:
        constraints.append("遵循项目现有架构")
    
    return constraints if constraints else ["遵循编程最佳实践"]


def identify_risk_factors(user_request: str, task_type: TaskType) -> List[str]:
    """识别风险因素"""
    risk_factors = []
    
    if task_type == TaskType.NEW_FEATURE:
        risk_factors.extend(["功能范围蔓延", "与现有功能冲突"])
    elif task_type == TaskType.BUG_FIX:
        risk_factors.extend(["修复引入新问题", "影响其他功能"])
    elif task_type == TaskType.REFACTOR:
        risk_factors.extend(["破坏现有功能", "重构范围过大"])
    elif task_type == TaskType.PERFORMANCE:
        risk_factors.extend(["过度优化", "可读性下降"])
    
    return risk_factors


def define_success_criteria(user_request: str, task_type: TaskType) -> List[str]:
    """定义成功标准"""
    base_criteria = ["功能正确实现", "代码质量良好", "通过测试验证"]
    
    type_specific_criteria = {
        TaskType.NEW_FEATURE: ["满足用户需求", "性能表现良好"],
        TaskType.BUG_FIX: ["问题完全解决", "无副作用"],
        TaskType.REFACTOR: ["代码更清晰", "性能不降低"],
        TaskType.PERFORMANCE: ["达到性能目标", "保持功能完整"]
    }
    
    return base_criteria + type_specific_criteria.get(task_type, [])


def identify_context_needs(user_request: str, project_context: str) -> List[str]:
    """识别上下文需求"""
    needs = ["了解现有代码结构", "理解业务逻辑"]
    
    if not project_context:
        needs.append("获取项目架构信息")
    
    return needs


def generate_approach_recommendation(task_analysis: TaskAnalysis) -> str:
    """生成实现方法建议"""
    if task_analysis.complexity_level == ComplexityLevel.SIMPLE:
        return "直接实现，注重代码质量"
    elif task_analysis.complexity_level == ComplexityLevel.MEDIUM:
        return "分步实现，先设计后编码"
    else:
        return "分阶段实现，先制定详细计划"


def generate_quality_checklist(task_analysis: TaskAnalysis) -> List[str]:
    """生成质量检查清单"""
    return [
        "代码是否清晰易读？",
        "是否遵循项目规范？",
        "错误处理是否完善？",
        "是否有充分的测试？",
        "性能是否可接受？",
        "是否考虑了边界情况？"
    ]


@mcp.tool()
def guided_thinking_process(
    task_analysis_json: str,
    current_step: str = "understanding"
) -> str:
    """
    🎯 渐进式思考引导器 - 步步为营的智慧路径
    
    基于任务分析结果，提供分阶段的深度思考指导，确保每个环节都经过充分思考：
    
    • **理解阶段 (understanding)**: 深入洞察问题本质，理解真实需求
    • **规划阶段 (planning)**: 制定实现策略，评估技术选型和风险
    • **实现阶段 (implementation)**: 指导具体编码实现，确保质量
    • **验证阶段 (validation)**: 质量验证和测试策略制定
    
    使用场景：
    - 已完成任务分析，需要逐步深入思考
    - 希望在每个阶段都获得专业指导
    - 确保思考过程的完整性和系统性
    - 避免遗漏关键的考虑因素
    
    工作流程：
    1. 先调用 analyze_programming_context 获取任务分析
    2. 使用返回的JSON作为此工具的输入
    3. 从 understanding 开始，逐步推进到 validation
    4. 每完成一个阶段，进入下一个阶段继续思考
    
    Args:
        task_analysis_json: analyze_programming_context工具返回的JSON结果
        current_step: 当前思考阶段 ("understanding"/"planning"/"implementation"/"validation")
    
    Returns:
        当前阶段的详细指导信息：
        {
            "phase": "当前阶段名称",
            "focus": "阶段重点描述",
            "questions": ["引导性问题列表"],
            "considerations": ["关键考虑点"],
            "output_format": "预期输出格式",
            "examples": ["具体示例"],
            "next_step": "下一个阶段"
        }
    """
    
    try:
        task_data = json.loads(task_analysis_json)
        frameworks = task_data.get("thinking_frameworks", {})
        
        if current_step not in frameworks:
            return f"无效的步骤: {current_step}. 可用步骤: {list(frameworks.keys())}"
        
        current_framework = frameworks[current_step]
        
        guidance = {
            "phase": current_framework["phase"],
            "focus": f"专注于{current_framework['phase']}阶段",
            "questions": current_framework["guiding_questions"],
            "considerations": current_framework["key_considerations"],
            "output_format": current_framework["output_format"],
            "examples": current_framework["examples"],
            "next_step": get_next_step(current_step)
        }
        
        return json.dumps(guidance, ensure_ascii=False, indent=2)
        
    except json.JSONDecodeError:
        return "错误：无法解析任务分析JSON"
    except Exception as e:
        return f"错误：{str(e)}"


def get_next_step(current_step: str) -> str:
    """获取下一步骤"""
    step_order = ["understanding", "planning", "implementation", "validation"]
    try:
        current_index = step_order.index(current_step)
        if current_index < len(step_order) - 1:
            return step_order[current_index + 1]
        else:
            return "完成"
    except ValueError:
        return "未知"


@mcp.tool()
def validate_instruction_quality(
    instruction: str,
    task_context: str = ""
) -> str:
    """
    ✅ 编程指令质量评估器 - 确保指令的专业水准
    
    这个工具采用多维度评估体系，对编程指令进行全面的质量分析：
    
    **评估维度：**
    • **清晰度 (Clarity)**: 指令是否明确易懂，目标清晰
    • **完整性 (Completeness)**: 是否包含必要的输入输出、约束条件
    • **具体性 (Specificity)**: 是否有具体的技术细节和文件名
    • **可执行性 (Actionability)**: 是否提供明确步骤，避免模糊语言
    • **风险意识 (Risk Awareness)**: 是否考虑测试、错误处理、兼容性
    
    **评分标准：**
    - 0.9-1.0: 优秀 - 指令质量非常高
    - 0.8-0.9: 良好 - 指令质量较高  
    - 0.7-0.8: 一般 - 指令质量中等
    - 0.6-0.7: 需要改进 - 指令质量偏低
    - 0.0-0.6: 不合格 - 指令质量较差，需要重新设计
    
    使用场景：
    - 完成指令编写后，验证质量是否达标
    - 对已有指令进行优化改进
    - 学习如何编写高质量的编程指令
    - 确保指令能被编程代理准确理解和执行
    
    Args:
        instruction: 需要评估的编程指令文本
        task_context: 任务相关上下文信息（可选，用于更精确评估）
    
    Returns:
        详细的质量评估报告：
        {
            "overall_score": 0.85,
            "quality_metrics": {
                "clarity": 0.8,
                "completeness": 0.9,
                "specificity": 0.7,
                "actionability": 0.9,
                "risk_awareness": 0.8
            },
            "assessment": "良好 - 指令质量较高",
            "improvement_suggestions": ["具体改进建议"],
            "recommended_actions": ["推荐行动"]
        }
    """
    
    # 质量评估维度
    quality_metrics = {
        "clarity": assess_clarity(instruction),
        "completeness": assess_completeness(instruction),
        "specificity": assess_specificity(instruction),
        "actionability": assess_actionability(instruction),
        "risk_awareness": assess_risk_awareness(instruction)
    }
    
    # 计算总分
    total_score = sum(quality_metrics.values()) / len(quality_metrics)
    
    # 生成改进建议
    suggestions = generate_improvement_suggestions(quality_metrics, instruction)
    
    result = {
        "overall_score": round(total_score, 2),
        "quality_metrics": quality_metrics,
        "assessment": get_quality_assessment(total_score),
        "improvement_suggestions": suggestions,
        "recommended_actions": get_recommended_actions(quality_metrics)
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def assess_clarity(instruction: str) -> float:
    """评估指令清晰度"""
    score = 0.6  # 基础分
    
    # 检查是否有明确的动词
    action_verbs = ["implement", "create", "fix", "optimize", "refactor", "test", "实现", "创建", "修复", "优化", "重构", "测试"]
    if any(verb in instruction.lower() for verb in action_verbs):
        score += 0.2
    
    # 检查是否有具体的目标
    if any(word in instruction.lower() for word in ["function", "class", "method", "api", "函数", "类", "方法"]):
        score += 0.2
    
    return min(score, 1.0)


def assess_completeness(instruction: str) -> float:
    """评估指令完整性"""
    score = 0.5  # 基础分
    
    # 检查是否包含输入/输出描述
    if any(word in instruction.lower() for word in ["input", "output", "return", "parameter", "输入", "输出", "返回", "参数"]):
        score += 0.2
    
    # 检查是否包含约束条件
    if any(word in instruction.lower() for word in ["constraint", "requirement", "must", "should", "约束", "要求", "必须", "应该"]):
        score += 0.2
    
    # 检查是否包含成功标准
    if any(word in instruction.lower() for word in ["success", "criteria", "expect", "成功", "标准", "期望"]):
        score += 0.1
    
    return min(score, 1.0)


def assess_specificity(instruction: str) -> float:
    """评估指令具体性"""
    score = 0.4  # 基础分
    
    # 检查是否有具体的文件或函数名
    if re.search(r'\w+\.(py|js|ts|java|cpp|c)', instruction):
        score += 0.3
    
    # 检查是否有具体的技术栈
    tech_terms = ["react", "vue", "angular", "django", "flask", "express", "spring"]
    if any(term in instruction.lower() for term in tech_terms):
        score += 0.2
    
    # 检查是否有数值或量化指标
    if re.search(r'\d+', instruction):
        score += 0.1
    
    return min(score, 1.0)


def assess_actionability(instruction: str) -> float:
    """评估指令可执行性"""
    score = 0.6  # 基础分
    
    # 检查是否有明确的步骤
    if any(word in instruction.lower() for word in ["step", "first", "then", "步骤", "首先", "然后"]):
        score += 0.2
    
    # 检查是否避免了模糊语言
    vague_terms = ["somehow", "maybe", "possibly", "大概", "可能", "或许"]
    if not any(term in instruction.lower() for term in vague_terms):
        score += 0.2
    
    return min(score, 1.0)


def assess_risk_awareness(instruction: str) -> float:
    """评估风险意识"""
    score = 0.3  # 基础分
    
    # 检查是否提到了测试
    if any(word in instruction.lower() for word in ["test", "testing", "测试"]):
        score += 0.3
    
    # 检查是否提到了错误处理
    if any(word in instruction.lower() for word in ["error", "exception", "handle", "错误", "异常", "处理"]):
        score += 0.2
    
    # 检查是否提到了兼容性
    if any(word in instruction.lower() for word in ["compatible", "backward", "兼容"]):
        score += 0.2
    
    return min(score, 1.0)


def generate_improvement_suggestions(quality_metrics: Dict[str, float], instruction: str) -> List[str]:
    """生成改进建议"""
    suggestions = []
    
    if quality_metrics["clarity"] < 0.8:
        suggestions.append("增加指令的清晰度：使用更明确的动词和具体的目标描述")
    
    if quality_metrics["completeness"] < 0.8:
        suggestions.append("补充完整性：添加输入输出描述、约束条件和成功标准")
    
    if quality_metrics["specificity"] < 0.8:
        suggestions.append("提高具体性：指定具体的文件名、函数名或技术栈")
    
    if quality_metrics["actionability"] < 0.8:
        suggestions.append("增强可执行性：提供明确的步骤，避免模糊语言")
    
    if quality_metrics["risk_awareness"] < 0.8:
        suggestions.append("加强风险意识：考虑测试、错误处理和兼容性问题")
    
    return suggestions if suggestions else ["指令质量良好，建议保持当前水平"]


def get_quality_assessment(score: float) -> str:
    """获取质量评估结果"""
    if score >= 0.9:
        return "优秀 - 指令质量非常高"
    elif score >= 0.8:
        return "良好 - 指令质量较高"
    elif score >= 0.7:
        return "一般 - 指令质量中等"
    elif score >= 0.6:
        return "需要改进 - 指令质量偏低"
    else:
        return "不合格 - 指令质量较差，需要重新设计"


def get_recommended_actions(quality_metrics: Dict[str, float]) -> List[str]:
    """获取推荐行动"""
    actions = []
    
    lowest_metric = min(quality_metrics.items(), key=lambda x: x[1])
    
    if lowest_metric[1] < 0.7:
        metric_actions = {
            "clarity": "重新组织语言，使用更清晰的表达",
            "completeness": "补充缺失的关键信息",
            "specificity": "添加具体的技术细节",
            "actionability": "分解为可执行的步骤",
            "risk_awareness": "考虑潜在的风险和问题"
        }
        actions.append(metric_actions[lowest_metric[0]])
    
    return actions if actions else ["继续保持当前的指令质量"]



@mcp.tool()
def smart_programming_coach(
    user_request: str,
    project_context: str = "",
    mode: str = "full_guidance"
) -> str:
    """
    🎓 智能编程教练 - 大模型的思维导航仪
    
    这是一个元工具，专门指导大模型如何智能地运用其他3个工具来完成完整的编程思维过程。
    它会根据用户请求的特点，自动推荐最佳的工具使用策略和顺序。
    
    **核心价值：**
    • 自动分析任务特点，推荐最优的工具使用流程
    • 提供具体的工具调用示例和参数建议
    • 确保大模型能够系统性地完成编程思维过程
    • 避免工具使用的混乱和遗漏
    
    **使用模式：**
    • **full_guidance**: 完整指导模式，提供详细的步骤和工具调用示例
    • **quick_start**: 快速入门模式，提供简化的使用流程
    • **expert_mode**: 专家模式，仅提供关键提示和最佳实践
    
    **智能推荐策略：**
    1. 简单任务 → 直接使用 analyze_programming_context + validate_instruction_quality
    2. 中等任务 → 完整3工具流程，重点在 guided_thinking_process
    3. 复杂任务 → 迭代式使用，多轮 guided_thinking_process 深度思考
    4. 学习场景 → 完整流程 + 详细的思考过程展示
    
    Args:
        user_request: 用户的编程请求
        project_context: 项目上下文信息
        mode: 指导模式 ("full_guidance"/"quick_start"/"expert_mode")
    
    Returns:
        智能化的工具使用指导方案，包含：
        {
            "analysis": "任务分析和复杂度评估",
            "recommended_workflow": "推荐的工具使用流程",
            "tool_sequence": ["工具调用顺序"],
            "sample_calls": {
                "step1": "具体的工具调用示例",
                "step2": "下一步的调用示例"
            },
            "expected_outcomes": ["每个步骤的预期结果"],
            "tips": ["使用技巧和注意事项"],
            "next_actions": "建议的下一步行动"
        }
    """
    
    # 分析任务特征
    task_complexity = estimate_request_complexity(user_request)
    task_nature = analyze_request_nature(user_request)
    
    # 根据复杂度和性质推荐流程
    workflow = generate_workflow_recommendation(task_complexity, task_nature, mode)
    
    # 生成具体的工具调用示例
    sample_calls = generate_sample_tool_calls(user_request, project_context, workflow)
    
    # 构建指导方案
    guidance = {
        "analysis": f"任务类型: {task_nature}, 复杂度: {task_complexity}",
        "recommended_workflow": workflow["description"],
        "tool_sequence": workflow["sequence"],
        "sample_calls": sample_calls,
        "expected_outcomes": workflow["outcomes"],
        "tips": generate_usage_tips(task_complexity, mode),
        "next_actions": workflow["next_actions"]
    }
    
    return json.dumps(guidance, ensure_ascii=False, indent=2)


def estimate_request_complexity(user_request: str) -> str:
    """快速评估请求复杂度"""
    request_lower = user_request.lower()
    
    # 复杂度指标
    high_complexity_indicators = [
        "architecture", "system", "multiple", "integrate", "refactor", 
        "optimize", "架构", "系统", "多个", "集成", "重构", "优化"
    ]
    
    medium_complexity_indicators = [
        "feature", "function", "class", "module", "api",
        "功能", "函数", "类", "模块", "接口"
    ]
    
    high_score = sum(1 for indicator in high_complexity_indicators if indicator in request_lower)
    medium_score = sum(1 for indicator in medium_complexity_indicators if indicator in request_lower)
    
    if high_score >= 2:
        return "complex"
    elif high_score >= 1 or medium_score >= 2:
        return "medium"
    else:
        return "simple"


def analyze_request_nature(user_request: str) -> str:
    """分析请求性质"""
    request_lower = user_request.lower()
    
    if any(word in request_lower for word in ["learn", "understand", "explain", "学习", "理解", "解释"]):
        return "learning"
    elif any(word in request_lower for word in ["fix", "bug", "error", "修复", "错误", "问题"]):
        return "debugging"
    elif any(word in request_lower for word in ["optimize", "performance", "优化", "性能"]):
        return "optimization"
    elif any(word in request_lower for word in ["create", "implement", "build", "创建", "实现", "构建"]):
        return "development"
    else:
        return "general"


def generate_workflow_recommendation(complexity: str, nature: str, mode: str) -> dict:
    """生成工作流推荐"""
    
    workflows = {
        "simple": {
            "description": "轻量级流程：快速分析 + 质量验证",
            "sequence": ["analyze_programming_context", "validate_instruction_quality"],
            "outcomes": ["获得任务分析和思考框架", "验证最终指令质量"],
            "next_actions": "基于分析结果直接编写编程指令，然后验证质量"
        },
        "medium": {
            "description": "标准流程：完整的4阶段思考过程",
            "sequence": ["analyze_programming_context", "guided_thinking_process(understanding)", 
                        "guided_thinking_process(planning)", "guided_thinking_process(implementation)",
                        "validate_instruction_quality"],
            "outcomes": ["任务分析", "深度理解", "策略规划", "实现指导", "质量验证"],
            "next_actions": "按阶段逐步深入思考，每个阶段充分思考后再进入下一阶段"
        },
        "complex": {
            "description": "深度流程：迭代式思考 + 多轮优化",
            "sequence": ["analyze_programming_context", "guided_thinking_process(understanding)", 
                        "guided_thinking_process(planning)", "guided_thinking_process(implementation)",
                        "guided_thinking_process(validation)", "validate_instruction_quality",
                        "可能需要多轮迭代"],
            "outcomes": ["全面分析", "深度理解", "详细规划", "精准实现", "严格验证", "高质量指令"],
            "next_actions": "完成一轮思考后，根据需要进行第二轮优化思考"
        }
    }
    
    base_workflow = workflows.get(complexity, workflows["medium"])
    
    # 根据任务性质调整
    if nature == "learning":
        base_workflow["description"] += " (注重思考过程的展示和解释)"
    elif nature == "debugging":
        base_workflow["description"] += " (重点关注问题根因分析)"
    elif nature == "optimization":
        base_workflow["description"] += " (强调性能分析和权衡思考)"
    
    return base_workflow


def generate_sample_tool_calls(user_request: str, project_context: str, workflow: dict) -> dict:
    """生成具体的工具调用示例"""
    
    samples = {}
    
    # 第一步：任务分析
    samples["step1_analyze"] = {
        "tool": "analyze_programming_context",
        "call": f'analyze_programming_context("{user_request}", "{project_context}")',
        "purpose": "获取任务分析和思考框架"
    }
    
    # 如果包含guided_thinking_process
    if "guided_thinking_process" in str(workflow["sequence"]):
        samples["step2_understand"] = {
            "tool": "guided_thinking_process", 
            "call": 'guided_thinking_process(task_analysis_json, "understanding")',
            "purpose": "深入理解阶段的思考指导",
            "note": "task_analysis_json 是第一步返回的完整JSON结果"
        }
        
        samples["step3_plan"] = {
            "tool": "guided_thinking_process",
            "call": 'guided_thinking_process(task_analysis_json, "planning")', 
            "purpose": "规划阶段的思考指导"
        }
        
        samples["step4_implement"] = {
            "tool": "guided_thinking_process",
            "call": 'guided_thinking_process(task_analysis_json, "implementation")',
            "purpose": "实现阶段的思考指导"
        }
    
    # 最后：质量验证
    samples["final_validate"] = {
        "tool": "validate_instruction_quality",
        "call": 'validate_instruction_quality("your_final_instruction")',
        "purpose": "验证最终编程指令的质量"
    }
    
    return samples


def generate_usage_tips(complexity: str, mode: str) -> list:
    """生成使用技巧"""
    
    base_tips = [
        "每次工具调用后，仔细阅读返回结果再进行下一步",
        "思考过程要充分，不要急于得出结论",
        "将工具返回的JSON结果完整传递给下一个工具"
    ]
    
    complexity_tips = {
        "simple": ["保持简洁，避免过度分析"],
        "medium": ["平衡深度和效率，确保每个阶段都有收获"],
        "complex": ["允许多轮迭代，复杂问题需要时间来思考", "考虑分阶段实现策略"]
    }
    
    mode_tips = {
        "full_guidance": ["详细记录每步的思考过程"],
        "quick_start": ["重点关注核心问题，快速形成方案"],
        "expert_mode": ["信任自己的判断，灵活调整流程"]
    }
    
    return base_tips + complexity_tips.get(complexity, []) + mode_tips.get(mode, [])


def main():
    """Main entry point to run the MCP server."""
    mcp.run()
