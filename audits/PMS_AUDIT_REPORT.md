# 酒店 PMS 开源代码审计总报告

> 审计对象：`datongcfl-repository` 内 12 个开源 PMS / 脚手架（均浅克隆 + 剥 `.git`）
> 审计规则：`PMS_AUDIT_RULES.md`（五类：功能模块 / 数据模型 / 安全 / 集成架构 / 工程质量）
> 审计日期：2026-07-08
> 判定符号：✓ 覆盖 / ⚠ 部分或有风险 / ✗ 缺失

---

## 一、12 仓总览评分表

| # | 仓库 | 技术栈 | ①功能 | ②数据 | ③安全 | ④集成 | ⑤质量 | 综合 |
|---|---|---|---|---|---|---|---|---|
| 1 | haip | TS/NestJS+PG | ✓ | ✓ | ✓ | ⚠ | ✓ | **A 最成熟** |
| 2 | erpnext_hospitality_core | Python/Frappe | ✓ | ⚠ | ⚠ | ✗ | ⚠ | B+ |
| 3 | KAMRA-PMS | Py/Frappe+MCP | ✓ | ✓ | ⚠ | ✗ | ✓ | B+ |
| 4 | QloApps | PHP/PrestaShop | ⚠ | ✓ | ⚠ | ✗ | ⚠ | B |
| 5 | PMS-HOTEL | Node/React/Prisma | ⚠ | ✓ | ⚠ | ✗ | ⚠ | B |
| 6 | HPMS_Tiny | .NET/React | ⚠ | ✓ | ⚠ | ✗ | ✓ | B- |
| 7 | hoteldruid | PHP 过程式 | ⚠ | ⚠ | ✗ | ⚠ | ✗ | C+ |
| 8 | HOTELMANAGEMENT-VueSpringBoot | Vue+Spring Boot | ⚠ | ⚠ | ⚠ | ✗ | ⚠ | C+ |
| 9 | HOTELHUB | Java/Spring Boot | ⚠ | ⚠ | ⚠ | ✗ | ✓ | C+ |
| 10 | minical | PHP/CodeIgniter | ⚠ | ⚠ | ⚠ | ⚠ | ⚠ | C |
| 11 | RuoYi | Java/Spring Boot RBAC | —(脚手架) | — | ⚠ | ⚠ | ✓ | 参考 |
| 12 | HOTEL-MANAGEMENT-PROJECT-JAVA | Java 单文件 | ✗ | ✗ | ✗ | ✗ | ✗ | 教学 demo |

> 评分说明：①~⑤ 取各仓库报告中主导判定；综合=A 生产可用 / B 可借鉴模块 / C 仅参考 / 参考=非PMS脚手架。

---

## 二、逐仓库审计报告

### 1. haip（Telivity Hotel AI Platform）
**技术栈**：TypeScript(strict)+NestJS+PostgreSQL(Drizzle)+Redis/BullMQ+Keycloak+Stripe+React；pnpm monorepo；Vitest 1100 测试。
**①功能**✓：预订/房态/入住退房/价盘/账务/夜审/会员/Booking·Expedia·SiteMinder 适配器/报表/property_id 隔离 RBAC 齐全。
**②数据**✓：Reservation/RoomType/RatePlan/Availability 贴近 OTA 标准；金额 `numeric(12,2)`+币种+税率，无浮点（缺 BookingRule 独立表）。
**③安全**✓：BOLA 靠 property_id 双层隔离、Keycloak 鉴权、限流、SSRF url-guard、审计日志；PCI 仅存 token；等保⚠（默认 `AUTH_ENABLED=false`）。
**④集成**✓：ChannelAdapter 接口+各 OTA 隔离实现+mapper；配置分离；`/api/v1`；⚠ 重试补偿仅 sync-log 审计、无显式事务补偿。
**⑤质量**✓：分层+统一异常过滤器；1100+ 测试；文档详尽；复用成熟库。
**差距**：缺携程/美团直连与 OTA 对账（你们强项）；无内置对账差异模块。
**借鉴**：① `numeric` 金额+存款负债分类(Deposit Ledger) 严谨账务；② 渠道适配器+字段映射范式；③ 双层租户隔离(请求边界+数据层 fail-closed)。
**风险**：默认关闭鉴权；渠道推送缺显式重试补偿（断网易丢同步）。

