"""
Project Intelligence Parser (PIP) Services.
F036: PIP Input Ingestion & Normalisation
F037: NLP Feature Extraction (NER)
F038: Dependency DAG Construction
F039: Budget Allocation Engine (Constrained Optimisation)
F040: Sprint Planner & Gantt Generator
"""

import logging
from typing import Dict, Any, List
import networkx as nx
from scipy.optimize import linprog

logger = logging.getLogger(__name__)


class ProjectIntelligenceParser:
    """
    Project Intelligence Parser (PIP)
    Handles the 7-step intake pipeline for new projects.
    """

    async def process_project_intake(self, raw_data: str, total_budget: float = 0.0) -> Dict[str, Any]:
        """Orchestrates the entire PIP pipeline."""
        logger.info("Starting PIP Pipeline...")
        
        # F036 & F037
        nlp_data = await self.step1_nlp_extraction(raw_data)
        
        # F038
        dag_structure = await self.step2_generate_dag(nlp_data)
        
        roles = await self.step3_role_identification(dag_structure)
        
        # F039
        budget_alloc = await self.step4_budget_allocation(roles, total_budget, dag_structure)
        
        team = await self.step5_team_matching(roles)
        
        # F040
        timeline = await self.step6_timeline_estimation(dag_structure, team)
        
        approval = await self.step7_risk_and_approval(budget_alloc, timeline)

        return {
            "nlp_data": nlp_data,
            "dag": dag_structure,
            "allocated_budget": budget_alloc,
            "team_matched": team,
            "timeline": timeline,
            "status": approval,
        }

    async def step1_nlp_extraction(self, text: str) -> Dict[str, Any]:
        """F036 & F037: NLP Feature Extraction (NER) and normalisation."""
        # Simulated SpaCy NER extraction
        features = []
        if "login" in text.lower() or "auth" in text.lower():
            features.append({"name": "Authentication", "domain": "Backend", "complexity": 0.5, "type": "Core"})
        if "dashboard" in text.lower() or "ui" in text.lower():
            features.append({"name": "Dashboard UI", "domain": "Frontend", "complexity": 0.7, "type": "Feature"})
        if "ml" in text.lower() or "model" in text.lower() or "ai" in text.lower():
            features.append({"name": "ML Engine", "domain": "AI", "complexity": 0.9, "type": "Core"})
        
        if not features:
            features = [{"name": "Generic Feature", "domain": "Full-stack", "complexity": 0.5, "type": "Feature"}]
            
        return {"project_name": "Parsed Project", "scope": text, "features": features}

    async def step2_generate_dag(self, nlp_data: Dict[str, Any]) -> Dict[str, Any]:
        """F038: Dependency DAG Construction using NetworkX."""
        G = nx.DiGraph()
        features = nlp_data.get("features", [])
        
        for feature in features:
            G.add_node(feature["name"], **feature)
            
        # Simulated dependencies
        feature_names = [f["name"] for f in features]
        if "Authentication" in feature_names and "Dashboard UI" in feature_names:
            G.add_edge("Authentication", "Dashboard UI")
        if "ML Engine" in feature_names and "Dashboard UI" in feature_names:
            G.add_edge("ML Engine", "Dashboard UI")
            
        try:
            # Topological sort for sprint ordering
            execution_order = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            execution_order = []
            logger.error("Circular dependency detected in DAG!")
            
        return {
            "nodes": list(G.nodes(data=True)),
            "edges": list(G.edges()),
            "execution_order": execution_order,
            "is_dag": nx.is_directed_acyclic_graph(G)
        }

    async def step3_role_identification(self, dag: Dict[str, Any]) -> List[str]:
        roles = set()
        for node, data in dag.get("nodes", []):
            domain = data.get("domain", "Backend")
            if domain == "Backend":
                roles.add("Backend Engineer")
            elif domain == "Frontend":
                roles.add("Frontend Engineer")
            elif domain == "AI":
                roles.add("Data Scientist")
            else:
                roles.add("Full-stack Engineer")
        return list(roles)

    async def step4_budget_allocation(self, roles: List[str], total_budget: float, dag: Dict[str, Any]) -> Dict[str, Any]:
        """F039: Budget Allocation Engine (Constrained Optimisation)"""
        if total_budget <= 0:
            total_budget = 100000.0  # Default budget if none provided

        # Simplified Linear Programming formulation
        # Objective: Maximize feature value (simulated by complexity)
        # Constraints: Total cost <= Total budget, category reserves
        
        nodes = dag.get("nodes", [])
        num_features = len(nodes)
        
        if num_features == 0:
             return {"total": total_budget, "breakdown": {}}
             
        # Mock feature costs based on complexity
        feature_costs = [data.get("complexity", 0.5) * 10000 for _, data in nodes]
        
        # We want to minimize -1 * (feature value), we assume value is proportional to cost for simplicity
        c = [-cost for cost in feature_costs]
        
        # Constraint: sum(costs) <= total_budget
        A_ub = [feature_costs]
        b_ub = [total_budget]
        
        # Bounds: 0 to 1 (whether to include the feature or partially fund)
        bounds = [(0, 1) for _ in range(num_features)]
        
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        allocated = {}
        if res.success:
            for i, (node_name, _) in enumerate(nodes):
                allocated[node_name] = res.x[i] * feature_costs[i]
        else:
            # Fallback
            for i, (node_name, _) in enumerate(nodes):
                allocated[node_name] = feature_costs[i]
                
        return {
            "total_budget": total_budget,
            "allocated": sum(allocated.values()),
            "breakdown": allocated,
            "optimization_success": res.success
        }

    async def step5_team_matching(self, roles: List[str]) -> List[Dict[str, Any]]:
        # Simulated team matching
        return [{"role": r, "employee_id": hash(r) % 1000} for r in roles]

    async def step6_timeline_estimation(self, dag: Dict[str, Any], team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """F040: Sprint Planner & Gantt Generator"""
        execution_order = dag.get("execution_order", [])
        
        sprints = []
        current_sprint = []
        current_complexity = 0
        sprint_capacity = 1.5  # Max complexity per sprint
        
        for task in execution_order:
            # Find task complexity
            complexity = 0.5
            for n, data in dag.get("nodes", []):
                if n == task:
                    complexity = data.get("complexity", 0.5)
                    break
                    
            if current_complexity + complexity > sprint_capacity and current_sprint:
                sprints.append(current_sprint)
                current_sprint = [task]
                current_complexity = complexity
            else:
                current_sprint.append(task)
                current_complexity += complexity
                
        if current_sprint:
            sprints.append(current_sprint)
            
        gantt = []
        start_week = 0
        for i, sprint in enumerate(sprints):
            for task in sprint:
                gantt.append({
                    "task": task,
                    "start_week": start_week,
                    "end_week": start_week + 2,
                    "sprint": i + 1
                })
            start_week += 2
            
        return {
            "sprints": [{"sprint_id": i+1, "tasks": s} for i, s in enumerate(sprints)],
            "gantt_chart": gantt,
            "estimated_weeks": len(sprints) * 2
        }

    async def step7_risk_and_approval(self, budget: Dict[str, Any], timeline: Dict[str, Any]) -> str:
        if not budget.get("optimization_success", False):
            return "REQUIRES_REVIEW"
        if timeline.get("estimated_weeks", 0) > 24:
            return "HIGH_RISK_APPROVAL_NEEDED"
        return "APPROVED"


pip_service = ProjectIntelligenceParser()
