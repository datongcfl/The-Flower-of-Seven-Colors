# 酒店 PMS 代码审计 — 参考规范与对接资源

> 用途：审计 `datongcfl-repository` 内 12 个开源 PMS/脚手架代码时，作为「对照基准」与「行业参照系」。
> 维护日期：2026-07-08

---

## 1. 行业标准组织（权威参照系）

### 1.1 HTNG（Hotel Technology Next Generation）
- 官网：https://www.htng.org/
- 定位：酒店技术互操作标准联盟，成员含各大酒店集团与技术服务商。
- 与 PMS 相关的标准方向（审计对照用）：
  - 客房状态 / 房态接口（Room Status Interface）
  - 计费接口（Billing Interface，HTNG 2011b 系列）
  - PMS 与周边系统（渠道、门锁、电话、POS）的对接接口
- 说明：完整规范多需成员权限，公开页仅概述。审计时着重看开源 PMS 的「集成/接口设计」是否遵循通用房态与计费消息格式。

### 1.2 OpenTravel Alliance
- 官网：https://opentravel.org/
- 定位：旅游行业互操作标准组织，定义 XML/JSON 消息格式；正与 Linux Foundation 合作推进 **OpenTravel 2.0**（模型驱动，基于 DEx 工具生成 OpenAPI）。
- 酒店领域关键消息类型（审计数据模型覆盖度时对照）：
  - `OTA_HotelRes` — 酒店预订
  - `OTA_HotelRatePlan` — 费率 / 价盘计划
  - `OTA_HotelInvBlock` — 库存块
  - `OTA_HotelAvail` — 可用房查询
  - `OTA_HotelBookingRule` — 预订规则
- 规范获取：官网 Technical Resources → Download Specs / OTM Repository（首页为概述，具体 Schema 需从下载区获取）。

---

## 2. 本土 OTA 对接（携程 / 美团）— 开源空白区

**重要事实**：GitHub 上所有开源 PMS **都没有**携程/美团对接实现（均为 Booking / Expedia 思路）。
你们「综合对账系统」已自行实现了对接解析，这是第一手、最权威的本土对接事实来源：

| 渠道 | 你们已实现 | 定价/结算逻辑 |
|---|---|---|
| 携程 | `engine/excel_doctor.py` 解析携程结算单（入住/离店/结算价） | 折后价 − 商家优惠 → 扣点前 ×(1−扣点率) = 结算价（特牌15%/普通12%） |
| 美团 | 解析美团结算单（底价/自促/佣金） | 结算金额 = 订单底价 − 商家自促金额 |

公开平台（需登录开发者后台，SPA 静态抓取无实质内容）：
- 携程开放平台：https://open.ctrip.com/
- 美团技术服务合作中心：https://developer.meituan.com/ （住宿与旅行业务：`en-US/hotel`，提供综合 API）

**审计建议**：审开源 PMS 的「渠道 / OTA」模块时，重点看它们如何抽象「渠道适配器（Channel Adapter）」模式，再对比你们对账引擎的携程/美团解析，找出可复用或可改进点。

---

## 3. 安全与合规基线（审计必查项）

- **OWASP API Security Top 10 (2023)**：对象级授权失效、鉴权失效、过度数据暴露、资源消耗无限制等 —— 逐条对照那 12 个开源项目。
- **PCI-DSS**：支付卡数据处理规范（你们系统涉及结算/支付）。
- **等保 2.0**：国内合规要求（酒店类系统通常按三级等保对标）。

---

## 4. 参考开源代码仓库清单（本仓库内）

### 4.1 原始 6 个 PMS
| 文件夹 | 技术栈 | 备注 |
|---|---|---|
| `haip` | TypeScript monorepo | AI 驱动酒店代理平台，含 apps/packages/keycloak/skills |
| `erpnext_hospitality_core` | Python / Frappe | 基于 ERPNext 的酒店模块 |
| `HPMS_Tiny` | C# (.NET) + TypeScript | 轻量 PMS |
| `hoteldruid` | PHP | 老牌开源 PHP PMS |
| `QloApps` | PHP（基于 PrestaShop） | 14k 星，完整酒店预订/PMS |
| `minical` | PHP | 原 `minical/minical` 404，已用 `minical/online-booking-engine` 顶替 |

### 4.2 补拉的高质量 PMS（stars>50）
| 文件夹 | 技术栈 | 星标 | 备注 |
|---|---|---|---|
| `HOTEL-MANAGEMENT-PROJECT-JAVA` | Java | 426 | 高质量 Java 酒店管理（原 `SHOURYAJ98/HOTEL-MANAGEMENT-PROJECT-JAVA`） |
| `HOTELMANAGEMENT-VueSpringBoot` | Vue + Spring Boot | 391 | 中文前后端分离项目（原 `MYNAMEISLY/HOTELMANAGEMENT`） |

### 4.3 补拉的脚手架（权限/多租户参考，非 PMS）
| 文件夹 | 技术栈 | 星标 | 备注 |
|---|---|---|---|
| `RuoYi` | Java / Spring Boot | 8.4k | 若依 RBAC 权限脚手架（MIT），对标你们 `X-Tenant-ID` 多租户架构 |
| `HOTELHUB` | Java / Spring Boot | 8 | 多角色酒店预订管理（课设级，作 Java 系入门参考） |
| `PMS-HOTEL` | Node.js / React / Prisma | 1 | 纯 Node 独立轻量 PMS |
| `KAMRA-PMS` | TypeScript（Next.js + MCP） | 3 | 2026-07-08 当天更新的 AI 原生 PMS |

> 所有仓库均以 `--depth 1` 浅克隆并剥除各自 `.git`，避免与 `datongcfl-repository` 本仓库产生嵌套 git 冲突。