### 2. erpnext_hospitality_core（Hospitality Core for ERPNext）
**技术栈**：Python+Frappe v14+/ERPNext；DocType 元数据驱动；MariaDB。
**①功能**✓：预订/房态/入住退房/价盘/账务/City Ledger/夜审(14:00)/会员/报表/角色权限齐全，仅缺 OTA。
**②数据**⚠：有 Reservation/RatePlan/Room/Inv 模型；金额用 `flt()` **浮点**（非 Decimal）；缺 BookingRule。
**③安全**⚠：依赖 Frappe 默认鉴权；无独立 OWASP/PCI/等保设计。
**④集成**✗：无 OTA 适配器/配置分离/版本/重试（刻意"Control not Connectivity"）。
**⑤质量**⚠：事件钩子分层清晰；含少量测试与文档；根目录散落大量 debug/verify 脚本。
**差距**：零 OTA 对接与对账（与你们相反）；金额浮点弱于你们 Decimal。
**借鉴**：① City Ledger 公司/团体 Folio 镜像与转账；② 夜审 `already_charged_today` 防重复计费+营业日归属；③ Folio 余额重算+作废需经理审批的财务内控。
**风险**：零 OTA+对账能力；金额浮点隐患；根目录散落 debug 脚本（越权执行风险）。

### 3. KAMRA-PMS
**技术栈**：Python+Frappe+React；MCP-first(FastMCP 17+ 工具)；Razorpay 支付。
**①功能**✓：预订/房态/入住退房/价盘/账务(Folio+GST)/夜审/会员/报表/六角色 RBAC 多租户；✗ 无 OTA 适配器。
**②数据**✓：Reservation/RatePlan/RoomType/Folio doctype；金额 `Decimal`；⚠ 未显式对照 OTA 字段，BookingRule 内嵌策略。
**③安全**✓：RBAC(authz role 装饰器)+现金 PIN+Webhook HMAC+审计日志；⚠ 限流未见、PCI 卡明文未证、等保未声明。
**④集成**⚠：Voice/WhatsApp provider-agnostic 适配器雏形；配置分离/版本/重试弱（outbound best-effort）。
**⑤质量**✓：分层+统一 `frappe.throw`；27 单测+18 CI eval；文档齐全。
**差距**：完全无携程/美团 OTA 对账（你们 `fetch_xiecheng/fetch_meituan`+reconciler 是其空白）。
**借鉴**：① 确定性定价引擎(Decimal+季节/价盘/券/税链，AI 不碰钱)；② 治理化 MCP 工具层(role 限定+Autonomy Gate+Action Log 全审计)；③ 价盘护栏(rate floor/ceiling 系统级强制)。
**风险**：缺 OTA 对接与限流/重试；支付卡与等保未落实。

### 4. QloApps
**技术栈**：PHP 8.1+/MySQL/PrestaShop 内核(OSL-3.0)；模块式；SOAP/REST Webservice。
**①功能**⚠：预订/房态/入住退房/价盘/账务/会员齐全；**无夜审**；OTA 仅自家 Channel Manager。
**②数据**✓：`decimal(20,6)` 金额精度好；预订/房型/库存/可用房齐备，覆盖 OTA 主体字段。
**③安全**⚠：复用 PrestaShop 鉴权加密(defuse/php-encryption)；无自研审计日志/PCI/等保/限流。
**④集成**✗：仅 `qlochannelmanagerconnector` 单 IP 白名单对接 Webkul CM；无携程/美团/Booking 适配、无重试/版本。
**⑤质量**⚠：分层清晰；**无测试目录**；文档偏安装向。
**差距**：缺夜审、缺携程/美团 OTA 对账、缺测试与等保，渠道薄弱。
**借鉴**：① 金额全程 `decimal(20,6)`+含税/不含税双字段；② 房型特征/需求定价/退款规则模型完整；③ ARI Webservice 可用房态查询接口设计清晰。
**风险**：渠道适配缺失、无夜审、无测试、耦合 PrestaShop 内核难独立部署。

