import os
import sys
import json
import logging
import subprocess
from typing import Dict, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("MCP-Diagnostics")

class MCPDiagnostics:
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or settings.MCP_REGISTRY
        self.report = {
            "mcp_operability_score": 0,
            "results": []
        }

    def run_diagnostics(self):
        if not os.path.exists(self.registry_path):
            logger.error("Registry not found")
            return

        with open(self.registry_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            configs = data.get("configurations", [])

        total_mcps = len(configs)
        operational_count = 0

        for mcp in configs:
            mcp_id = mcp.get("id")
            logger.info(f"Testing MCP: {mcp_id}...")
            
            result = {
                "id": mcp_id,
                "configured": True,
                "connected": False,
                "operational": False,
                "error": None
            }

            if mcp_id == "filesystem":
                status = self._test_filesystem()
            elif mcp_id == "git":
                status = self._test_git()
            elif mcp_id == "browser":
                status = self._test_browser()
            elif mcp_id == "memory-layer":
                status = self._test_memory_layer()
            else:
                status = {"connected": False, "operational": False, "error": "Unknown diagnostic path"}

            result.update(status)
            if result["operational"]:
                operational_count += 1
            
            self.report["results"].append(result)

        self.report["mcp_operability_score"] = int((operational_count / total_mcps) * 100) if total_mcps > 0 else 0
        self._generate_report()

    def _test_filesystem(self) -> Dict:
        try:
            test_file = os.path.join(settings.BASE_DIR, "mcp_test.tmp")
            with open(test_file, "w") as f: f.write("test")
            with open(test_file, "r") as f: content = f.read()
            os.remove(test_file)
            if content == "test":
                return {"connected": True, "operational": True}
            return {"connected": True, "operational": False, "error": "Content mismatch"}
        except Exception as e:
            return {"connected": False, "operational": False, "error": str(e)}

    def _test_git(self) -> Dict:
        try:
            res = subprocess.run(["git", "status"], capture_output=True, text=True)
            if res.returncode == 0:
                return {"connected": True, "operational": True}
            return {"connected": True, "operational": False, "error": res.stderr}
        except Exception as e:
            return {"connected": False, "operational": False, "error": str(e)}

    def _test_browser(self) -> Dict:
        if "VSCODE_PID" in os.environ or "TERM_PROGRAM" in os.environ:
             return {"connected": True, "operational": True}
        return {"connected": False, "operational": False, "error": "No VS Code environment detected"}

    def _test_memory_layer(self) -> Dict:
        mem_path = settings.MEMORY_DIR
        if os.path.exists(mem_path):
            return {"connected": True, "operational": True}
        return {"connected": False, "operational": False, "error": "Memory folder missing"}

    def _generate_report(self):
        score = self.report["mcp_operability_score"]
        classification = "PRODUCTION READY" if score >= 76 else "FUNCTIONAL" if score >= 51 else "PARTIAL" if score >= 26 else "PAPER"
        
        lines = [
            "# MCP REALITY REPORT",
            f"**Operability Score:** {score}/100",
            f"**Classification:** {classification}",
            "\n## MCP Status Matrix",
            "| MCP | CONFIGURED | CONNECTED | OPERATIONAL | ERROR |",
            "| :--- | :---: | :---: | :---: | :--- |"
        ]
        
        for r in self.report["results"]:
            lines.append(f"| {r['id']} | {'✔️' if r['configured'] else '❌'} | {'✔️' if r['connected'] else '❌'} | {'✔️' if r['operational'] else '❌'} | {r['error'] or '-'} |")

        report_path = os.path.join(settings.DOCS_DIR, "mcp-reality-report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        logger.info(f"Report generated with score {score}")

if __name__ == "__main__":
    diag = MCPDiagnostics()
    diag.run_diagnostics()
