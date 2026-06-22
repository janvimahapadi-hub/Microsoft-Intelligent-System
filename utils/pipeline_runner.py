import subprocess
import sys

from utils.config import PROJECT_ROOT


PIPELINE_MODULES = {
    "Collector Manager": {
        "module": "collectors.manager",
        "path": "collectors/manager.py"
    },
    "Cleaner": {
        "module": "preprocessing.cleaner",
        "path": "preprocessing/cleaner.py"
    },
    "Deduplication": {
    "module": "preprocessing.duplication",
    "path": "preprocessing/duplication.py"
   },
    "Chunker": {
        "module": "preprocessing.chunker",
        "path": "preprocessing/chunker.py"
    },
    "Embedder": {
        "module": "embeddings.embedder",
        "path": "embeddings/embedder.py"
    },
    "FAISS Builder": {
        "module": "vectorstore.faiss_store",
        "path": "vectorstore/faiss_store.py"
    },
    "Audit": {
        "module": "utils.audit_project",
        "path": "utils/audit_project.py"
    }
}


def script_exists(relative_path):
    script_path = PROJECT_ROOT / relative_path
    return script_path.exists()


def get_pipeline_script_status():
    status = []

    for name, item in PIPELINE_MODULES.items():
        status.append({
            "Step": name,
            "Module": item["module"],
            "Path": item["path"],
            "Exists": script_exists(item["path"])
        })

    return status


def run_python_module(module_name, timeout=600):
    """
    Runs a project module using python -m.
    This keeps project-root imports working, for example:
    from collectors.extra_sources_collector import ...
    """

    try:
        completed = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "step": module_name,
            "success": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "return_code": completed.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "step": module_name,
            "success": False,
            "stdout": "",
            "stderr": f"Timeout: {module_name} took longer than {timeout} seconds.",
            "return_code": None
        }

    except Exception as error:
        return {
            "step": module_name,
            "success": False,
            "stdout": "",
            "stderr": str(error),
            "return_code": None
        }


def run_audit():
    return run_python_module(
        PIPELINE_MODULES["Audit"]["module"],
        timeout=120
    )


def build_refresh_plan(
    run_collection=False,
    run_cleaning=True,
    run_chunking=True,
    rebuild_embeddings=False,
    rebuild_faiss=False,
    run_audit_after=True
):
    plan = []

    if run_collection:
        plan.append(("Collector Manager", PIPELINE_MODULES["Collector Manager"]["module"]))

    if run_cleaning:
        plan.append(("Cleaner", PIPELINE_MODULES["Cleaner"]["module"]))
        plan.append(("Deduplication", PIPELINE_MODULES["Deduplication"]["module"]))

    if run_chunking:
        plan.append(("Chunker", PIPELINE_MODULES["Chunker"]["module"]))

    if rebuild_embeddings:
        plan.append(("Embedder", PIPELINE_MODULES["Embedder"]["module"]))

    if rebuild_faiss:
        plan.append(("FAISS Builder", PIPELINE_MODULES["FAISS Builder"]["module"]))

    if run_audit_after:
        plan.append(("Audit", PIPELINE_MODULES["Audit"]["module"]))

    return plan


def run_refresh_pipeline(
    run_collection=False,
    run_cleaning=True,
    run_chunking=True,
    rebuild_embeddings=False,
    rebuild_faiss=False,
    run_audit_after=True
):
    plan = build_refresh_plan(
        run_collection=run_collection,
        run_cleaning=run_cleaning,
        run_chunking=run_chunking,
        rebuild_embeddings=rebuild_embeddings,
        rebuild_faiss=rebuild_faiss,
        run_audit_after=run_audit_after
    )

    results = []

    for step_name, module_name in plan:
        result = run_python_module(
            module_name,
            timeout=900
        )

        result["step_name"] = step_name
        results.append(result)

        if not result["success"]:
            break

    return results


def get_manual_refresh_commands():
    return [
        "python -m collectors.manager",
        "python -m preprocessing.cleaner",
        "python -m preprocessing.duplication",
        "python -m preprocessing.chunker",
        "python -m embeddings.embedder",
        "python -m vectorstore.faiss_store",
        "python -m utils.audit_project"
    ]


if __name__ == "__main__":
    print("Pipeline script status:")

    for item in get_pipeline_script_status():
        print(item)

    print("\nRunning audit:")
    audit_result = run_audit()
    print(audit_result["stdout"])
    print(audit_result["stderr"])