### 5. PMS-HOTEL（"PMS centralizado"）
**技术栈**：React/TS+Node/Express+Prisma/PostgreSQL+JWT+BCrypt；多酒店租户；偏餐饮 POS+哥斯达黎加电子发票。
**①功能**✓：预订/房态/入住退房/价盘/账务/会员/多租户；✗ 夜审（仅 CashAudit 收银班次）、✗ OTA；⚠ 报表基础。
**②数据**✓：Reservation/RatePlan/RateOverride/RoomType/RoomDay/Availability；金额全 `Decimal(12,2)`；⚠ BookingRule 仅简单建模。
**③安全**✓：tenantCtx 拒 header 越权+requirePermission+限流+审计日志；✗ 无 PCI 合规设计；等保⚠。
**④集成**✗：仅 Contract.channel 字符串，无适配器；配置分离✓；API 版本⚠；重试✗。
**⑤质量**✓：分层+统一错误处理；✗ 0 测试；⚠ README 全西语无 API 文档。
**差距**：无 OTA 适配器/对账、无夜审；你们有携程/美团 OTA 对账更贴国内。
**借鉴**：① `tenantCtx` 拒 header 注入+`auditMiddleware` 审计日志(等保友好)；② Decimal+RoomDay 逐日房态/房价建模；③ RBAC+多酒店 SaasClient 隔离。
**风险**：无 OTA/对账/夜审、零测试、无中文文档、无 PCI/等保三级。

### 6. HPMS_Tiny（HotelPms）
**技术栈**：.NET 8/ASP.NET Core+EF Core+MSSQL；React18+TS；Keycloak 24；Docker；QuestPDF。
**①功能**⚠：预订/房态/入住退房/账务✓；价盘✗(仅 BasePrice)、夜审✗、会员⚠、OTA✗、报表✗(仅发票PDF)、多租户⚠(RBAC无Tenant)。
**②数据**✓：金额 `decimal`(无浮点)；Res✓/InvBlock✓/Avail✓；缺 RatePlan/BookingRule。
**③安全**⚠：Keycloak JWT✓、限流✓、审计✓；⚠ BOLA 未逐对象校验、批量分配弱、占房无总次数限、SSRF 未防护、**默认弱口令 manager/admin**、Swagger 生产暴露。
**④集成**✗：无适配器/重试；配置分离✓；`/api/v1`✓。
**⑤质量**✓：分层+统一；xUnit 测试✓；文档✓。
**差距**：缺夜审/价盘/OTA/多租户/对账——纯单体前台，无中式渠道对账。
**借鉴**：① Keycloak+资源级授权 handler 的 RBAC 落地；② decimal 金额+VAT 的 Folio 模型；③ 容量感知可用性/占房防竞争。
**风险**：默认弱口令、Swagger 暴露、无多租户、无 OTA/夜审/对账。

### 7. hoteldruid
**技术栈**：PHP 5/7 过程式（非框架）；多数据库适配；内置 API+互联模块。
**①功能**⚠：预订/房态/价盘/账务/权限齐全；缺会员/OTA/夜审/多租户专用模块。
**②数据**⚠：有合同/客户/价格表；未对齐 OTA 标准；金额用浮点字符串，无十进制保障。
**③安全**✗：API 明文密码比较(`$pass==$pass_api`)、`$_POST/$_GET` 动态变量覆盖(RCE)、缺 CSRF/参数化/PCI/等保。
**④集成**⚠：有互联模块非适配器；配置耦合代码；无版本/重试。
**⑤质量**✗：巨型单文件(>300KB)、无分层、无测试、文档仅多语言 README。
**差距**：缺携程/美团 OTA 对账、会员营销、夜审自动化、多租户隔离。
**借鉴**：① 多数据库抽象层；② 细粒度年度权限(privilegi)模型；③ 内置 API 限流+失败登录计数。
**风险**：过程式+动态变量覆盖致 RCE/越权高危，不适合直接生产。

