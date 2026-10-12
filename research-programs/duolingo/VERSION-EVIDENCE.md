# 多邻国版本证据与观察边界

## 为什么需要版本证据

多邻国的功能会因为平台、地区、课程方向、账号类型、订阅状态、实验分组和时间而变化。官方文章能证明某项设计曾经存在或被团队解释过，但不能自动证明今天每个用户都能看到同样的入口。因此本页把产品陈述分成三种状态：**已由公开资料支持**、**需要当前版本实测**、**只能作为设计假说**。

## 已由官方公开资料支持的产品结构

| 陈述 | 公开依据 | 可以支持的范围 | 不能支持的范围 |
|---|---|---|---|
| Unit 围绕沟通目标组织词汇和语法 | Duolingo 101 | 课程内容的总体编排原则 | 每个语言方向都完全相同 |
| 练习包含听说读写并逐渐提高主动输入 | Duolingo 101 | 题型递进的公开说明 | 当前每道题的具体算法 |
| Hearts 会与错误和练习恢复关联 | Duolingo 101 | 资源机制的公开描述 | 所有平台的当前上限和恢复时间 |
| Gems 可用于商店和连胜保护 | Duolingo 101 | 经济系统的公开入口 | 当前全部商品和价格 |
| League 按周运行并按 XP 排序 | Leagues & Leaderboards | 周周期竞争模型 | 当前所有 League 层级和匹配算法 |
| Friends Quest 使用共同目标和共享进度 | Friends Quests | 轻协作机制 | 当前配对规则和所有地区可用性 |
| 成就集中在 Profile 并包含个人纪录 | Achievement Badges | 档案与奖励的关系 | 当前全部徽章及解锁阈值 |
| 核心标签经历过统一设计系统重构 | Core Tabs Redesign | 页面层级、标题、间距的设计意图 | 当前 App 的每个像素和所有实验分支 |
| Streak 是连续完成学习日的记录 | Improving the Streak | 连续机制的定义和增长实验 | 当前冻结、补救和通知的全部细节 |

## 需要当前版本实测的内容

以下问题不能只靠历史文章回答：

1. 当前底部导航具体有哪些标签，标签顺序是否因平台改变；
2. 用户的 Daily Quest、Monthly Quest 和 Friends Quest 是否共用一个 Quest 页面；
3. 当前课程是否显示 Section、Unit、Level、Legendary 和 Score；
4. Energy 是否出现在语言课程，还是只出现在新活动或特定学科；
5. Hearts 的初始数量、错误扣除、恢复练习、等待时间和订阅权益；
6. Profile 中 Avatar、成就、好友、League 历史和公开状态的实际布局；
7. Feed 是否仍是铃铛入口，哪些事件会同时进入 Feed 和 Push；
8. 动态 App Icon、Widget、活动衣服和限时联动是否在当前地区可见；
9. 订阅页面是否阻断 Lesson，免费用户关闭弹窗后回到哪里；
10. 当前题型、课程难度、推荐复习和 Score 的计算解释。

## 实测账户矩阵

正式观察需要至少准备以下账户和设备组合。没有该组合时，结果只能标记为“未观察”。

| 组合 | 平台 | 账号 | 课程上下文 | 目的 |
|---|---|---|---|---|
| A | iOS | 新用户 | 语言课程起点 | 首次使用、目标、第一课 |
| B | Android | 回归用户 | 已有 Streak | 连胜、通知、恢复 |
| C | Web | 公开档案 | 中段语言课程 | Leaderboard、Profile、Feed |
| D | iOS/Android | 订阅用户 | 中段 Unit | Hearts、Shop、订阅权益 |
| E | 任一 | 互相关注好友 | 同周活跃 | Friends Quest、Friend Streak |
| F | 任一 | 非活跃或关闭通知 | 任意课程 | 召回、隐私、退出路径 |

## 版本观察表

每次实测保存一份 JSON 或 Markdown 记录：

```text
observation_id：
captured_at：
timezone：
platform：
app_version_or_web_build：
locale_and_region：
account_state：
course_and_language_direction：
feature_name：
entry_point：
screen_sequence：
visible_copy：
interaction_result：
resource_changes：
task_changes：
notification_or_deeplink：
evidence_level：
source_or_screenshot_id：
uncertainty：
next_question：
```

## 证据与设计结论的分界

“官方文章展示了 Friends Quest”是公开事实；“Friends Quest 通过低表达成本促进关系承诺”是设计推断；“Friends Quest 能提高长期完成率”是效果假说，必须有当前版本行为数据或研究证据。类似地，“排行榜按 XP 排序”不等于“排行榜提高学习能力”，“徽章出现在 Profile”不等于“徽章让用户长期坚持”。

## BrainLab 的使用原则

BrainLab 只迁移机制，不复制未经授权的品牌资产。对每个拟借鉴的机制，先写清楚它解决的用户问题、依赖的产品条件、可能的副作用和验证指标。若一个机制的效果只在特定大规模网络、课程内容或商业边界中成立，就不能直接移植到认知训练产品。
