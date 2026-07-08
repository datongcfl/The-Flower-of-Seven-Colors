# 自有 hotel-pms 代码审计报告

> 审计对象：`D:\福昶工作目录\hotel-pms`（Django 5.1 / DRF / PostgreSQL 15 / Redis / Celery / Vue3，SaaS 多租户 PMS + 物资商城）
> 审计日期：2026-07-08
> 规则来源：`PMS_AUDIT_RULES.md`（与 12 个开源 PMS 同套五类规则）
> 说明：OTA 携程/美团对接与对账不在本 PMS，已确认在独立 `reconciliation/` 对账系统实现，本审计不计入缺失。

---

## 一、总览判定

| 域 | 功能落地 | 数据模型 | 安全 | 集成架构 | 工程质量 | 综合 |
|---|---|---|---|---|---|---|
| common / platform | ✓ | ✓ | ⚠ | ⚠ | ✓ | **B+** |
| pms（核心业务） | ✓ | ⚠ | ⚠ | ✗ | ✓ | **B+** |
| commerce（商城） | ✓ | ✓ | ⚠ | ⚠ | ✓ | **B+** |
| integrations（支付/短信/门锁/OTA） | ✗ | ✗ | ✗ | ✗ | ✗ | **未开发（空壳）** |

**总体结论**：代码完成度与工程质量**显著高于**已审的 12 个开源 PMS（那 12 个最佳 haip 为 A，多数 C+ 及以下）。自有代码在**多租户隔离、金额精度、事务并发、状态机/幂等/审计基础设施**上已具备生产级雏形。主要短板集中在 **integrations 域完全空壳**、**价盘/渠道价模型缺失**、**users 表 RLS 缺口**三处。

---

## 二、各域详情

### 2.1 common / platform（通用工具 + SaaS 平台）
- **✓ 已落地**：`TenantManager` 拦截裸 `.all()/.filter()`；`BaseAPIView.check_required_permission` 真实校验 56 个权限码；`X-Hotel-Id` 校验酒店作用域；PG RLS 迁移 `FORCE ROW LEVEL SECURITY` 兜底；`money()` Decimal 量化到分（无 float）；JWT 存 httpOnly Cookie 防 XSS；`UserRole.save()` 校验同租户绑定。
- **⚠ 风险**：
  1. **`User`/`Role`/`Permission` 模型用普通 Manager 无租户拦截，且 RLS 策略表不含 `users` 表**——裸查 `User.objects.filter(...)` 不写 `tenant_id` 会跨租户泄露。这是当前**最严重的安全缺口**，依赖 service 层自觉。
  2. 状态机 `transit` 不强制 `required_permission` / `requires_reason`（仅声明），越权校验压在调用方。
  3. `SECURE` / `SESSION_COOKIE_SECURE` 未在生产 settings 强制。
  4. superuser 绕过权限码（设计如此，需监控）。

### 2.2 pms（预订/房态/入住/账页/夜审/报表）
- **✓ 已落地**：`create_reservation`/`cancel_reservation` + 状态机；`Room.sellable_status` + `housekeeping_status` + 事件日志；`checkin/walkin/extend_stay/shorten_stay/checkout_confirm` 齐全；Folio 流水 append-only、正负净额汇总、补收/多退/押金抵扣完整；`run_night_audit`（预检查→自动房费→快照→推进 `current_business_date`）**真实健壮、幂等**；全程 `DecimalField`；金额操作 `@transaction.atomic` + `select_for_update`。
- **⚠ 风险/缺失**：
  1. **价盘模型缺失**：仅 `RoomType.base_price`，无促销价/渠道价/RatePlan 模型。结算口径只取 base_price，与对账系统 OTA 折后价脱节。
  2. **无 OTA 渠道建模**：`Reservation.source` 仅 frontdesk/walk_in 字符串，无 Channel Adapter（已确认 OTA 在对账系统，本 PMS 不自含，可接受）。
  3. **无 No-show / 担保规则**状态。
  4. **报表薄弱**：仅夜审 `ReportSnapshot`(in_house_count)，无营业报表/对账差异接口。
  5. **预订并发超售竞态**：`create_reservation` 锁房型/房间，但 `_validate_room_request` 在事务内先查后插，房型级库存用 count 比较存在竞态窗口。建议加库存唯一约束或对计数行 `SELECT ... FOR UPDATE`。
  6. 未检索到限流 / 审计日志中间件（审计日志在业务层 append-only，缺 HTTP 层）。