### 8. HOTELMANAGEMENT-VueSpringBoot（含同源 HOTELHUB 后端）
**技术栈**：前端 Vue3+Element UI+Vuex；后端同源 HOTELHUB 为 Spring Boot 3+Spring Security+JWT+JPA。
**①功能**⚠：预订/房态/入住退房/账务/会员/权限；缺价盘促销/夜审/OTA/对账报表。
**②数据**⚠：Booking/Invoice/RoomType 用 BigDecimal；无 RatePlan/Avail/InvBlock/BookingRule。
**③安全**⚠：JWT+RBAC 基础；CSRF 关闭、无限流、无审计日志、等保未落地。
**④集成**✗：无适配器/OTA；仅 `/api/v1` 前缀。
**⑤质量**⚠：分层清晰、全局异常+DTO Mapper；仅 1 个空测试；文档缺。
**差距**：贵司有携程/美团 OTA 对账/夜审/多租户(X-Tenant-ID)，本仓库均无；**前端与 HOTELHUB 后端接口路径不一致，仓库实为纯前端脚手架**。
**借鉴**：① BigDecimal 金额+税/折扣/净额分离；② 标准 Spring 分层+DTO/Entity Mapper；③ JWT 无状态+角色继承权限雏形。
**风险**：前后端 API 脱节不可直接复用；缺 OTA/对账/夜审/多租户；无 API 限流与审计日志。

### 9. HOTELHUB（KhaledAshrafH/HotelHub）
**技术栈**：Spring Boot+JPA+MySQL+Spring Security/JWT+MapStruct+SpringDoc；JDK11+。
**①功能**⚠：预订/房态/入住退房/发票/支付/权限(ADMIN/STAFF/GUEST)；缺夜审/OTA/报表/会员积分/价盘促销。
**②数据**⚠：Booking/Payment/Invoice 用 BigDecimal；无 OTA 标准对照、无 BookingRule。
**③安全**⚠：JWT+RBAC 基础；缺限流、BOLA 弱、无审计日志、密码明文存储隐患、CORS 仅 localhost。
**④集成**✗：完全无 OTA 适配器/配置分离/版本/重试。
**⑤质量**✓：分层+@RestControllerAdvice 统一异常+SpringDoc+MapStruct；测试仅 1 空壳类。
**差距**：教学级单体，缺夜审/OTA/对账/RatePlan——你们在渠道对账与营业日归属远超它。
**借鉴**：① BigDecimal 金额+Invoice 税费拆分；② 清晰分层与 DTO/Entity 分离(MapStruct)；③ SpringDoc 自动 API 文档。
**风险**：无 OTA/对账/夜审；BOLA 缺防护、无审计日志、密码未确认加密、无 API 限流。

### 10. minical（online-booking-engine）
**技术栈**：PHP+CodeIgniter（miniCal 扩展）；MySQL；信用卡 iframe tokenize；仅面向客人的预订引擎。
**①功能**⚠：预订/房态/价盘/账务/渠道同步；缺夜审/入住退房/会员/报表/独立权限(依赖父框架)。
**②数据**⚠：booking/rate_plan/room_type/currency 模型；无显式 OTA 映射；金额精度未约束(浮点风险)。
**③安全**⚠：信用卡 iframe tokenize(PCI 友好)；但多处 SQL 字符串拼接 `$company_id` 注入风险；无独立鉴权/审计。
**④集成**⚠：有 roomsy 渠道管理器+集成日志；无统一适配器/配置分离/版本/重试。
**⑤质量**⚠：controller/model/view 分层；错误处理仅 show_error；**无测试目录**；文档仅 README。
**差距**：缺携程/美团 OTA 对账/夜审/营业日归属/报表差异，仅为前端预订壳。
**借鉴**：① 信用卡 iframe tokenize 隔离 PAN(PCI 思路)；② rate_plan/date_range restriction 建模；③ company_id 多租户隔离雏形。
**风险**：SQL 拼接注入、无测试、无重试补偿、缺夜审与对账。

### 11. RuoYi v4.8.3（权限/安全脚手架，非 PMS）
**技术栈**：Java+Spring Boot+Apache Shiro+MyBatis+Thymeleaf+Druid。
**①RBAC/数据权限**✓：用户-角色-菜单-部门完整模型；`@DataScope` 切面按 5 级范围拼 SQL 过滤。
**②模型**✓：SysUser/SysRole/SysMenu/SysDept 齐全。
**③安全**⚠：登录/操作日志/CSRF/验证码/防重提交；无 API 限流、无 PCI、等保三级不完整；**单租户无 tenant 概念**。
**④集成**⚠：配置与代码分离；无 API 版本/适配器。
**⑤质量**✓：分层+统一 AjaxResult+全局异常；单测缺失；文档偏使用向。
**差距**：RuoYi 单租户，全仓无 tenant；你们 `X-Tenant-ID` 多租户+行级隔离测试是其没有的；数据权限靠部门树非门店维度。
**借鉴**：① `@DataScope` 注解+AOP 自动注入数据范围 SQL(零侵入)；② Shiro Realm+Filter 链会话治理(踢出/在线/同步)；③ 统一操作/登录日志审计骨架。
**风险**：数据权限靠 `BaseEntity.params` 拼 SQL(虽防注入但管理员 bypass)、无租户隔离、无 API 限流。

