import asyncio
import traceback
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.task import Task, TaskStatus, SearchMode
from app.models.platform_result import PlatformResult, PlatformStatus, ErrorCode
from app.models.lead import Lead, LeadCategory
from app.platforms.registry import PlatformRegistry
from app.platforms.unified_schema import UnifiedContent
from app.services.keyword_expander import KeywordExpander
from app.services.lead_analyzer import LeadAnalyzer
from app.services.cost_engine import CostEngine
from app.services.content_cache import ContentCache
from app.services.llm_client import LLMClient


class TaskEngine:
    def __init__(self):
        self._running: Dict[int, threading.Thread] = {}
        self._thread_futures: Dict[int, asyncio.Future] = {}
        self._cache = ContentCache.get("platform_search")

    @staticmethod
    def create_task(
        db: Session,
        query: str,
        search_mode: SearchMode = SearchMode.FAMILY_BUCKET,
        platforms: Optional[List[str]] = None,
    ) -> Task:
        default_platforms = platforms or PlatformRegistry.tier1()
        task = Task(
            query=query,
            search_mode=search_mode,
            platforms=default_platforms,
            status=TaskStatus.PENDING,
            progress=0.0,
            current_step="等待执行",
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    async def run_task_async(self, task_id: int):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            task.current_step = "初始化..."
            db.commit()

            llm = LLMClient()
            cost_engine = CostEngine(task_id=task_id)
            keyword_expander = KeywordExpander(llm=llm)
            analyzer = LeadAnalyzer(llm=llm, cost_engine=cost_engine)

            task.current_step = "关键词扩展中..."
            db.commit()
            keywords = await keyword_expander.expand(task.query, task.search_mode.value)
            task.expanded_keywords = keywords
            db.commit()

            platforms = list(task.platforms or [])
            total_platforms = max(1, len(platforms))
            platform_results: Dict[str, PlatformResult] = {}

            for idx, pname in enumerate(platforms):
                pr = PlatformResult(
                    task_id=task.id,
                    platform_name=pname,
                )
                adapter = PlatformRegistry.get(pname)
                if adapter:
                    pr.platform_tier = adapter.tier
                db.add(pr)
                db.commit()
                db.refresh(pr)
                platform_results[pname] = pr

            base_progress = 10.0

            for pidx, pname in enumerate(platforms):
                adapter = PlatformRegistry.get(pname)
                pr = platform_results[pname]
                pr.status = PlatformStatus.RUNNING
                pr.started_at = datetime.utcnow()
                db.commit()

                task.current_step = f"正在搜索 {pname}..."
                p_progress_start = base_progress + (pidx / total_platforms) * 70.0
                task.progress = round(p_progress_start, 1)
                db.commit()

                try:
                    available, err_code, err_msg = await adapter.is_available()
                    if not available:
                        pr.status = PlatformStatus.SKIPPED
                        pr.error_code = err_code or ErrorCode.NOT_SUPPORTED
                        pr.error_message = err_msg or "platform unavailable"
                        pr.completed_at = datetime.utcnow()
                        db.commit()
                        continue

                    cached = self._cache.lookup(pname, "search", keywords=sorted(set(keywords))[:20])
                    if cached:
                        unified_list_raw = cached
                    else:
                        raw_items, checkpoint = await adapter.search(keywords, checkpoint=pr.checkpoint, max_items=500)
                        unified_list_raw = [u.to_dict() for u in raw_items]
                        self._cache.store(pname, "search", unified_list_raw, keywords=sorted(set(keywords))[:20])

                    unified_items: List[UnifiedContent] = []
                    for d in unified_list_raw:
                        try:
                            from app.platforms.unified_schema import ContentType
                            pub = d.get("published_at")
                            if isinstance(pub, str):
                                try:
                                    pub = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                                except Exception:
                                    pub = None
                            uc = UnifiedContent(
                                platform=d["platform"],
                                content_type=ContentType(d["content_type"]),
                                raw_id=d["raw_id"],
                                title=d.get("title"),
                                content=d.get("content"),
                                url=d.get("url"),
                                author_name=d.get("author_name"),
                                author_url=d.get("author_url"),
                                author_company=d.get("author_company"),
                                author_location=d.get("author_location"),
                                published_at=pub,
                                language=d.get("language"),
                                location=d.get("location"),
                                tags=list(d.get("tags") or []),
                                metadata=dict(d.get("metadata") or {}),
                                engagement=dict(d.get("engagement") or {}),
                            )
                            unified_items.append(uc)
                        except Exception:
                            continue

                    pr.raw_items_count = len(unified_items)
                    pr.unified_data = unified_list_raw[:100]
                    pr.checkpoint = None
                    db.commit()

                    task.current_step = f"正在AI分析 {pname} ({len(unified_items)} 条)"
                    db.commit()

                    leads: List[Lead] = []
                    leads_hi_count = 0
                    for ci, content in enumerate(unified_items):
                        try:
                            analysis = await analyzer.analyze_content(content)
                            lead = analyzer.content_to_lead(task.id, content, analysis)
                            if adapter and hasattr(adapter, "name"):
                                cost_engine.log_platform_api(adapter.name, 1, 0.0005)
                            leads.append(lead)
                            if lead.is_high_intent:
                                leads_hi_count += 1
                        except Exception:
                            continue
                        if (ci + 1) % 20 == 0:
                            db.add_all(leads)
                            db.commit()
                            leads.clear()
                        p_mid = p_progress_start + ((ci + 1) / max(1, len(unified_items))) * (70.0 / total_platforms) * 0.7
                        task.progress = round(min(p_mid, 92.0), 1)
                    if leads:
                        db.add_all(leads)
                    pr.leads_extracted = leads_hi_count
                    pr.unified_items_count = len(unified_items)
                    pr.status = PlatformStatus.COMPLETED
                    pr.completed_at = datetime.utcnow()
                    db.commit()
                except Exception as e:
                    pr.status = PlatformStatus.FAILED
                    pr.error_code = ErrorCode.API_ERROR
                    pr.error_message = f"{e}\n{traceback.format_exc()[-500:]}"
                    pr.completed_at = datetime.utcnow()
                    db.commit()
                task.progress = round(base_progress + ((pidx + 1) / total_platforms) * 70.0, 1)
                db.commit()

            task.current_step = "汇总统计中..."
            task.progress = 95.0
            db.commit()
            self._refresh_stats(db, task.id)
            task.progress = 100.0
            task.current_step = "完成"
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = TaskStatus.FAILED
                task.error_message = f"{e}\n{traceback.format_exc()[-2000:]}"
                task.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
            if task_id in self._running:
                try:
                    del self._running[task_id]
                except Exception:
                    pass

    def _refresh_stats(self, db: Session, task_id: int):
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        leads = db.query(Lead).filter(Lead.task_id == task_id).all()
        categories = set(l.category for l in leads)
        task.total_contents = len(leads)
        task.total_high_intent_leads = sum(1 for l in leads if l.is_high_intent)
        task.total_companies = sum(1 for l in leads if l.category == LeadCategory.COMPANY or (l.company_name and l.company_name.strip()))
        task.total_communities = sum(1 for l in leads if l.tags and ("community" in " ".join(l.tags).lower() or "group" in " ".join(l.tags).lower()))
        task.total_demands = sum(1 for l in leads if l.category == LeadCategory.DEMAND)
        task.total_company_opportunities = sum(1 for l in leads if l.category == LeadCategory.OPPORTUNITY)
        task.total_trends = sum(1 for l in leads if l.category == LeadCategory.TREND)
        task.total_competitions = sum(1 for l in leads if l.category == LeadCategory.COMPETITION)
        db.commit()

    def start_task(self, task_id: int):
        if task_id in self._running and self._running[task_id].is_alive():
            return

        def _runner():
            try:
                asyncio.run(self.run_task_async(task_id))
            except Exception:
                pass
            finally:
                if task_id in self._running:
                    try:
                        del self._running[task_id]
                    except Exception:
                        pass

        t = threading.Thread(target=_runner, daemon=True, name=f"task-{task_id}")
        self._running[task_id] = t
        t.start()

    def is_running(self, task_id: int) -> bool:
        t = self._running.get(task_id)
        return bool(t and t.is_alive())


_engine: Optional[TaskEngine] = None


def get_task_engine() -> TaskEngine:
    global _engine
    if _engine is None:
        _engine = TaskEngine()
    return _engine
