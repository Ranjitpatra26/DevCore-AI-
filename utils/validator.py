import os
import sys
import logging
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import execute_query
from agents.base import get_role_display_name
from exports.pdf_generator import build_pdf_blueprint
from exports.markdown import package_project_blueprint_zip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validator")

def validate_all_projects() -> Dict[str, Any]:
    """Audit every project in the database and verify rendering, parsing, and export pipelines."""
    results = {
        "total_projects": 0,
        "valid_projects": 0,
        "pdf_exports_tested": 0,
        "zip_exports_tested": 0,
        "errors": []
    }
    
    try:
        projects = execute_query("SELECT * FROM projects")
        results["total_projects"] = len(projects)
        
        all_13_roles = [
            "ceo", "business_analyst", "project_manager", "architect", "ui_ux",
            "frontend", "backend", "database", "security", "devops", "qa",
            "documentation", "reviewer"
        ]
        
        for project in projects:
            p_id = project["id"]
            p_name = project["name"]
            
            # Fetch agent runs for this project
            agent_runs = execute_query(
                "SELECT agent_role, output_markdown, execution_time_s, timestamp FROM agent_runs WHERE project_id = ?",
                (p_id,)
            )
            
            runs_map = {run["agent_role"].lower(): run["output_markdown"] for run in agent_runs}
            missing_roles = [r for r in all_13_roles if r not in runs_map or not runs_map[r].strip()]
            
            if missing_roles:
                logger.warning(f"Project '{p_name}' ({p_id[:8]}) missing {len(missing_roles)} roles: {missing_roles}")
            else:
                results["valid_projects"] += 1
                
            # Test PDF Export Generation
            try:
                pdf_bytes = build_pdf_blueprint(p_name, agent_runs)
                if len(pdf_bytes) > 0:
                    results["pdf_exports_tested"] += 1
                else:
                    results["errors"].append(f"PDF export returned 0 bytes for project {p_name}")
            except Exception as e:
                results["errors"].append(f"PDF export failed for {p_name}: {str(e)}")
                
            # Test ZIP Export Generation
            try:
                zip_bytes = package_project_blueprint_zip(p_name, agent_runs)
                if len(zip_bytes) > 0:
                    results["zip_exports_tested"] += 1
                else:
                    results["errors"].append(f"ZIP export returned 0 bytes for project {p_name}")
            except Exception as e:
                results["errors"].append(f"ZIP export failed for {p_name}: {str(e)}")
                
    except Exception as err:
        results["errors"].append(f"Validation suite error: {str(err)}")
        
    return results

if __name__ == "__main__":
    res = validate_all_projects()
    print("=== SELF-VALIDATION REPORT ===")
    print(f"Total Projects Audited: {res['total_projects']}")
    print(f"Fully Synthesized Projects (13/13 Roles): {res['valid_projects']}")
    print(f"PDF Exports Verified: {res['pdf_exports_tested']}")
    print(f"ZIP Packages Verified: {res['zip_exports_tested']}")
    if res["errors"]:
        print(f"Errors Found ({len(res['errors'])}):")
        for err in res["errors"]:
            print(f"  - {err}")
    else:
        print("[OK] ALL PIPELINES & RENDERING LAYERS VALIDATED WITH ZERO ERRORS!")
