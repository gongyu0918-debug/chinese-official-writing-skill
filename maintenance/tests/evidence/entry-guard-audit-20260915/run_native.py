"""Bounded real-writing pairs for issuer roles and plain/Markdown delivery."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py"
spec = importlib.util.spec_from_file_location("entry_guard_native", SOURCE)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

NOTICE = "业务科、资料室于9月18日下午3时在二楼会议室参加档案整理培训。参会回执请于9月16日前报办公室，接收邮箱为office@example.org，联系人是王老师。"
PROCUREMENT = "海岚市档案服务中心拟采购扫描仪3台，最高限价合计1.8万元；采用公开询价，报名截止2026年9月25日17时，材料交市档案服务中心综合科，联系人李工，电话020-81234567。公告只发布这些已明确事项，不增加资质、评审标准或履约要求。"
runner.CASES = {
    "issuer_missing": "请根据这些安排写一则简短通知：" + NOTICE,
    "issuer_given": "请以综合办公室名义发出一则简短通知，主送业务科和资料室：" + NOTICE,
    "plain_default": "以下为虚拟写作材料。请拟采购公告：" + PROCUREMENT,
    "markdown_requested": "以下为虚拟写作材料。请用Markdown写采购公告，标题用一级标题，采购信息用表格：" + PROCUREMENT,
}

if __name__ == "__main__":
    runner.main()