### 2.3 commerce（物资商城）
- **✓ 已落地**：catalog/orders/inventory/after_sales/reports 齐全；订单状态机（草稿→完成）；库存预占/扣减 `select_for_update` + 价格快照 + 幂等 + append-only 流水 + RLS 隔离，**设计质量高**，可复用至对账系统订单侧。`tests/commerce` 8 文件覆盖订单/库存/售后/隔离。
- **⚠ 风险/缺失**：
  1. 全积分制（`PositiveIntegerField`），**无现金 `Decimal` 金额**（MVP 明确不接支付，可接受，但接支付时需补 Decimal 精度 + 验签）。
  2. **工单（work order）模块缺失**。
  3. **Celery 未实际使用**，失败补偿依赖事务回滚，无异步重试。

### 2.4 integrations（支付/短信/门锁/OTA）
- **✗ 纯空壳**：`apps/integrations/` 仅 `apps.py` + 空 `urls.py`，`payments/sms/door_locks/ota` 四目录**均为空占位**，无任何适配器代码。符合 README "骨架/占位" 规划，属尚未开发，非硬编码密钥问题。OTA 对接在外部对账系统，本 PMS 不自含。

---

## 三、相对 12 个开源 PMS 的优势

1. **多租户双保险真实落地**（应用层 Manager 拦截 + PG RLS `SET LOCAL`）——12 个开源无一做到。
2. **金额全 Decimal 精度、事务+行锁并发控制**——开源多为 float / 无锁（如 PMS-HOTEL 用 Decimal 但无 RLS）。
3. **夜审、Folio 正负净额、状态机、幂等、审计日志**为自研基础设施且带隔离测试——开源多为 C+ 且无测试。
4. **JWT httpOnly Cookie + RBAC 56 码 + X-Hotel-Id 作用域**——开源普遍缺失细粒度数据权限。

## 四、必须修复 / 重点补齐（按优先级）

1. **【高危·安全】补 `users` 表 RLS + 给 User/Role/Permission 模型加租户 Manager**：消除跨租户泄露唯一缺口。
2. **【高·业务】价盘/渠道价 RatePlan 模型**：否则 OTA 结算口径与对账系统对不上，是你们最核心的"对账"链路断点。
3. **【中·安全】状态机内聚 `required_permission`/`requires_reason` 校验**；生产 settings 强制 `SECURE`/`SESSION_COOKIE_SECURE`。
4. **【中·稳定】预订库存竞态**：加唯一约束或计数行 `FOR UPDATE`，防超售。
5. **【低·规划】integrations 域**：按优先级实现 OTA 适配器（可借鉴 haip 的 Channel Adapter 范式）、支付回调验签（密钥入 env）、短信/门锁。
6. **【低·可观测】HTTP 层限流 + 审计日志中间件**；丰富营业报表。

---

## 五、可借鉴的开源点（回填到自有代码）

- **haip** 的 Channel Adapter 范式 → 用于后续 integrations/ota 实现。
- **erpnext / KAMRA-PMS** 的夜审财务内控 → 可进一步增强本 PMS 夜审的差异校验。
- **RuoYi** 的 `@DataScope` 数据权限 AOP → 加固多租户隔离（与现有 RLS 互补）。
- 12 个开源共同的限流/审计/SSRF 软肋 → 提醒：**这些不要参考它们，要自己补齐**。