### 12. HOTEL-MANAGEMENT-PROJECT-JAVA（单文件 demo）
**技术栈**：Java 单文件 Main.java（20KB 控制台菜单，ObjectOutputStream 落盘）；仅 4 文件。
**判定**：①⚠ 仅房态/预订/退房/餐饮账单；②✗ 无 OTA 模型、金额 float/double 浮点；③✗ 无认证/授权/加密/审计；④✗ 全无；⑤✗ 全静态方法堆 Main 类。
**结论**：纯教学 demo，审计价值低，无借鉴价值；风险：浮点精度、不安全反序列化(readObject)、房间号边界未校验。

---

## 三、横向对比与结论

### 3.1 12 个仓库的**共性缺失**（你们 hotel-pms 的独有优势）
1. **携程/美团 OTA 适配器 + 对账引擎：12 个全部缺失**。开源 PMS 只对接 Booking/Expedia/SiteMinder，无一家做中式 OTA 结算单解析与差异对账——这是你们对账系统的**核心壁垒**，开源里找不到对标。
2. **夜审（Night Audit）/ 营业日归属**：仅 haip、erpnext、KAMRA 有；其余 9 个缺。你们 14:00 营业日规则是成熟实践。
3. **渠道适配器模式（Channel Adapter）**：仅 haip 清晰实现；其余多为字符串字段或单 IP 对接，无隔离实现。
4. **多租户隔离**：仅 PMS-HOTEL（tenantCtx）、haip（双层）、RuoYi（仅数据权限雏形）有；你们 `X-Tenant-ID` 行级隔离是明确实现且更规范。
5. **自动化测试**：仅 haip(1100+)、KAMRA(27) 充分；其余多为 0~1 个空壳测试。

### 3.2 12 个仓库的**共性弱点**（安全）
- API 限流(API4)、审计日志(API10)、SSRF 防护(API7)、BOLA 对象级授权(API1) 普遍不足。
- 金额精度：hoteldruid / HOTEL-MANAGEMENT-PROJECT-JAVA / minical 用浮点→有精度风险；其余用 Decimal/BigDecimal→正确（你们应已遵循）。
- 等保 2.0 / PCI-DSS：基本无项目做完整合规落地。

### 3.3 最值得你们借鉴的点（Top 5）
1. **haip 的渠道适配器 + 字段映射范式 + 双层租户隔离** —— 若你们未来要抽象"渠道对接层"，这是最佳范本。
2. **erpnext / KAMRA 的夜审 + Folio 财务内控**（防重复计费、经理审批、余额重算）—— 强化你们夜审与账务。
3. **RuoYi 的 `@DataScope` 数据权限 AOP** —— 可借鉴到你们 `X-Tenant-ID` 多租户行级隔离，零侵入注入。
4. **普遍 Decimal/BigDecimal 金额建模** —— 验证你们做法正确，继续坚持。
5. **KAMRA 的"AI 不碰钱"确定性定价引擎 + 价盘护栏** —— 若你们引入 AI 收益管理，这是安全范式。

### 3.4 对你们 hotel-pms 的启示
- **你们已领先**：OTA 对账（携程/美团结算单解析+差异定位）、营业日归属、多租户隔离——开源无对标，是产品护城河。
- **可补齐**：夜审财务内控（借鉴 erpnext/KAMRA）、渠道层抽象（借鉴 haip）、数据权限 AOP 化（借鉴 RuoYi）、金额精度已正确。
- **需加固**：对照 OWASP API Top 10 补齐限流/审计日志/SSRF/BOLA（这 12 个开源都没做好，但生产必须做）。

---

## 四、配套文档
- `PMS_AUDIT_REFERENCE.md`：标准来源（HTNG / OpenTravel / 携程美团 / 安全基线 / 仓库清单）
- `PMS_AUDIT_RULES.md`：五类审计规则与可勾选检查清单
